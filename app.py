from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import logging



app = Flask(__name__)
app.secret_key = "6b8aff760b701265494ae0d98a5058fa"
# The above key is generated using secrets module, see the program below
# import secrets
# print(secrets.token_hex(16)) # it generates a random 16 bit string everytime.
app.permanent_session_lifetime = timedelta(minutes = 5)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password





@app.route("/") # Creating routes for the webpages
@app.route("/home") # Creating routes for the webpages
def home(): # defining pages on the website
    return render_template("home.html")




@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":

        if request.form["nm"] == "" or request.form["eml"] == "" or request.form["passw"] == "":
            flash("required fields are not filled", category = "danger")
            return redirect(url_for("register"))
        else:
            usr_name = request.form["nm"]
            usr_email = request.form["eml"]
            usr_password = request.form["passw"]
            usr_confirm_password = request.form["passw_confr"]
            if usr_password == usr_confirm_password:
                found_user = Users.query.filter_by(email=usr_email).first()
                if found_user:
                    flash("User with this email address already exists, Please Log in!", category="info")
                    return redirect(url_for("login"))
                else:
                    # registering a new user
                    new_user = Users(usr_name, usr_email, usr_password)
                    db.session.add(new_user)
                    db.session.commit()
                    flash("You have been Successfully Registered!", category="success")
                    return redirect(url_for("login"))
            else:
                flash("Both the passwords don't match, Please try again", category = "danger")
                return render_template("register.html", usr_name = usr_name, usr_email = usr_email)
    
    else: # "GET" request
        return render_template("register.html")




@app.route("/login", methods=["POST", "GET"]) # Creating routes for the webpages
def login():
    if request.method == "POST":
        session.permanent = True
        if request.form["eml"] == "" or request.form["passw"] == "":
            flash("required fields are not filled", category = "danger")
            return redirect(url_for("login"))
        else:
            usr_email = request.form["eml"]
            usr_password = request.form["passw"]
            found_user = Users.query.filter_by(email = usr_email, password = usr_password).first()
            if found_user:
                session["user's name"] = found_user.name
                session["user's email"] = usr_email
                flash("Logged In Successfully!", category = "success")
                return redirect(url_for("user"))
            else: # User not found
                found_user_2 = Users.query.filter_by(email= usr_email).first()
                if found_user_2:
                    flash("Entered The Wrong Password!, Please try again", category = "danger")
                    return render_template("login.html", usr_email = usr_email)
                else:
                    flash("User with this email has not yet registered, Register Now!", category="warning")
                    return redirect(url_for("register"))
    else:
        if "user's email" in session:
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
        if "user's email" in session:
            usr_name = session["user's name"]
            usr_email = session["user's email"]
            return render_template("user_data.html", usr_name = usr_name, usr_email = usr_email)
        else:
            return redirect(url_for("login"))
    elif request.method == "POST":
        if "user's name" in session: # check if session is still running
            if request.form["passw"] == "" or request.form["new_passw"] == "" or request.form["confr_passw"] == "": # check if any of the boxes are empty
                flash("required fields are not filled", category = "danger")
                return redirect(url_for("change_password"))
            else:
                found_user = Users.query.filter_by(email = session["user's email"]).first()
                if request.form["passw"] == found_user.password: # check if the user entered the correct current password
                    if request.form["new_passw"] != request.form["confr_passw"]: # check if both the new passwords don't match
                        flash("The New Passwords don't match, Please try again", category="danger")
                        return redirect(url_for("change_password"))
                    else: # sucessful change
                        found_user.password = request.form["new_passw"]
                        db.session.commit()
                        flash("Password changed successfully", category="success")
                        return redirect(url_for("user"))
                else:
                    flash("Entered The Wrong Password, Please Try again", category="danger")
                    return redirect(url_for("change_password"))
        else:
            flash("You got Logged out, Please Log in again", category="warning")
            return redirect(url_for("login"))
        




@app.route("/logout") # Creating routes for the webpages
def logout():
    if "user's email" in session:
        session.pop("user's name", None)
        session.pop("user's email", None)
        session.pop("user's password", None)
        flash("You have been Logged Out Successfully!", category="success")
        return redirect(url_for("login"))
    else:
        flash("No User Logged In", category = "info")
        return redirect(url_for("home"))

@app.route("/delete_account")
def delete_account():
    Users.query.filter_by(email = session["user's email"]).delete()
    db.session.commit()
    session.pop("user's name", None)
    session.pop("user's email", None)
    session.pop("user's password", None)
    flash("Account deleted successfully!", category = "success")
    return redirect(url_for("login"))


@app.route("/change_password", methods=["GET"])
def change_password():
    return render_template("change_password.html")


if __name__ == '__main__':
    db.create_all()
    app.run(debug = True) # "debug = True" helps make simultaneous changes in the website without restarting the server.