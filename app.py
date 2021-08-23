from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import logging



app = Flask(__name__)
app.secret_key = "hello_world"
# app.secret_key = "6b8aff760b701265494ae0d98a5058fa" # a more secure key should be something like this
# The above key is generated using secrets module, see the program below
# import secrets
# print(secrets.token_hex(16)) # it generates a random 16 bit string everytime.
app.permanent_session_lifetime = timedelta(minutes = 2)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, name, email):
        self.name = name
        self.email = email






@app.route("/") # Creating routes for the webpages
@app.route("/home") # Creating routes for the webpages
def home(): # defining pages on the website
    return render_template("home.html")




@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":

        if request.form["nm"] == "" or request.form["eml"] == "":
            flash("required fields not filled", category = "danger")
            return redirect(url_for("register"))
        else:
            usr_name = request.form["nm"]
            usr_email = request.form["eml"]
            found_user_by_name = Users.query.filter_by(name = usr_name).first() # only one entry should match
            found_user_by_email = Users.query.filter_by(email = usr_email).first() # only one entry should match
            if found_user_by_name or found_user_by_email:
                if found_user_by_name and found_user_by_email:
                    if found_user_by_name.id == found_user_by_email.id: # The user is already present in the system
                        flash("User already registered, Please Login", category = "info")
                        return redirect(url_for("login"))
                else:
                    # either of the name or email has been used already so flashing to prevent register
                    flash("Name or Email has already been used, please try a different Name or Email")
                    return redirect(url_for("register"))
            else:
                # registering a new user with a unique name and an unique email
                new_user = Users(usr_name, usr_email)
                db.session.add(new_user)
                db.session.commit()
                flash("You have been Successfully Registered!", category="success")
                return redirect(url_for("login"))        
    
    else: # "GET" request
        return render_template("register.html")




@app.route("/login", methods=["POST", "GET"]) # Creating routes for the webpages
def login():
    if request.method == "POST":
        session.permanent = True
        if request.form["nm"] == "" or request.form["eml"] == "":
            flash("required fields not filled", category = "danger")
            return redirect(url_for("login"))
        else:
            usr_name = request.form["nm"]
            usr_email = request.form["eml"]
            found_user = Users.query.filter_by(name = usr_name, email = usr_email).first()
            if found_user:
                session["user's name"] = usr_name
                session["user's email"] = usr_email
                flash("Logged In Successfully!", category = "success")
                return redirect(url_for("user"))
            else: # User not found
                flash("The Name or Email doesn't match, Please try again!", category="danger")
                return redirect(url_for("login"))
    else:
        if "user's name" in session:
            flash("User already Logged In", category = "warning")
            return redirect(url_for("user"))
        else:
            return render_template("login.html")




@app.route("/view_all_users")
def view_all_users():
    logging.basicConfig(filename='log_file_view_all_users.log', encoding='utf-8', level=logging.DEBUG)
    logging.info(Users.query.all())
    return render_template("view_all_users.html", all_users = Users.query.all())



@app.route("/user", methods = ["POST", "GET"]) # Creating routes for the webpages
def user():
    if request.method == "GET":
        if "user's name" in session:
            usr_name = session["user's name"]
            usr_email = session["user's email"]
            return render_template("user_data.html", user_name = usr_name, user_email = usr_email)
        else:
            return redirect(url_for("login"))
    elif request.method == "POST":
        if request.form["eml"] == "":
            flash("required fields not filled", category = "danger")
        else:
            if session["user's email"] == request.form["eml"]:
                flash("The same email has been entered", category="warning")
            else:
                found_email = Users.query.filter_by(email = request.form["eml"]).first()
                if found_email:
                    flash("The Entered email address already exists please try again!")
                else:
                    found_user = Users.query.filter_by(name=session["user's name"], email=session["user's email"]).first()
                    found_user.email = request.form["eml"]
                    db.session.commit()
                    session["user's email"] = request.form["eml"]
                    flash("user's email chaged Successfully!", category = "success")
            return redirect(url_for("user"))
        




@app.route("/logout") # Creating routes for the webpages
def logout():
    if "user's name" in session:
        session.pop("user's name", None)
        session.pop("user's email", None)
        flash("You have been Logged Out Successfully!", category="success")
        return redirect(url_for("login"))
    else:
        flash("No User Logged In", category = "info")
        return redirect(url_for("home"))

@app.route("/delete_account")
def delete_account():
    Users.query.filter_by(name = session["user's name"], email = session["user's email"]).delete()
    db.session.commit()
    session.pop("user's name", None)
    session.pop("user's email", None)
    flash("Account deleted successfully!", category = "success")
    return redirect(url_for("login"))


if __name__ == '__main__':
    db.create_all()
    app.run(debug = True) # "debug = True" helps make simultaneous changes in the website without restarting the server.