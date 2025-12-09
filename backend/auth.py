#!/usr/bin/env python

#-----------------------------------------------------------------------
# auth.py
# Authors: Alex Halderman, Scott Karlin, Brian Kernighan, Bob Dondero,
#          and Joshua Lau '26
#-----------------------------------------------------------------------

import urllib.request
import urllib.parse
import re
import json
import flask
from backend.top import app
from backend import database

#-----------------------------------------------------------------------

_CAS_URL = 'https://fed.princeton.edu/cas/'


#-----------------------------------------------------------------------

@app.route('/api/getusername', methods=['GET'])
def api_getusername():
    if not is_authenticated():
        flask.abort(403)
    return flask.jsonify({"username": get_username()})

#-----------------------------------------------------------------------

@app.route('/api/profile', methods=['GET'])
def api_profile():
    if not is_authenticated():
        flask.abort(403)
    username = get_username()
    ok, user_data = database.get_user_by_username(username)
    if not ok:
        # User not found in DB, return session data
        return flask.jsonify({
            "user": get_user_info(),
            "username": username,
            "firstname": get_firstname(),
            "fullname": get_fullname(),
            "email": get_email(),
            "favorite_cuisine": [],
            "allergies": [],
            "dietary_restrictions": [],
            "admin_status": False
        })
    # Return data from database (favorite_cuisine, allergies, and dietary_restrictions are arrays)
    return flask.jsonify({
        "user": get_user_info(),
        "username": user_data.get('netid', ''),
        "firstname": user_data.get('firstname', ''),
        "fullname": user_data.get('fullname', ''),
        "email": user_data.get('email', ''),
        "favorite_cuisine": user_data.get('favorite_cuisine', []),
        "allergies": user_data.get('allergies', []),
        "dietary_restrictions": user_data.get('dietary_restrictions', []),
        "admin_status": user_data.get('admin_status', False)
    })

#-----------------------------------------------------------------------

@app.route('/api/profile', methods=['PUT', 'POST'])
def api_profile_update():
    if not is_authenticated():
        flask.abort(403)
    
    data = flask.request.get_json()
    print(f"DEBUG: PUT /api/profile received data: {data}")
    if not data:
        print("DEBUG: No JSON data provided")
        return flask.jsonify({"error": "No data provided"}), 400
    
    username = get_username()
    
    # Check which field to update
    if 'favorite_cuisine' in data:
        favorite_cuisine = data.get('favorite_cuisine', [])
        print(f"DEBUG: Updating {username} with cuisines: {favorite_cuisine}")
        ok, user_data = database.update_favorite_cuisine(username, favorite_cuisine)
    elif 'allergies' in data:
        allergies = data.get('allergies', [])
        print(f"DEBUG: Updating {username} with allergies: {allergies}")
        ok, user_data = database.update_allergies(username, allergies)
    elif 'dietary_restrictions' in data:
        dietary_restrictions = data.get('dietary_restrictions', [])
        print(f"DEBUG: Updating {username} with dietary_restrictions: {dietary_restrictions}")
        ok, user_data = database.update_dietary_restrictions(username, dietary_restrictions)
    else:
        return flask.jsonify({"error": "No valid fields to update"}), 400
    
    print(f"DEBUG: Update result - ok: {ok}, data: {user_data}")
    if not ok:
        print(f"DEBUG: Error updating user: {user_data}")
        return flask.jsonify({"error": user_data}), 400
    
    return flask.jsonify({
        "username": user_data.get('netid', ''),
        "firstname": user_data.get('firstname', ''),
        "fullname": user_data.get('fullname', ''),
        "email": user_data.get('email', ''),
        "favorite_cuisine": user_data.get('favorite_cuisine', []),
        "allergies": user_data.get('allergies', []),
        "dietary_restrictions": user_data.get('dietary_restrictions', [])
    })

#-----------------------------------------------------------------------

@app.route('/api/logout-app', methods=['POST'])
def api_logoutapp():
    flask.session.clear()
    return flask.jsonify({"status": "logged out"})

#-----------------------------------------------------------------------

@app.route('/logoutapp', methods=['GET'])
def logoutapp():

    flask.session.clear()
    return flask.redirect('/logout_app')

#-----------------------------------------------------------------------

@app.route('/logoutcas', methods=['GET'])
def logoutcas():

    # Log out of the CAS session, and then the application.
    logout_url = (_CAS_URL + 'logout?service='
        + urllib.parse.quote(
            re.sub('logoutcas', 'logout_cas', flask.request.url)))
    return flask.redirect(logout_url)

#-----------------------------------------------------------------------

# Return url after stripping out the "ticket" parameter that was
# added by the CAS server.

def strip_ticket(url):
    if url is None:
        return "something is badly wrong"
    url = re.sub(r'ticket=[^&]*&?', '', url)
    url = re.sub(r'\?&?$|&$', '', url)
    return url

#-----------------------------------------------------------------------

# Validate a login ticket by contacting the CAS server. If
# valid, return the user's user_info; otherwise, return None.

def validate(ticket):
    val_url = (_CAS_URL + "validate"
        + '?service='
        + urllib.parse.quote(strip_ticket(flask.request.url))
        + '&ticket='
        + urllib.parse.quote(ticket)
        + '&format=json')
    with urllib.request.urlopen(val_url) as flo:
        result = json.loads(flo.read().decode('utf-8'))

    if (not result) or ('serviceResponse' not in result):
        return None

    service_response = result['serviceResponse']

    if 'authenticationSuccess' in service_response:
        user_info = service_response['authenticationSuccess']
        return user_info

    if 'authenticationFailure' in service_response:
        print('CAS authentication failure:', service_response)
        return None

    print('Unexpected CAS response:', service_response)
    return None

#-----------------------------------------------------------------------

def is_authenticated():

    return 'user_info' in flask.session

#-----------------------------------------------------------------------

def get_user_info():

    return flask.session.get('user_info')

#-----------------------------------------------------------------------

def get_username():

    user_info = flask.session.get('user_info')
    if user_info is None:
        return ''
    return user_info.get('user', '')

#-----------------------------------------------------------------------

def get_fullname():

    user_info = flask.session.get('user_info')
    if user_info is None:
        return ''
    return user_info.get('attributes', {}).get('displayname', [''])[0]

#-----------------------------------------------------------------------

def get_firstname():

    user_info = flask.session.get('user_info')
    if user_info is None:
        return ''
    return user_info.get('attributes', {}).get('givenname', [''])[0]

#-----------------------------------------------------------------------

def get_email():
    
    user_info = flask.session.get('user_info')
    if user_info is None:
        return ''
    return user_info.get('attributes', {}).get('mail', [''])[0]

#-----------------------------------------------------------------------

# Authenticate the user. Do not return unless the user is
# successfully authenticated.

def authenticate():

    # If the user_info is in the session, then the user was
    # authenticated previously. Ensure they're in the database and return.
    if 'user_info' in flask.session:
        username = get_username()
        ok, user_data = database.get_user_by_username(username)
        if not ok:
            # User not in DB, insert them now
            email = get_email()
            firstname = get_firstname()
            fullname = get_fullname()
            print(f"DEBUG authenticate(): User {username} not in DB, inserting now")
            database.upsert_user(username, email, firstname, fullname)
        return

    # If the request does not contain a login ticket, then redirect
    # the browser to the login page to get one.
    ticket = flask.request.args.get('ticket')
    if ticket is None:
        login_url = (_CAS_URL + 'login?service=' +
            urllib.parse.quote(flask.request.url))
        flask.abort(flask.redirect(login_url))

    # If the login ticket is invalid, then redirect the browser
    # to the login page to get a new one.
    user_info = validate(ticket)
    if user_info is None:
        login_url = (_CAS_URL + 'login?service='
            + urllib.parse.quote(strip_ticket(flask.request.url)))
        flask.abort(flask.redirect(login_url))

    # The user is authenticated, so store the user_info in
    # the session and return.
    flask.session['user_info'] = user_info
    
    # Also store the user in the database
    username = get_username()
    email = get_email()
    firstname = get_firstname()
    fullname = get_fullname()
    print(f"DEBUG authenticate(): Inserting user - username: {username}, email: {email}, firstname: {firstname}, fullname: {fullname}")
    ok, result = database.upsert_user(username, email, firstname, fullname)
    print(f"DEBUG authenticate(): upsert_user result - ok: {ok}, result: {result}")
    
    # Redirect to home page (stripping the ticket parameter)
    flask.abort(flask.redirect(strip_ticket(flask.request.url)))

