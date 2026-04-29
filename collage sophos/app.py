from flask import Flask,redirect,render_template,url_for,session,flash,request
from datetime import datetime,timedelta
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.secret_key="vivekkali"
app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///Sophosdb.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db=SQLAlchemy(app)

class Sophosdb(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(30),nullable=False)
    password=db.Column(db.String(30),nullable=False)

with app.app_context():
    db.create_all()
    print("database is created succuessfully !")

@app.route("/",methods=["GET","POST"])
def sophos():
    session.permanent=True
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")

        if not username or username.strip()=="":
            return "enter a valid username"

        if not password or password.strip()=="":
            return "enter a valid password"
        
        session["username"]=username
        session["password"]=password

        new_user=Sophosdb(
            username=username,
            password=password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            print("user added !")
        except Exception as e :
            db.session.rollback()
            print(e)

        return f"signed in successful thank you {username}"
    else:
        return render_template("sophos_index.html")
    




    



    
