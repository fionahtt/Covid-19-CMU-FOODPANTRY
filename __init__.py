"""App entry point"""

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

if __name__ == "__main__":
    import routes
    database.create_all()
    app.run()
