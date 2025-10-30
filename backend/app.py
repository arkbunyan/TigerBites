import flask
import flask_session
import flask_sqlalchemy
import os
import auth
from top import app

# import database
session_database_url = os.getenv('SESSION_DATABASE_URL',
    'sqlite:///proto_sessions.sqlite') 
session_database_url = session_database_url.replace(
    'postgres://', 'postgresql://')
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
    restaurants = [True, []]  # Placeholder
    if restaurants[0] is False:
        html_code = flask.render_template('error.html',
            message=restaurants[1])
        response = flask.make_response(html_code)
        return response
    html_code = flask.render_template('home.html',
        restaurants=restaurants[1])
    response = flask.make_response(html_code)
    return response

@app.route('/search_form', methods=['GET'])
def search_form():
    html_code = flask.render_template('search_form.html')
    response = flask.make_response(html_code)
    return response

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