import flask
from flask import render_template
import os
import sign_out
import login
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, redirect, render_template, url_for , session, request, flash
from datetime import timedelta
import psycopg2
import requests
import json
from flask import jsonify
from flask_debug import Debug
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
Debug(app)

app.add_url_rule('/login' , view_func=login.login) 
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


app.permanent_session_lifetime = timedelta(days=1)
app.secret_key = 'you'
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
def signout():
    session.pop('password', None)
    session.pop('email', None)
    session.pop('name', None)
    return  redirect(url_for('signin'))