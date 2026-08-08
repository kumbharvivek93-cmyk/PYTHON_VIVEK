from flask import Flask, render_template, redirect, session, flash, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, datetime
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loginlogout.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.permanent_session_lifetime = timedelta(days=2)
app.secret_key = 'vivekkali'

db = SQLAlchemy(app)


# ================= IMAGE UPLOAD =================

UPLOAD_FOLDER = os.path.join(app.instance_path, 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================= DATABASE =================

class Students(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.String(30), nullable=False)

    Dob = db.Column(db.String(30), nullable=False)

    name = db.Column(db.String(50), nullable=False)

    branch = db.Column(db.String(13), nullable=False)

    email = db.Column(db.String(50), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    image_path = db.Column(db.String(300))


# ================= CREATE DATABASE =================

with app.app_context():
    db.create_all()


# ================= ROUTE =================

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == 'POST':

        student_id = request.form.get('student_id')
        Dob = request.form.get('Dob')
        name = request.form.get('name')
        branch = request.form.get('branch')
        email = request.form.get('email')

        # Get image
        image = request.files.get('image')

        # Initially no image
        image_path = None

        if image and image.filename != '':

            # Make filename safe
            filename = secure_filename(image.filename)

            # Save actual image inside instance/uploads
            image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            # Store path in database
            image_path = os.path.join(
                'uploads',
                filename
            )

        # Create student object
        new_student = Students(
            name=name,
            email=email,
            student_id=student_id,
            branch=branch,
            Dob=Dob,
            image_path=image_path
        )

        try:

            db.session.add(new_student)
            db.session.commit()

            print('user added to the database')

            return 'You are added to the Database <h4>Thank you for support</h4>'

        except Exception as e:

            db.session.rollback()

            print('something went wrong')
            print(e)

            return f'Something went wrong: {e}'

    return render_template('index.html')


# ================= RUN =================

if __name__ == '__main__':
    app.run(debug=True)