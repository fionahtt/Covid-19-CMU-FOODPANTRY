from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy

from flaskTest import Users

user = Users("Alex", "asdf@gmail.com", "asdf")
