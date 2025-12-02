import flask
import flask_session
import flask_sqlalchemy
import os
from backend import auth
from backend import database
from backend.top import app
from data_management import db_manager


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
def index():
    auth.authenticate()
    return flask.send_file('../frontend/react/index.html')

# Home Page
@app.route('/api/home', methods=['GET'])
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

# Load restaurant data for map
@app.route('/api/map', methods=['GET'])
def map():
    auth.authenticate()
    restaurants = database.load_all_restaurants()

    if restaurants[0] is False:
        return flask.jsonify({"error": restaurants[1]}), 400

    return flask.jsonify({
        "restaurants": restaurants[1]
    })

# Load profile data
@app.route('/profile', methods=['GET'])
def profile_page():
    # Serve React app for client-side profile routing
    auth.authenticate()
    return flask.send_file('../frontend/react/index.html')

# Serve map page
@app.route('/map', methods=['GET'])
def map_page():
    auth.authenticate()
    return flask.send_file('../frontend/react/index.html')

# Serve group page
@app.route('/group', methods=['GET'])
def group_page():
    auth.authenticate()
    return flask.send_file('../frontend/react/index.html')

# Logout route that redirects to CAS logout
@app.route('/logout_cas', methods=['GET'])
def logout_cas():
    # This route serves the React app to show the LogoutCasPage after CAS redirects back
    return flask.send_file('../frontend/react/index.html')

# Logout app page (no authentication required)
@app.route('/logout_app', methods=['GET'])
def logout_app_page():
    return flask.send_file('../frontend/react/index.html')

# Logout CAS landing page (no authentication required)
@app.route('/logout_cas_landing', methods=['GET'])
def logout_cas_landing_page():
    return flask.send_file('../frontend/react/index.html')

# Endpoint to retrieve search results 
@app.route('/api/search', methods=['GET'])
def search_results():
    
    # Test Restaurant Data
    name = flask.request.args.get('name', '')
    category = flask.request.args.get('category', '')
    restaurants = database.restaurant_search([name, category])

    if not restaurants[0]:
        return flask.jsonify({"error": restaurants[1]}), 400

    return flask.jsonify({"restaurants": restaurants[1]})

# Retrieve restaurant details and menu
@app.route('/api/restaurants/<rest_id>', methods=['GET'])
def restaurant_details(rest_id):
    ok_r, rest = database.load_restaurant_by_id(rest_id)
    if not ok_r:
        return flask.abort(404)

    ok_m, menu = database.load_menu_for_restaurant(rest_id)
    if not ok_m:
        menu = []

    return flask.jsonify({"restaurant": rest, "menu": menu})

# Review endpoints
@app.route('/api/restaurants/<rest_id>/reviews', methods=['GET'])
def get_restaurant_reviews(rest_id):
    ok, reviews = database.get_reviews_by_restaurant(rest_id)
    if not ok:
        return flask.jsonify({"error": reviews}), 400
    return flask.jsonify({"reviews": reviews})

# Create or update a review for a restaurant
@app.route('/api/restaurants/<rest_id>/reviews', methods=['POST'])
def create_review(rest_id):
    auth.authenticate()
    data = flask.request.get_json()
    if not data:
        return flask.jsonify({"error": "No data provided"}), 400
    
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return flask.jsonify({"error": "Rating must be an integer between 1 and 5"}), 400
    
    username = auth.get_username()
    ok, review = database.upsert_review(rest_id, username, rating, comment)
    
    if not ok:
        return flask.jsonify({"error": review}), 400
    
    return flask.jsonify({"review": review}), 201

# Get all reviews by the authenticated user
@app.route('/api/users/reviews', methods=['GET'])
def get_user_reviews():
    auth.authenticate()
    username = auth.get_username()
    ok, reviews = database.get_reviews_by_user(username)
    if not ok:
        return flask.jsonify({"error": reviews}), 400
    return flask.jsonify({"reviews": reviews})

# Delete a review by review ID
@app.route('/api/reviews/<review_id>', methods=['DELETE'])
def delete_user_review(review_id):
    auth.authenticate()
    username = auth.get_username()
    ok, result = database.delete_review(review_id, username)
    if not ok:
        return flask.jsonify({"error": result}), 400
    return flask.jsonify({"message": "Review deleted"}), 200

# @app.route('/protected')
# def protected():
#     # Force CAS authentication (will redirect to CAS if needed)
#     auth.authenticate()
#     return f"Hello {auth.get_username()}! This is protected."

# Example API endpoint that requires authentication
@app.route('/data')
def api_data():
    if not auth.is_authenticated():
        flask.abort(403)
    return flask.jsonify({"user": auth.get_username(), "data": []})

# -------------------- Group Feature API Endpoints --------------------

def _require_auth():
    auth.authenticate()
    return auth.get_username()

@app.route('/api/groups', methods=['GET'])
def list_groups():
    """List groups current user belongs to."""
    username = _require_auth()
    ok, groups = database.list_groups_for_user(username)
    if not ok:
        return flask.jsonify({"error": groups}), 400
    return flask.jsonify({"groups": groups})

@app.route('/api/groups', methods=['POST'])
def create_group():
    """Create a new group; creator becomes leader."""
    username = _require_auth()
    data = flask.request.get_json() or {}
    group_name = data.get('group_name', '').strip()
    selected_restaurant_id = data.get('selected_restaurant_id')
    if not group_name:
        return flask.jsonify({"error": "group_name required"}), 400
    ok, result = database.create_group(group_name, username, selected_restaurant_id)
    if not ok:
        return flask.jsonify({"error": result}), 400
    return flask.jsonify({"group": result}), 201

@app.route('/api/groups/<group_id>', methods=['GET'])
def get_group(group_id):
    username = _require_auth()
    ok, group = database.get_group_with_members(group_id)
    if not ok:
        return flask.jsonify({"error": group}), 404
    # Basic authorization: only members can view
    if username not in [m['netid'] for m in group['members']]:
        return flask.jsonify({"error": "Forbidden"}), 403
    return flask.jsonify({"group": group})

def _is_leader(username, group):
    for m in group['members']:
        if m['netid'] == username and m['role'] == 'leader':
            return True
    return False

@app.route('/api/groups/<group_id>/members', methods=['POST'])
def add_group_member(group_id):
    username = _require_auth()
    data = flask.request.get_json() or {}
    member_netid = data.get('netid', '').strip()
    if not member_netid:
        return flask.jsonify({"error": "netid required"}), 400
    ok, group = database.get_group_with_members(group_id)
    if not ok:
        return flask.jsonify({"error": group}), 404
    if not _is_leader(username, group):
        return flask.jsonify({"error": "Only leaders can add members"}), 403
    ok, err = database.add_member_to_group(group_id, member_netid)
    if not ok:
        return flask.jsonify({"error": err}), 400
    # Return updated group
    ok, updated = database.get_group_with_members(group_id)
    return flask.jsonify({"group": updated}), 200

@app.route('/api/groups/<group_id>/members/<member_netid>', methods=['DELETE'])
def remove_group_member(group_id, member_netid):
    username = _require_auth()
    ok, group = database.get_group_with_members(group_id)
    if not ok:
        return flask.jsonify({"error": group}), 404
    # Prevent removal of leader entirely
    if any(m['netid'] == member_netid and m['role'] == 'leader' for m in group['members']):
        return flask.jsonify({"error": "Cannot remove group leader"}), 400
    # Allow self removal or leader removing others
    if username != member_netid and not _is_leader(username, group):
        return flask.jsonify({"error": "Forbidden"}), 403
    ok, err = database.remove_member_from_group(group_id, member_netid)
    if not ok:
        return flask.jsonify({"error": err}), 400
    ok, updated = database.get_group_with_members(group_id)
    if not ok:
        return flask.jsonify({"error": updated}), 400
    return flask.jsonify({"group": updated}), 200

@app.route('/api/groups/<group_id>/restaurant', methods=['PUT'])
def set_group_restaurant(group_id):
    username = _require_auth()
    data = flask.request.get_json() or {}
    restaurant_id = data.get('restaurant_id')
    if not restaurant_id:
        return flask.jsonify({"error": "restaurant_id required"}), 400
    ok, group = database.get_group_with_members(group_id)
    if not ok:
        return flask.jsonify({"error": group}), 404
    if not _is_leader(username, group):
        return flask.jsonify({"error": "Only leaders can set restaurant"}), 403
    ok, updated = database.update_group_selected_restaurant(group_id, restaurant_id)
    if not ok:
        return flask.jsonify({"error": updated}), 400
    ok, full = database.get_group_with_members(group_id)
    return flask.jsonify({"group": full}), 200

@app.route('/api/users/search', methods=['GET'])
def user_search():
    """Search users by name or NetID (partial match). Requires authentication."""
    _require_auth()
    q = flask.request.args.get('q', '')
    ok, results = database.search_users(q)
    if not ok:
        return flask.jsonify({"error": results}), 400
    return flask.jsonify({"users": results})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)