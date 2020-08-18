import os
import sign_out
import login
import admin
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
app.config['JSON_SORT_KEYS'] = False
Debug(app)

app.add_url_rule('/signout' , view_func=sign_out.signout) 
app.add_url_rule('/login' , view_func=login.login) 
app.add_url_rule('/admin' , view_func=admin.admin) 

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


app.permanent_session_lifetime = timedelta(days=1)
app.secret_key = 'Joshi'
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
@app.route('/', methods=["POST", "GET"])

def signin():
    # session.pop('password', None)
    # session.pop('email', None)
    # session.pop('name', None)
    if 'name' in session:
        flash('Already Signed in')
        return redirect(url_for('admin'))
    if 'name' not in session:
        flash('Welcome')
        return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/signin_validation', methods=["POST", "GET"])
def signin_validation():
    if request.method == 'POST':
        get_password=request.form['signinPassword']
        password = get_password
        get_email=request.form['signinEmail']
        email = get_email
        check_user = db.execute("select * from public.users where email = :email", {'email' : email}).fetchone()


        if check_user: 
            list = []
            for i in check_user:
               list.append(i)
            flag=0
            if list[1] == email and list[2] == password:
                flag=1
                session.permanent = True
                session['name'] = list[0]
                session['password'] = list[2]
                session['email'] = list[1]
                session['date'] = list[3]
                flash('Successfully Signed In')
                return redirect(url_for('admin'))
            if not flag:
                flash('User name or password is incorrect')
                return redirect(url_for('signin'))
        if not check_user:
            flash('You are not signed-up in this website. Please register first.')
            return redirect(url_for('signin'))
    if request.method == 'GET':
        flash('Failed To SignIn')
        return redirect(url_for('signin'))



@app.route('/register' , methods = ['POST','GET'])
def register():
   if request.method == 'POST':
      name = request.form['signupName']
      email = request.form['signupEmail']
      password = request.form['signupPassword']

      check_user = db.execute("select * from public.users where email = :email", {'email' : email}).fetchall()
      
      if check_user:
         flash('Hey you.....You are Already registered')
         return redirect(url_for('signin'))
      else :
         db.execute("INSERT INTO public.users (name, email, password) VALUES (:name, :email , :password)", {
            "name":name, "email":email, "password":password})
         db.commit()

         session['name'] = name
         session['email'] = email
         session['password'] = password

         flash('Registraion successful')
         return redirect(url_for('admin'))
   else:
      if 'name' in session:
         flash('Hey There !! You Have done the registration part. . . . ')
         return redirect(url_for('admin'))
      else:
         flash('else flashed')
         return render_template('signin.html')

@app.route('/book', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        title = request.form['byTitle']
        title = title.title()
        isbn = request.form['byIsbn']
        author = request.form['byAuthor']
        year = request.form['byYear']

        list = []
        text = None
        baseUrl = request.base_url
        if title:
            result = db.execute(" SELECT * FROM books WHERE title LIKE '%"+title+"%' ;").fetchall()
            text = title
        elif year:
            result = db.execute(" SELECT * FROM books WHERE year = :year", {'year':year}).fetchall()
            text = year
        elif isbn:
            result = db.execute(" SELECT * FROM books WHERE isbn LIKE '%"+isbn+"%' ;").fetchall()
            text = isbn
        elif author:
            result = db.execute(" SELECT * FROM books WHERE author LIKE '%"+author+"%' ;").fetchall()
            text = author
        if result: 
            for i in result : 
                list.append(i)
            itemsCount = len(list)
            return render_template('search.html', baseUrl = baseUrl,  items = list, msg = "Following Search results matched", text = text , itemsCount = itemsCount)
        else:
            return render_template('search.html', msgNo = "No Entry Found" , text = text)

    return render_template ('search.html')

@app.route("/name/<string:name>")
def namea(name):
    name=name
    return "hello "+name

@app.route("/api/<string:isbn>")
def api(isbn):
    if 'email' in session: 
        data=db.execute("SELECT * FROM public.books WHERE isbn = :isbn",{"isbn":isbn}).fetchone()
        flag=False
        if data is not None:
            flag=True
            res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "2OQ8UVpiwShIj0OTy3dSAg", "isbns": isbn})
            objectt = {
            "title": data.title,
            "author": data.author,
            "year": data.year,
            "isbn": isbn,
            "review_count":res.json()['books'][0]['work_ratings_count'],
            "average_rating":res.json()['books'][0]['average_rating']
            }
        if flag is True:
            return  jsonify(objectt)
        else:
            return render_template('404.html')


@app.route('/book/<string:isbn>', methods = ['GET', 'POST'])
def singleBook(isbn):
    isbn = isbn
    email = session['email']
    apiCall = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "PlM0Yn7UcJQxgM6X2k1rA", "isbns": isbn })
    apidata = apiCall.json()
    dbdata = db.execute(" SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    dbreviews = db.execute('SELECT * FROM reviews WHERE isbn = :isbn', {'isbn': isbn}).fetchall()
    alreadyHasReview = db.execute('SELECT * FROM public.reviews WHERE isbn = :isbn and email = :email ', {'isbn': isbn, 'email': email}).fetchall()
    if request.method == 'POST':
        if alreadyHasReview: 
            flash('You alreaddy submitted a review on this book')
        if not alreadyHasReview : 
            rating = int(request.form['rating'])
            comment = request.form['comment']
            email = session['email']
            fisbn = request.form['isbn']
            db.execute("INSERT into public.reviews (email, rating, comment, isbn) Values (:email, :rating, :comment, :isbn)", {'email': email, 'rating': rating, 'comment': comment, 'isbn': fisbn})
            db.commit()
            flash('WoW, Your review has been added successfully!! ')
    
    if apiCall:
        return render_template('singlebook.html', apidata = apidata, dbdata = dbdata, dbreviews = dbreviews, isbn = isbn )
    else:
        flash('Data fetch failed')
        return render_template('singlebook.html')



if __name__ == '__main__':
    app.run(host="127.0.0.1",debug =True)