import flask
from flask import render_template

# @app.route('/test', methods=['GET'])
def login():
     return render_template('signin.html')
