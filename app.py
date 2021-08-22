from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home(): # defining pages on the website
    return render_template("home.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        usr_name = request.form["nm"]
        return redirect(url_for("user", usr = usr_name))
    else:
        return render_template("login.html")

@app.route("/<usr>")
def user(usr):
    return "<h2>Hi! {}, you are logged in!</h2>".format(usr)

if __name__ == '__main__':
    app.run(debug = True) # "debug = True" helps make simultaneous changes in the website without restarting the server.