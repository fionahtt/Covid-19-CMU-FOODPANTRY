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

    #Food categories, "on" if applicable, "" if not
    grain = database.Column(database.String(2))
    produce = database.Column(database.String(2))
    dairy = database.Column(database.String(2))
    snacks = database.Column(database.String(2))
    vegan = database.Column(database.String(2))
    vegetarian = database.Column(database.String(2))

    #maybe add image later on somehow?
    def __init__(self, name, amount, grain, produce, dairy, snacks, vegan, vegetarian):
        self.name = name
        self.amount = amount
        self.grain = grain
        self.produce = produce
        self.dairy = dairy
        self.snacks = snacks
        self.vegan = vegan
        self.vegetarian = vegetarian

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
def sortInventoryByAmount(inventoryList):
    #Create a list just for the amounts of all items in database
    sortedAmounts = []
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


#Might just make sortInventoryByAmount and sortInventoryByAlphabetical one function later
def sortInventoryByAlphabetical(inventoryList):
    sortedNames = []
    for item in inventoryList:
        sortedNames.append(item.name)
    sortedNames = sorted(sortedNames)
    for item in inventoryList:
        name = item.name
        nameIndex = sortedNames.index(name)
        sortedNames.insert(nameIndex, item)
        sortedNames.pop(nameIndex+1)
    return sortedNames


#Uses a builtin sqlalchemy command to return a list of only the items under the given category
def sortInventoryByCategory(category):
    inventoryList = Inventory.query.all()
    categoryDictionary = {category: "on"}
    result = Inventory.query.filter_by(**categoryDictionary).all()
    return result


#Put in how inventory should be sorted as a parameter later
@app.route("/inventory", methods = ["POST", "GET"])
def inventory():
    if request.method == "POST":
        print(request.form)
        print("Vegetarian" in request.form)
        item = request.form["Item"].title()
        amount = request.form["Amount"]

        grain = ""
        produce = ""
        dairy = ""
        snacks = ""
        vegan = ""
        vegetarian = ""

        if "Grain" in request.form:
            grain = "on"
        if "Produce" in request.form:
            produce = "on"
        if "Dairy" in request.form:
            dairy = "on"
        if "Snacks" in request.form:
            snacks = "on"
        if "Vegan" in request.form:
            vegan = "on"
        if "Vegetarian" in request.form:
            vegetarian = "on"

        #Check to see if item already exists in database
        foundItem = Inventory.query.filter_by(name = item).first()
        #If item already exists or user didn't enter an amount:
        if foundItem or amount == "": 
            Inventory.query.filter_by(name = item).delete()
            #If user didn't enter an amount, delete entry
            if amount == "": 
                #commit changes to database and return the inventory template
                database.session.commit()

                return render_template("staff_inventory.html", values = sortInventoryByAmount(Inventory.query.all()), auth=verify_staff(), user="Alex")
        #Add info user entered into form to database
        newEntry = Inventory(item, amount, grain, produce, dairy, snacks, vegan, vegetarian)
        database.session.add(newEntry)
        database.session.commit()
    return render_template("staff_inventory.html", values = sortInventoryByAmount(Inventory.query.all()), auth=verify_staff(), user="Alex")

if __name__ == "__main__":
    database.create_all()
    app.run()
