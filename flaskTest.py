from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "hello"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

database = SQLAlchemy(app)

class Inventory(database.Model):
    _id = database.Column("id", database.Integer, primary_key = True)
    name = database.Column(database.String(100))
    amount = database.Column(database.Integer)
    #maybe add image later on somehow?
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/inventory", methods = ["POST", "GET"])
def inventory():
    if request.method == "POST":
        item = request.form["Item"].title()
        amount = request.form["Amount"]

        #Check to see if item already exists in database
        foundItem = Inventory.query.filter_by(name = item).first()
        if foundItem or amount == "": 
            Inventory.query.filter_by(name = item).delete()
            #If user didn't enter an amount, delete entry
            if amount == "": 
                database.session.commit()
                return render_template("inventory.html", values = Inventory.query.all())
                
        newEntry = Inventory(item, amount)
        database.session.add(newEntry)
        database.session.commit()
    return render_template("inventory.html", values = Inventory.query.all())


if __name__ == "__main__":
    database.create_all()
    app.run()