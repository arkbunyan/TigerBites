import flask
import flask_session
import flask_sqlalchemy
import os
from backend import auth
from backend import database
from backend.top import app
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file
session_database_url = os.getenv("TB_DATABASE_URL")
session_database_url = session_database_url.replace('postgres://', 'postgresql://')
# Configure session to use the database
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SQLALCHEMY_DATABASE_URI'] = session_database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_SQLALCHEMY'] = flask_sqlalchemy.SQLAlchemy(app)
flask_session.Session(app)

# Home Page
@app.route('/home', methods=['GET'])
def home_page():
    # Protected entrance to page
    auth.authenticate()
    # NOTE: We probably want a list of dicts here
    # restaurants = database.get_restaurant_cards()
    restaurants = database.load_all_restaurants()
    firstname = auth.get_firstname()
    print(restaurants)
    if restaurants[0] is False:
        html_code = flask.render_template('error.html',
            message=restaurants[1])
        response = flask.make_response(html_code)
        return response
    html_code = flask.render_template('home.html',
        restaurants=restaurants[1], firstname=firstname)
    response = flask.make_response(html_code)
    return response

@app.route('/map_page', methods=['GET'])
def map_page():
    firstname = auth.get_firstname()
    html_code = flask.render_template('map_page.html', firstname=firstname)
    response = flask.make_response(html_code)
    return response

@app.route('/profile_page', methods=['GET'])
def profile_page():
    # Protected entrance to page
    auth.authenticate()
    user = auth.get_user_info()
    username = auth.get_username()
    firstname = auth.get_firstname()
    fullname = auth.get_fullname()
    email = auth.get_email()
    html_code = flask.render_template('profile_page.html', user=user, username=username, firstname=firstname, fullname=fullname, email=email)
    response = flask.make_response(html_code)
    return response

@app.route('/logout_app', methods=['GET'])
def logout_app():
    html_code = flask.render_template('logout_app.html')
    return flask.make_response(html_code)

@app.route('/logout_cas', methods=['GET'])
def logout_cas():
    return flask.redirect('/logoutcas')

@app.route('/search_results', methods=['GET'])
def search_results():
    
    # Test Restaurant Data
    name = flask.request.args.get('name', '')
    category = flask.request.args.get('category', '')
    restaurants = database.restaurant_search([name, category])
    if restaurants[0] is False:
        html_code = flask.render_template('error.html',
            message=restaurants[1])
        response = flask.make_response(html_code)
        return response

    html_code = flask.render_template('search_results.html', 
        restaurants=restaurants[1])
    response = flask.make_response(html_code)
    return response

@app.route('/restaurants/<int:rest_id>', methods=['GET'])
def restaurant_details(rest_id):

    ok_r, rest = database.load_restaurant_by_id(rest_id)
    if not ok_r:
        return flask.abort(404)

    ok_m, menu = database.load_menu_for_restaurant(rest_id)
    if not ok_m:
        menu = []

    html = flask.render_template('restaurant_details.html',
                                 restaurant=rest, menu_items=menu)
    return flask.make_response(html)

# @app.route('/protected')
# def protected():
#     # Force CAS authentication (will redirect to CAS if needed)
#     auth.authenticate()
#     return f"Hello {auth.get_username()}! This is protected."

@app.route('/api/data')
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