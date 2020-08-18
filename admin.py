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

app.add_url_rule('/signout' , view_func=sign_out.sign_out) 
app.add_url_rule('/login' , view_func=login.login) 
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


app.permanent_session_lifetime = timedelta(days=1)
app.secret_key = 'you'
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
def admin():
    if 'email' in session:    
        email = session['email']   
        db_user_query = db.execute("select * from public.users where email = :email", {'email': email}).fetchall()
        db_review_query = db.execute(" select * from public.reviews where email = :email", {'email' : email}).fetchall()
        userInfo = {
            'name': db_user_query[0][0], 
            'email': session['email'],
            'password': db_user_query[0][2],
            'date': db_user_query[0][3]
        }
        reviewCount = len(db_review_query)
        return render_template('admin.html', userInfo = userInfo, reviewedbooks = db_review_query , reviewCount= reviewCount )

    if 'email' not in session: 
        flash('Sign In first Before login')
        return redirect(url_for('signin'))
