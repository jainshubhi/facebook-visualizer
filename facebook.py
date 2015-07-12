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

# # facebook app configuration
# APP_ID =
# APP_SECRET =
# CLIENT_CREDENTIALS =

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
    friends = flatten_tuple(query_db('SELECT NAME FROM friends'))
    return render_template('show_friends.html', friends=friends)

# refresh data regarding friends from facebook
@app.route('/refresh')
def refresh_friends():
    if not session.get('logged_in'):
        abort(401)
    friends = flatten_tuple(query_db('SELECT NAME FROM friends'))
    # token = generate_token()
    token = 'CAACEdEose0cBAN9Ex2HoNW0ppDZBUhSXOf45uZAq1OzZA3HcV8wGwXura69knSB9idu2cW2gGdFIEmZAp3j9TJ7RBaaaZC7lzHbFFW1KhJecECYZCVWATUDc7vPeiBHk4osy2F1RBf433ngWK7zHsTy4pYJwbvEzVD8mywVHZBzPZA0URE8dNbqB5lzNr7OmmDDtzxXBtdmvi4OkO5kDVt1URZB8vpNruResZD'
    req = requests.get('https://graph.facebook.com/me/friends?access_token=' + token).json()
    has_new_friends = False
    for friend in req['data']:
        if friend['name'] not in friends:
            g.db.execute('INSERT INTO friends (ID, NAME) VALUES (?, ?)',
                         [friend['id'], friend['name']])
            g.db.commit()
            has_new_friends = True
    if has_new_friends:
        flash('You made some new friends!')
    else:
        flash('No new friends for you Senor!')
    return redirect(url_for('show_friends'))

def flatten_tuple(lst_of_tup):
    lst = []
    for tup in lst_of_tup:
        lst.append(tup[0])
    return lst

# query db easily
def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

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
    # empty friends table
    g.db.execute('DELETE FROM friends')
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_friends'))

@app.route('/graph')
def graph():
    friends = flatten_tuple(query_db('SELECT NAME FROM friends'))
    # Convert from unicode to UTF8
    friends = [x.encode('UTF8') for x in friends]
    letter_map = {}
    for friend in friends:
        if friend[0] in letter_map.keys():
            letter_map[friend[0]] += 1
        else:
            letter_map[friend[0]] = 1
    print letter_map
    return render_template('show_graphs.html', data=letter_map)

# fire up server
if __name__ == '__main__':
    app.run()
