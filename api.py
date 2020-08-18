import os
import sign_out
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

# @app.route("/book/api/<string:isbn>")
def api(isbn):
    if 'email' in session: 
        data=db.execute("SELECT * FROM public.books WHERE isbn = :isbn",{"isbn":isbn}).fetchone()
        if data==None:
            return render_template('404.html')
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "PlM0Yn7UcJQxgM6X2k1rA", "isbns": isbn})
        average_rating=res.json()['books'][0]['average_rating']
        work_ratings_count=res.json()['books'][0]['work_ratings_count']
        x = {
        "title": data.title,
        "author": data.author,
        "year": data.year,
        "review_count": work_ratings_count,
        "isbn": isbn,
        "average_rating": average_rating
        }
        # api=json.dumps(x)
        # return render_template("api.json",api=api)
        return  jsonify(x)
