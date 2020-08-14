from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from models import database, User, Inventory

#@google.tokengetter
#def get_access_token():
#    return session.get('access_token')

def get_session_display():
    if "name" in session:
        return (True, session["name"])
    else:
        return (False, "")

def goto_page(s):
    sd = get_session_display()
    return render_template(s, auth=sd[0], user=sd[1])

# TODO TODO temporary bandaid, will change later
def goto_page_inventory(values, editItemID):
    sd = get_session_display()
    return render_template("staff_inventory.html", values=values, editItemID=editItemID, auth=sd[0], user=sd[1])

def goto_page_users(values):
    sd = get_session_display()
    return render_template("staff_users.html", values=values, auth=sd[0], user=sd[1])




def verify_staff():
    pass


@app.route("/")
def home():
    flash("hello")
    sd = get_session_display()
    return goto_page("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        form = request.form
        #hashed_password = generate_password_hash(form['password'], method="sha256")

        found_user = Users.query.filter_by(email=form['email']).first()
        if found_user:
            pw = found_user.password
            if form.get('password') == pw:
                session["email"] = found_user.email
                session["name"] = found_user.name
            else:
                return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))

        session.permanent = True
        session["email"] = form["email"]
        return redirect(url_for("home"))
    else:
        return goto_page("login.html")
    #return google.authorize(callback=url_for('oauth_authorized',
    #    next=request.args.get('next') or request.referrer or None))


#@app.route('/oauth2callback')
#@google.authorized_handler
#def oauth_authorized(resp):
#    next_url = request.args.get('next') or url_for('home')
#    if resp is None:
#        flash(u'You denied the request to sign in.')
#        return redirect(next_url)
#
#    session['google_token'] = (
#        resp['oauth_token'],
#        resp['oauth_token_secret']
#    )
#    session['google_user'] = resp['screen_name']
#
#    flash('You were signed in as %s' % resp['screen_name'])
#    return redirect(next_url)

@app.route("/logout")
def logout():
    session.pop("name", None)
    return redirect(url_for("home"))

@app.route("/staff")
def staff_index():
    if (verify_staff()):
        return goto_page("staff_index.html")
    else:
        return redirect(url_for("home"))

@app.route("/register")
def register():
    pass

@app.route("/users")
def users():
    return goto_page_users(values = Users.query.all())


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
def sortInventoryByCategory(categoryList):
    inventoryList = Inventory.query.all()
    categoryDictionary = {}
    for cat in categoryList:
        categoryDictionary[cat] = "on"
    result = Inventory.query.filter_by(**categoryDictionary).all()
    result = sortInventoryByAmount(result)
    return result


#Parameter sortBy is a string representing how the inventory table should be sorted
#   Values: 'amount', 'dairy', 'grain', 'snacks', etc.
@app.route("/inventory", methods = ["POST", "GET"])
def inventory():
    inventoryList = sortInventoryByAmount(Inventory.query.all())
    if request.method == "POST":
        #If the form being submitted is the Add/Edit Items form at top of page:
        if "Item" in request.form:
            item = request.form["Item"].title()
            amount = request.form["Amount"]
            note = request.form["Note"]
            grain = ""
            produce = ""
            dairy = ""
            snacks = ""
            vegan = ""
            vegetarian = ""
            #Check form data to see if any categories have been checked, set values to 'on' if so
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
                #If user didn't enter an amount, automatically set item amount to 0
                if amount == "":
                    amount = "0"
            #Add info user entered into form to database
            newEntry = Inventory(item, amount, note, grain, produce, dairy, snacks, vegan, vegetarian)
            database.session.add(newEntry)
            database.session.commit()
        #If user submits a form to filter inventory by categories
        elif "filterBy" in request.form:
            catList = []
            for cat in request.form:
                #filterBy is the submit button's name, so it's not a category
                if cat != "filterBy":
                    catList.append(cat)
            inventoryList = sortInventoryByCategory(catList)
            return render_template("staff_inventory.html", values = inventoryList, editItemID = "None", auth=verify_staff(), user="Alex")
        #If a 'Remove' button in the table is clicked:
        elif "removeItemID" in request.form:
            #Remove item from database and commit changes
            removedID = request.form["removeItemID"]
            removedItem = Inventory.query.filter_by(_id = removedID).delete()
            database.session.commit()
        #If an "edit" button in the table is clicked:
        elif "editItemID" in request.form:
            #Record the item id of the specific item to edit, return the template w/ this id as attribute for use in template
            editID = int(request.form["editItemID"])
            return render_template("staff_inventory.html", values = inventoryList, editItemID = editID, auth=verify_staff(), user="Alex")
        #If changes within the table are saved:
        elif "editedItemID" in request.form:
            #Assign vars to newly inputted values, assign to that item in the database and save
            editedID = request.form["editedItemID"]
            newName = request.form["newName"].title()
            newAmount = request.form["newAmount"]
            item = Inventory.query.filter_by(_id = editedID).first()
            item.name = newName
            item.amount = newAmount
            database.session.commit()

    inventoryList = sortInventoryByAmount(Inventory.query.all())
    return goto_page_inventory(values = sortInventoryByAmount(Inventory.query.all()), editItemID = "None")

