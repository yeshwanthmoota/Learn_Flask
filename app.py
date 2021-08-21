from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home(): # defining pages on the website
    return render_template("home.html", var = ["Hi", "Their", "Yeshwanth"], greet = "Welcome!")

@app.route("/<name>")
def user(name):
    if name == "Yeshwanth":
        return redirect(url_for("home"))
    return "Hi! {}".format(name)

if __name__ == '__main__':
    app.run(debug = True) # "debug = True" helps make simultaneous changes in the website without restarting the server.