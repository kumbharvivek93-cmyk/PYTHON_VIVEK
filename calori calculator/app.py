from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///helth.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Helth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    activity_level = db.Column(db.String(50), nullable=False)
    goal = db.Column(db.String(30), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    diet_plan = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


GOAL_ADJUSTMENTS = {
    "lose": -500,
    "maintain": 0,
    "gain": 400,
}


DIET_SUGGESTIONS = {
    "lose": [
        "Breakfast: oats with chia seeds, apple, and boiled eggs",
        "Lunch: grilled chicken or paneer with brown rice and salad",
        "Snack: Greek yogurt or roasted chana with cucumber",
        "Dinner: vegetable soup with tofu or fish and sauteed vegetables",
        "Tip: prioritize protein, fiber, and water while limiting sugary foods",
    ],
    "maintain": [
        "Breakfast: whole grain toast, peanut butter, fruit, and milk",
        "Lunch: dal or lean meat with roti, rice, and mixed vegetables",
        "Snack: nuts, fruit, or buttermilk",
        "Dinner: quinoa or chapati with paneer, chicken, or beans",
        "Tip: keep meals balanced with carbs, protein, healthy fats, and vegetables",
    ],
    "gain": [
        "Breakfast: peanut butter toast, banana smoothie, and omelette",
        "Lunch: rice, potatoes, chicken or paneer, and curd",
        "Snack: trail mix, dates, milkshake, or cheese sandwich",
        "Dinner: pasta or rice bowl with salmon, chicken, tofu, or beans",
        "Tip: add calorie-dense but nutritious foods like nuts, dairy, seeds, and smoothies",
    ],
}


def calculate_bmr(weight, height, age, gender):
    if gender == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    return 10 * weight + 6.25 * height - 5 * age - 161


def calculate_bmi(weight, height):
    height_in_meters = height / 100
    return weight / (height_in_meters ** 2)


def calorie_target(weight, height, age, gender, activity_level, goal):
    bmr = calculate_bmr(weight, height, age, gender)
    maintenance = bmr * ACTIVITY_MULTIPLIERS[activity_level]
    target = maintenance + GOAL_ADJUSTMENTS[goal]
    return max(int(target), 1200)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        name = request.form["name"].strip()
        age = int(request.form["age"])
        gender = request.form["gender"]
        height = float(request.form["height"])
        weight = float(request.form["weight"])
        activity_level = request.form["activity_level"]
        goal = request.form["goal"]

        calories = calorie_target(weight, height, age, gender, activity_level, goal)
        bmi = round(calculate_bmi(weight, height), 1)
        diet_plan = DIET_SUGGESTIONS[goal]

        entry = Helth(
            name=name,
            age=age,
            gender=gender,
            height=height,
            weight=weight,
            activity_level=activity_level,
            goal=goal,
            calories=calories,
            bmi=bmi,
            diet_plan="\n".join(diet_plan),
        )
        db.session.add(entry)
        db.session.commit()

        result = {
            "name": name,
            "calories": calories,
            "bmi": bmi,
            "goal": goal,
            "diet_plan": diet_plan,
        }

    return render_template("index.html", result=result)


@app.route("/history")
def history():
    records = Helth.query.order_by(Helth.created_at.desc()).all()
    return render_template("history.html", records=records)


with app.app_context():
    db.create_all()
    
    


