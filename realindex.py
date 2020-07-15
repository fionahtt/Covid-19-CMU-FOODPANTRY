from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = "hello "
#app.permanent_session_lifetime = timedelta(days=5)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column("name", db.String(100))
    password = db.Column("password", db.String(100))

    def __init__(self, name, password):
        self.name = name
        self.password = password


@app.route("/<name>")
def home(name):
    return render_template("index.html")

@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())
@app.route("/click")
def clicked():
    return "Click"
@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["login"]
        password = request.form["password"]
        session["user"] = user

        found_user = users.query.filter_by(name =user).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = users(user, password)
            db.session.add(usr)
            db.session.commit()
        flash("Login Successful!")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already Logged In!")
            #return redirect(url_for("user"))
        return render_template("login.html")

    return render_template("login.html")

@app.route("/user")
def user():
    if "user" in session:
        return session["user"]
    else:
        redirect(url_for("login"))
if __name__ == "__main__":
    db.create_all()
    app.run(debug = True)
