/*
  ESP32 + 2x MPU6500 + HC-SR04 + Buzzer -> Flask backend over Wi-Fi
  ------------------------------------------------------------------
  Builds on the two-I2C-bus MPU6500 setup (each sensor on its own bus,
  both at address 0x68, no AD0 wiring needed). Adds:

    1. HC-SR04 ultrasonic distance sensor -> used to estimate
       displacement (mm) from a baseline measured at boot.
    2. Active buzzer -> sounds a local alarm if vibration RMS or
       displacement crosses a configurable threshold.

  WIRING (new additions):
    HC-SR04:
      VCC  -> 5V / VIN
      GND  -> GND
      TRIG -> GPIO 5
      ECHO -> GPIO 18  (THROUGH A VOLTAGE DIVIDER - ECHO is 5V output,
                        ESP32 GPIOs are NOT 5V tolerant. Use e.g. a
                        1k/2k divider so ECHO sees ~3.3V at GPIO18.)

    Buzzer (active buzzer, 2-pin):
      +   -> GPIO 19
      -   -> GND

  MPU6500 wiring is unchanged from before:
    Sensor 1 (Wire,  bus 0): SDA->21, SCL->22, AD0->GND, addr 0x68
    Sensor 2 (Wire1, bus 1): SDA->25, SCL->26, AD0->GND, addr 0x68

  LIBRARIES NEEDED:
    - "ArduinoJson" by Benoit Blanchon (v6.x)

  NOTES ON THE NEW SENSORS:
    - HC-SR04 baseline: on boot, the code takes several distance
      readings and averages them as the "zero" position. displacement_mm
      is then (baseline - current distance), so an object moving CLOSER
      to the sensor reads as a POSITIVE displacement. Flip the sign in
      readDistanceCM()'s caller if you want the opposite convention.
    - If HC-SR04 read fails (timeout / out of range), the last known
      distance is reused rather than sending garbage.
    - Buzzer alarm thresholds (ALARM_VIBRATION_RMS_G and
      ALARM_DISPLACEMENT_MM below) are guesses - tune them to your
      actual structure/setup. The buzzer works independently of Wi-Fi,
      so it will still alert even if the server is unreachable.
*/

#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ---------- CONFIG ----------
const char* WIFI_SSID     = "Airtel_Airtel vivek";
const char* WIFI_PASSWORD = "Vivekkali@12345";
const char* SERVER_URL    = "http://192.168.1.7:5000/api/sensor-data"; // <-- change to your laptop IP

const unsigned long SEND_INTERVAL_MS   = 2000;
const unsigned long WIFI_TIMEOUT_MS    = 15000;
const unsigned long WIFI_RETRY_MS      = 5000;
const unsigned long DETECT_RETRY_MS    = 10000;

const int WINDOW_SIZE = 20;
const uint8_t MPU_ADDR = 0x68; // both sensors use this now - different buses

// ---------- HC-SR04 config ----------
const int TRIG_PIN = 5;
const int ECHO_PIN = 18;
const int HCSR04_TIMEOUT_US = 30000;      // ~5m max range cutoff
const int BASELINE_SAMPLES  = 20;         // readings averaged at boot for "zero"

// ---------- Buzzer config ----------
const int BUZZER_PIN = 19;
const float ALARM_VIBRATION_RMS_G = 0.35f;  // tune to your setup
const float ALARM_DISPLACEMENT_MM = 15.0f;  // tune to your setup
const float ALARM_PROXIMITY_CM    = 10.0f;  // buzzer sounds if object is closer than this
const unsigned long ALARM_BEEP_INTERVAL_MS = 500; // beep on/off period while alarm active

// ---------- Per-sensor state ----------
struct MpuNode {
  TwoWire* bus;
  const char* busName;
  const char* nodeId;
  bool present;
  unsigned long lastDetectAttempt;
  float accelMagBuffer[WINDOW_SIZE];
  int bufferIndex;
  bool bufferFilled;
  float lastVibrationRMS;
};

MpuNode nodes[2] = {
  { &Wire,  "bus0", "NODE-01", false, 0, {0}, 0, false, 0.0f },
  { &Wire1, "bus1", "NODE-02", false, 0, {0}, 0, false, 0.0f }
};

unsigned long lastSendTime = 0;
unsigned long lastWifiRetry = 0;

// HC-SR04 state
float baselineDistanceCM = 0.0f;
float lastDistanceCM = 0.0f;
bool baselineSet = false;

// Buzzer state
bool alarmActive = false;
bool buzzerOn = false;
unsigned long lastBuzzerToggle = 0;

// ---------- I2C helpers ----------
bool i2cDevicePresent(TwoWire &bus, uint8_t addr) {
  bus.beginTransmission(addr);
  return bus.endTransmission() == 0;
}

uint8_t readWhoAmI(TwoWire &bus, uint8_t addr) {
  bus.beginTransmission(addr);
  bus.write(0x75); // WHO_AM_I register
  if (bus.endTransmission(false) != 0) return 0xFF;
  bus.requestFrom((int)addr, 1, true);
  if (bus.available() < 1) return 0xFF;
  return bus.read();
}

void mpuWrite(TwoWire &bus, uint8_t addr, uint8_t reg, uint8_t val) {
  bus.beginTransmission(addr);
  bus.write(reg);
  bus.write(val);
  bus.endTransmission();
}

void mpuInit(TwoWire &bus, uint8_t addr) {
  mpuWrite(bus, addr, 0x6B, 0x00); // PWR_MGMT_1: wake up
  delay(100);
  mpuWrite(bus, addr, 0x1C, 0x00); // ACCEL_CONFIG: +/-2g
  mpuWrite(bus, addr, 0x1B, 0x00); // GYRO_CONFIG: +/-250 dps
}

bool readMPU(TwoWire &bus, uint8_t addr, float &ax, float &ay, float &az, float &gx, float &gy, float &gz) {
  bus.beginTransmission(addr);
  bus.write(0x3B); // ACCEL_XOUT_H
  if (bus.endTransmission(false) != 0) return false;

  bus.requestFrom((int)addr, 14, true);
  if (bus.available() < 14) return false;

  int16_t rawAx = (bus.read() << 8) | bus.read();
  int16_t rawAy = (bus.read() << 8) | bus.read();
  int16_t rawAz = (bus.read() << 8) | bus.read();
  bus.read(); bus.read(); // skip temperature
  int16_t rawGx = (bus.read() << 8) | bus.read();
  int16_t rawGy = (bus.read() << 8) | bus.read();
  int16_t rawGz = (bus.read() << 8) | bus.read();

  ax = rawAx / 16384.0;
  ay = rawAy / 16384.0;
  az = rawAz / 16384.0;
  gx = rawGx / 131.0;
  gy = rawGy / 131.0;
  gz = rawGz / 131.0;
  return true;
}

void detectAndInitNode(MpuNode &node) {
  node.present = i2cDevicePresent(*node.bus, MPU_ADDR);
  Serial.print(node.nodeId);
  Serial.print(" (");
  Serial.print(node.busName);
  Serial.print(", 0x");
  Serial.print(MPU_ADDR, HEX);
  Serial.print("): ");
  if (node.present) {
    uint8_t whoAmI = readWhoAmI(*node.bus, MPU_ADDR);
    Serial.print("present, WHO_AM_I=0x");
    Serial.println(whoAmI, HEX);
    mpuInit(*node.bus, MPU_ADDR);
  } else {
    Serial.println("NOT FOUND - check VCC/GND/SDA/SCL wiring for this sensor");
  }
}

// ---------- HC-SR04 ----------
// Returns distance in cm, or -1.0 on timeout/failed read.
float readDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long duration = pulseIn(ECHO_PIN, HIGH, HCSR04_TIMEOUT_US);
  if (duration == 0) return -1.0f; // timeout / no echo

  // speed of sound ~0.0343 cm/us, round trip -> divide by 2
  float distanceCM = (duration * 0.0343f) / 2.0f;
  return distanceCM;
}

void establishBaselineDistance() {
  Serial.println("Measuring HC-SR04 baseline distance...");
  float sum = 0;
  int validReadings = 0;
  for (int i = 0; i < BASELINE_SAMPLES; i++) {
    float d = readDistanceCM();
    if (d > 0) {
      sum += d;
      validReadings++;
    }
    delay(60);
  }
  if (validReadings > 0) {
    baselineDistanceCM = sum / validReadings;
    lastDistanceCM = baselineDistanceCM;
    baselineSet = true;
    Serial.print("Baseline distance: ");
    Serial.print(baselineDistanceCM);
    Serial.println(" cm");
  } else {
    Serial.println("Could not establish HC-SR04 baseline (no valid readings) - check wiring.");
    baselineSet = false;
  }
}

// ---------- Buzzer ----------
void updateBuzzer(unsigned long now) {
  if (alarmActive) {
    if (now - lastBuzzerToggle >= ALARM_BEEP_INTERVAL_MS) {
      lastBuzzerToggle = now;
      buzzerOn = !buzzerOn;
      digitalWrite(BUZZER_PIN, buzzerOn ? HIGH : LOW);
    }
  } else if (buzzerOn) {
    buzzerOn = false;
    digitalWrite(BUZZER_PIN, LOW);
  }
}

// ---------- Wi-Fi ----------
void connectWifi() {
  Serial.println("Connecting to WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < WIFI_TIMEOUT_MS) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi connected. IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi not connected yet, will keep retrying in background.");
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.begin(21, 22);   // bus 0: sensor 1
  Wire1.begin(25, 26);  // bus 1: sensor 2

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  detectAndInitNode(nodes[0]);
  detectAndInitNode(nodes[1]);
  establishBaselineDistance();

  connectWifi();
}

void sendNode(MpuNode &node) {
  float ax, ay, az, gx, gy, gz;
  if (!readMPU(*node.bus, MPU_ADDR, ax, ay, az, gx, gy, gz)) {
    Serial.print(node.nodeId);
    Serial.println(": read failed (was present at boot, lost mid-run?)");
    node.present = false;
    return;
  }

  float tiltX = atan2(ay, sqrt(ax * ax + az * az)) * 180.0 / PI;
  float tiltY = atan2(-ax, sqrt(ay * ay + az * az)) * 180.0 / PI;

  float mag = sqrt(ax * ax + ay * ay + az * az) - 1.0;
  node.accelMagBuffer[node.bufferIndex] = mag;
  node.bufferIndex = (node.bufferIndex + 1) % WINDOW_SIZE;
  if (node.bufferIndex == 0) node.bufferFilled = true;

  int count = node.bufferFilled ? WINDOW_SIZE : node.bufferIndex;
  float sumSq = 0;
  for (int i = 0; i < count; i++) sumSq += node.accelMagBuffer[i] * node.accelMagBuffer[i];
  float vibrationRMS = count > 0 ? sqrt(sumSq / count) : 0;
  node.lastVibrationRMS = vibrationRMS;

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<512> doc;
  doc["node_id"] = node.nodeId;
  doc["accel_x_g"] = ax;
  doc["accel_y_g"] = ay;
  doc["accel_z_g"] = az;
  doc["gyro_x_dps"] = gx;
  doc["gyro_y_dps"] = gy;
  doc["gyro_z_dps"] = gz;
  doc["tilt_x_deg"] = tiltX;
  doc["tilt_y_deg"] = tiltY;
  doc["vibration_rms_g"] = vibrationRMS;
  doc["crack_width_mm"] = 0.0;

  String payload;
  serializeJson(doc, payload);

  int httpCode = http.POST(payload);
  Serial.print("Sent -> ");
  Serial.print(payload);
  Serial.print("  [HTTP ");
  Serial.print(httpCode);
  Serial.println("]");

  http.end();
}

// Ultrasonic reading sent as its OWN payload, completely separate from
// the MPU node payloads above - not mixed into node_id/accel/gyro data.
void sendUltrasonicData(float distanceCM, float displacementMM, bool proximityAlarm) {
  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<256> doc;
  doc["sensor_id"] = "spidey";
  doc["distance_cm"] = distanceCM;
  doc["displacement_mm"] = displacementMM;
  doc["proximity_alarm"] = proximityAlarm;

  String payload;
  serializeJson(doc, payload);

  int httpCode = http.POST(payload);
  Serial.print("Sent -> ");
  Serial.print(payload);
  Serial.print("  [HTTP ");
  Serial.print(httpCode);
  Serial.println("]");

  http.end();
}

void loop() {
  unsigned long now = millis();

  if (WiFi.status() != WL_CONNECTED && now - lastWifiRetry >= WIFI_RETRY_MS) {
    lastWifiRetry = now;
    Serial.println("WiFi disconnected, attempting reconnect...");
    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  }

  for (int i = 0; i < 2; i++) {
    if (!nodes[i].present && now - nodes[i].lastDetectAttempt >= DETECT_RETRY_MS) {
      nodes[i].lastDetectAttempt = now;
      detectAndInitNode(nodes[i]);
    }
  }

  // Read HC-SR04 every loop (cheap, non-blocking-ish - pulseIn has its own timeout)
  float distanceCM = readDistanceCM();
  if (distanceCM > 0) {
    lastDistanceCM = distanceCM;
  } // else keep lastDistanceCM (reuse last good reading)

  float displacementMM = 0.0f;
  if (baselineSet) {
    displacementMM = (baselineDistanceCM - lastDistanceCM) * 10.0f; // cm -> mm
  }

  // ---- Alarm check ----
  bool vibrationAlarm = (nodes[0].lastVibrationRMS > ALARM_VIBRATION_RMS_G) ||
                         (nodes[1].lastVibrationRMS > ALARM_VIBRATION_RMS_G);
  bool displacementAlarm = baselineSet && (fabs(displacementMM) > ALARM_DISPLACEMENT_MM);
  bool proximityAlarm = (lastDistanceCM > 0) && (lastDistanceCM < ALARM_PROXIMITY_CM);
  alarmActive = vibrationAlarm || displacementAlarm || proximityAlarm;
  updateBuzzer(now);

  if (now - lastSendTime >= SEND_INTERVAL_MS) {
    lastSendTime = now;

    Serial.print("Distance: ");
    Serial.print(lastDistanceCM);
    Serial.print(" cm | Displacement: ");
    Serial.print(displacementMM);
    Serial.print(" mm | Alarm: ");
    Serial.println(alarmActive ? "ACTIVE" : "off");

    if (WiFi.status() == WL_CONNECTED) {
      for (int i = 0; i < 2; i++) {
        if (nodes[i].present) sendNode(nodes[i]);
      }
      sendUltrasonicData(lastDistanceCM, displacementMM, proximityAlarm);
    } else {
      Serial.println("WiFi disconnected, skipping send.");
    }
  }
}
