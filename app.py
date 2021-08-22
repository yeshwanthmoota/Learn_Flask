from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta



app = Flask(__name__)
app.secret_key = "hello_world"
# app.secret_key = "6b8aff760b701265494ae0d98a5058fa" # a more secure key should be something like this
# The above key is generated using secrets module, see the program below
# import secrets
# secrets.token_hex(16) # it generates a random 16 bit string everytime.
app.permanent_session_lifetime = timedelta(minutes = 1)






@app.route("/") # Creating routes for the webpages
@app.route("/home") # Creating routes for the webpages
def home(): # defining pages on the website
    return render_template("home.html")



@app.route("/login", methods=["POST", "GET"]) # Creating routes for the webpages
def login():
    if request.method == "POST":
        session.permanent = True
        if request.form["nm"] == "":
            flash("Name field not filled", category = "danger")
            return redirect(url_for("login"))
        else:
            usr_name = request.form["nm"]
            session["user's name"] = usr_name
            flash("Logged In Successfully!", category = "success")
            return redirect(url_for("user"))
    else:
        if "user's name" in session:
            flash("User already Logged In", category = "warning")
            return redirect(url_for("user"))
        else:
            return render_template("login.html")



@app.route("/user") # Creating routes for the webpages
def user():
    if "user's name" in session:
        usr = session["user's name"]
        return render_template("user_data.html", user_name = usr)
    else:
        return redirect(url_for("login"))




@app.route("/logout") # Creating routes for the webpages
def logout():
    if "user's name" in session:
        session.pop("user's name", None)
        flash("You have been logged Out!", category="success")
        return redirect(url_for("login"))
    else:
        flash("No User Logged In", category = "info")
        return redirect(url_for("home"))




if __name__ == '__main__':
    app.run(debug = True) # "debug = True" helps make simultaneous changes in the website without restarting the server.