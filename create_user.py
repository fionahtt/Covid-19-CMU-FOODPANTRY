from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy

from flaskTest import database, Users

alex = Users("Alex", "alexli2468@gmail.com", "zsdc")
fiona = Users("Fiona", "fionahtt@gmail.com", "12345")
sara = Users("Sara", "sarasong4@gmail.com", "website") 

admin = [alex, fiona, sara]
for acc in admin:
    exists = Users.query.filter(Users.email == acc.email).first()
    if not exists:
    	database.session.add(acc)
    	database.session.commit()
