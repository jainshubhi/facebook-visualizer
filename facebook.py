# all the imports
import sqlite3

import requests

from flask import Flask
from flask import request
from flask import session
from flask import g
from flask import redirect
from flask import url_for
from flask import abort
from flask import render_template
from flask import flash

from contextlib import closing


# flask configuration
DATABASE = '/tmp/facebook.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# facebook app configuration
APP_ID =
APP_SECRET =
CLIENT_CREDENTIALS =

# create our little application :)
app = Flask(__name__)
# determine configuration settings
app.config.from_object(__name__)

# init db
def init_db():
    """Initializes the database."""
    with closing(connect_db()) as db:
        with app.open_resource('./models/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# connect to db
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# before a request is made, the following functions must take place
@app.before_request
def before_request():
    g.db = connect_db()

# after a request is made, the following functions must take place (regardless
# of exception is thrown or not)
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# show names of all friends in db
@app.route('/')
def show_friends():
    if not session.get('logged_in'):
        abort(401)
    friends = query_db('SELECT NAME FROM friends')
    return render_template('show_friends.html', friends=friends)

# refresh data regarding friends from facebook
@app.route('/refresh')
def refresh_friends():
    if not session.get('logged_in'):
        abort(401)
    friends = query_db('SELECT NAME FROM friends')
    token = generate_token()
    req = requests.get('https://graph.facebook.com/me/friends?access_token=' + token)
    for friend in req['data']:
        if friend['name'] not in friends:
            g.db.execute('INSERT INTO friends (ID, NAME) VALUES (?, ?)',
                         friend['id'], friend['name'])
            g.db.commit()
            flash('You made some new friends!')
    return redirect(url_for('show_friends'))

# query db easily
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# generate FB API access token
def generate_token():
    token = requests.get('https://graph.facebook.com/oauth/access_token?client_id=' + APP_ID + '&client_secret=' + APP_SECRET + '&grant_type=' + CLIENT_CREDENTIALS).json()
    return token['access_token']

# method to login to app
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('refresh_friends'))
    return render_template('login.html', error=error)

# method to logout of app
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_friends'))

# fire up server
if __name__ == '__main__':
    app.run()
