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

#Haven't made yet
@app.route("/")
def home():
    return render_template("index.html", auth=verify_staff(), user="Alex")

def verify_staff():
    return "user" in session and session["user"] == "Alex"

@app.route("/logout")
def logout():
    session.pop("user")
    return redirect(url_for("home"))

@app.route("/login")
def login():
    session["user"] = "Alex"
    return render_template("login.html", auth=verify_staff(), user="Alex")

@app.route("/staff")
def staff_index():
    if (verify_staff()):
        return render_template("staff_index.html", auth=verify_staff(), user="Alex")
    else:
        return redirect(url_for("home"))

@app.route("/register")
def register():
    pass



#Helper function: Goes thru inventory database and returns a list where items are
# sorted by amount, least to most
#Called in inventory page whenever inventory.html is rendered
def sortInventory():
    inventoryList = Inventory.query.all()
    sortedAmounts = []
    #Create a list just for the amounts of all items in database
    for item in inventoryList:
        sortedAmounts.append(item.amount)
    sortedAmounts = sorted(sortedAmounts)
    #Go thru database again and...
    for item in inventoryList:
        amount = item.amount
        #Find where item is located in sorted list
        amountIndex = sortedAmounts.index(amount)
        #Add database item to that spot in the sorted list
        sortedAmounts.insert(amountIndex, item)
        #Remove the amount in the list
        sortedAmounts.pop(amountIndex+1)
    return sortedAmounts


#Sort by alphabetical name or small>large amount??
@app.route("/inventory", methods = ["POST", "GET"])
def inventory():
    if request.method == "POST":
        item = request.form["Item"].title()
        amount = request.form["Amount"]
        #Check to see if item already exists in database
        foundItem = Inventory.query.filter_by(name = item).first()
        #If item already exists or user didn't enter an amount:
        if foundItem or amount == "": 
            Inventory.query.filter_by(name = item).delete()
            #If user didn't enter an amount, delete entry
            if amount == "": 
                #commit changes to database and return the inventory template
                database.session.commit()
                return render_template("staff_inventory.html", values = sortInventory(), auth=verify_staff(), user="Alex")
        #Add info user entered into form to database
        newEntry = Inventory(item, amount)
        database.session.add(newEntry)
        database.session.commit()
    return render_template("staff_inventory.html", values = sortInventory(), auth=verify_staff(), user="Alex")


if __name__ == "__main__":
    database.create_all()
    app.run()
