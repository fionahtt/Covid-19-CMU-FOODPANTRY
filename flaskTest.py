from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
#from flask_oauth import OAuth
from datetime import timedelta
#from werkzeug.security import generate_password_hash
#from flask_login import LoginManager, UserMixin
#from authlib.integrations.flask_client import OAuth

#GOOGLE_CLIENT_ID='434804791134-5kl3ab8ml5k62tftvrv0cqos2jh2evs9.apps.googleusercontent.com'
#GOOGLE_CLIENT_SECRET='gPM0ax_AUvJG2Nrgf6Go9II-'
SECRET_KEY='hello'
#REDIRECT_URI = '/oauth2callback'

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///default.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=60)

database = SQLAlchemy(app)
#oauth = OAuth()

#google = oauth.remote_app(
#    'google',
#    base_url='https://www.google.com/accounts/',
#    authorize_url='https://accounts.google.com/o/oauth2/auth',
#    request_token_url=None,
#    request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
#    'response_type': 'code'},
#    access_token_url='https://accounts.google.com/o/oauth2/token',
#    access_token_method='POST',
#    access_token_params={'grant_type': 'authorization_code'},
#    consumer_key=GOOGLE_CLIENT_ID,
#    consumer_secret=GOOGLE_CLIENT_SECRET
#)



class Users(database.Model):
    __tablename__ = 'users'
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100))
    email = database.Column(database.String(100))
    password = database.Column(database.String(100))

    def __init__(self, name='', email='', password=''):
        self.name = name
        self.email = email
        self.password = password


#The following 3 tables make it so that staff can add their own categories using a many-to-many relationship
itemCategories = database.Table("itemCategories",
    database.Column("itemID", database.Integer, database.ForeignKey('items.id')),
    database.Column("categoryID", database.Integer, database.ForeignKey('categories.id'))
)


class Categories(database.Model):
    id = database.Column("id", database.Integer, primary_key = True)
    name = database.Column(database.String(100))

    def __init__(self, name):
        self.name = name


class Items(database.Model):
    id = database.Column("id", database.Integer, primary_key = True)
    name = database.Column(database.String(100))
    amount = database.Column(database.Integer)
    note = database.Column(database.Text)
    categories = database.relationship("Categories", secondary=itemCategories, backref=database.backref("items", lazy="dynamic"))

    def __init__(self, name, amount, note):
        self.name = name
        self.amount = amount
        self.note = note


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
def goto_page_inventory(catList, values, editItemID):
    sd = get_session_display()
    return render_template("staff_inventory.html", catList=catList, values=values, editItemID=editItemID, auth=sd[0], user=sd[1])

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




#Given a list of category IDs, return a list of all items in inventory
#that fit under all categories in this list
#   NOTE: Might wanna see if I could increase efficiency later
def sortInventoryByCategory(catList):
    #Use a query to:    1) Create a preliminary filter, return all items that fit under first category in catList
    #                      This might reduce a bit of time compared to calling up ALL items in inventory
    #                   2) Sort this list by increasing amount, no more need for another sortInventoryByAmount function
    inventoryList = Items.query.join(Categories, Items.categories).filter(Categories.id==catList[0]).order_by(Items.amount)
    result = []
    for item in inventoryList:
        #Create a list of categories each item has that matches categories in catList
        itemCats = []
        for cat in item.categories:
            if cat.id in catList:
                itemCats.append(cat.name)
        #If the length of catList and itemCats is the same, that means this item fits all filters!
        #   Add to result
        if len(itemCats)==len(catList):
            result.append(item)
    return result


@app.route("/inventory", methods = ["POST", "GET"])
def inventory():
    if request.method == "POST":
        #If the form being submitted is the Add/Edit Items form at top of page:
        if "Item" in request.form:
            item = request.form["Item"].title().strip()
            amount = request.form["Amount"]
            note = request.form["Note"]
            #Check to see if item already exists in Items table
            foundItem = Items.query.filter_by(name = item).first()
            #If item already exists or user didn't enter an amount:
            if foundItem or amount == "": 
                Items.query.filter_by(name = item).delete()
                #If user didn't enter an amount, automatically set item amount to 0
                if amount == "":
                    amount = "0" 
            #Add info user entered into form to database
            newItem = Items(item, amount, note)
            database.session.add(newItem)
            database.session.commit()
            for catID in request.form:
                if (catID != "Item") and (catID != "Amount") and (catID != "Note") and (catID != "Submit"):
                    foundCat = Categories.query.filter_by(id = catID).first()
                    newItem.categories.append(foundCat)
            database.session.commit()
        #If user submits form to add new category
        elif "addCategory" in request.form:
            catName = request.form["Category"].title().strip()
            existingCat = Categories.query.filter_by(name=catName).first()
            if not existingCat:
                newCat = Categories(catName)
                database.session.add(newCat)
                database.session.commit()
        #If user submits a form to filter inventory by categories
        elif "filterBy" in request.form:
            catList = []
            for catID in request.form:
                #filterBy is the submit button's name, so it's not a category
                if catID != "filterBy":
                    catList.append(int(catID))
            inventoryList = sortInventoryByCategory(catList)
            return goto_page_inventory(catList = Categories.query.all(), values = inventoryList, editItemID = "None")
        #If a 'Remove' button in the table is clicked:
        elif "removeItemID" in request.form:
            #Remove item from database and commit changes
            removedID = request.form["removeItemID"]
            removedItem = Items.query.filter_by(id = removedID).delete()
            database.session.commit()
        #If an "edit" button in the table is clicked:
        elif "editItemID" in request.form:
            #Record the item id of the specific item to edit, return the template w/ this id as attribute for use in template
            editID = int(request.form["editItemID"])
            return goto_page_inventory(catList = Categories.query.all(), values = Items.query.order_by(Items.amount).all(), editItemID = editID)
        #If changes within the table are saved:
        elif "editedItemID" in request.form:
            #Assign vars to newly inputted values, assign to that item in the database and save
            editedID = request.form["editedItemID"]
            newName = request.form["newName"].title()
            newAmount = request.form["newAmount"]
            item = Items.query.filter_by(id = editedID).first()
            item.name = newName
            item.amount = newAmount
            database.session.commit()
    return goto_page_inventory(catList = Categories.query.all(), values = Items.query.order_by(Items.amount).all(), editItemID = "None")


if __name__ == "__main__":
    database.create_all()
    alex = Users("Alex", "alexli2468@gmail.com", "zsdc")
    fiona = Users("Fiona", "fionahtt@gmail.com", "12345")
    sara = Users("Sara", "sarasong4@gmail.com", "website")

    admin = [alex, fiona, sara]
    for acc in admin:
        exists = Users.query.filter(Users.email == acc.email).first()
        if not exists:
            database.session.add(acc)
            database.session.commit()

    app.run()
