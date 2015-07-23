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
TOKEN = 'CAACEdEose0cBADHrN0vLLAsXWu0Yd5jmGii3ZAO3sZABrmGv0juZC0Q8MKdvFWSavlzAJVfiXc1aZA97vZAPzqVhl80q5dVvtnqPwks7aCvGicmQ93qcybdPwbFVRHGLnZA0cSZAThkFgYCdFFTKd55yIIAFGPbySmQWh3FLg1Sx7yd7Rdh33AEKF5x4EtobibeMh7SY5LjF5nGxv7JxntQrArOim0RShIZD'

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
    # TOKEN = generate_TOKEN()
    req = requests.get('https://graph.facebook.com/me/friends?access_token=' + TOKEN).json()
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

# query_db returns as a tuple with two elements (and empty last element)
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
def graph_name():
    friends = flatten_tuple(query_db('SELECT NAME FROM friends'))
    # Convert from unicode to UTF8
    friends = [x.encode('UTF8') for x in friends]
    letter_map = {'A': 0,'B': 0,'C': 0,'D': 0,'E': 0,'F': 0,'G': 0,'H': 0,
                  'I': 0,'J': 0, 'K': 0,'L': 0,'M': 0,'N': 0,'O': 0,'P': 0,
                  'Q': 0,'R': 0,'S': 0,'T': 0,'U': 0,'V': 0,'W': 0,'X': 0,
                  'Y': 0,'Z': 0}
    for friend in friends:
            letter_map[friend[0]] += 1
    return render_template('show_graphs.html', data=letter_map)

@app.route('/location')
def locate():
    s = requests.get('https://graph.facebook.com/me/tagged_places?access_token=' + TOKEN).json()
    t = requests.get(s['paging']['next']).json()
    s = dict(s.items() + t.items())
    # paging to get next items
    while 'next' in t['paging'].keys():
        t = requests.get(t['paging']['next']).json()
        s = dict(t.items() + s.items())
    lst_of_locations = []
    for place in s['data']:
        location_dict = {'name':'', 'lat':0, 'lon':0}
        location_dict['name'] = place['place']['name'].encode('UTF8')
        location_dict['lat'] = place['place']['location']['latitude']
        location_dict['lon'] = place['place']['location']['longitude']
        lst_of_locations.append(location_dict)
    return render_template('show_locations.html', data=lst_of_locations)

@app.route('/friends/<field>')
def friends_graph(field):
    friends = flatten_tuple(query_db('SELECT ID FROM friends'))
    val = {}
    for friend in friends:
        req = requests.get('https://graph.facebook.com/' + friend + '?fields=' + field).json()
        lst = req[field]
        # possibility for multiple values in each field
        for el in lst:
            # trying this out for devices first so that's why I'm using 'os'
            if el['os'] not in val.keys():
                val[el['os']] = 1
            else:
                val[el['os']] += 1
    return render_template('show_friends_graphs.html', field=field, data=val)

# fire up server
if __name__ == '__main__':
    app.run()
