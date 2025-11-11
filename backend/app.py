import flask
import flask_session
import flask_sqlalchemy
import os
from backend import auth
from backend import database
from backend.top import app


session_database_url = os.getenv('TB_DATABASE_URL') 
session_database_url = session_database_url.replace(
    'postgres://', 'postgresql://')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SQLALCHEMY_DATABASE_URI'] = session_database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_SQLALCHEMY'] = flask_sqlalchemy.SQLAlchemy(app)
flask_session.Session(app)

# Test React
@app.route('/', methods=['GET'])
# @app.route('/<path:path>')
def index():
    auth.authenticate()
    return flask.send_file('../frontend/react/index.html')

# Home Page
@app.route('/home', methods=['GET'])
def home():
    auth.authenticate()
    restaurants = database.load_all_restaurants()
    firstname = auth.get_firstname()

    if restaurants[0] is False:
        return flask.jsonify({"error": restaurants[1]}), 400

    return flask.jsonify({
        "firstname": firstname,
        "restaurants": restaurants[1]
    })


@app.route('/map_page', methods=['GET'])
def map():
    firstname = auth.get_firstname()
    return flask.jsonify({"firstname": firstname})


@app.route('/profile_page', methods=['GET'])
def profile():
    # Protected entrance to page
    auth.authenticate()
    return flask.jsonify({
        "user": auth.get_user_info(),
        "username": auth.get_username(),
        "firstname": auth.get_firstname(),
        "fullname": auth.get_fullname(),
        "email": auth.get_email()
    })

@app.route('/logout_app', methods=['GET'])
def logout_app():
    html_code = flask.render_template('logout_app.html')
    return flask.make_response(html_code)

@app.route('/logout_cas', methods=['GET'])
def logout_cas():
    return flask.redirect('/logoutcas')

@app.route('/api/search', methods=['GET'])
def search_results():
    
    # Test Restaurant Data
    name = flask.request.args.get('name', '')
    category = flask.request.args.get('category', '')
    restaurants = database.restaurant_search([name, category])

    if not restaurants[0]:
        return flask.jsonify({"error": restaurants[1]}), 400

    return flask.jsonify({"restaurants": restaurants[1]})

@app.route('/api/restaurants/<rest_id>', methods=['GET'])
def restaurant_details(rest_id):
    ok_r, rest = database.load_restaurant_by_id(rest_id)
    if not ok_r:
        return flask.abort(404)

    ok_m, menu = database.load_menu_for_restaurant(rest_id)
    if not ok_m:
        menu = []

    return flask.jsonify({"restaurant": rest, "menu": menu})

# @app.route('/protected')
# def protected():
#     # Force CAS authentication (will redirect to CAS if needed)
#     auth.authenticate()
#     return f"Hello {auth.get_username()}! This is protected."

@app.route('/data')
def api_data():
    if not auth.is_authenticated():
        flask.abort(403)
    return flask.jsonify({"user": auth.get_username(), "data": []})

@app.route('/', methods=['GET'])
def landing_page():
    html_code = flask.render_template('welcome_login.html')
    response = flask.make_response(html_code)
    return response


if __name__ == "__main__":
    app.run(debug=True)