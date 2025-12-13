import flask
import flask_session
import flask_sqlalchemy
import os
import atexit
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
# Cap SQLAlchemy engine pool size for session store to avoid exceeding DB role limits
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 1,        # keep minimal
    'max_overflow': 0,     # do not exceed pool_size
    'pool_pre_ping': True, # detect stale connections
    'pool_recycle': 1800   # recycle every 30 minutes
}
app.config['SESSION_SQLALCHEMY'] = flask_sqlalchemy.SQLAlchemy(
    app,
    engine_options=app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {})
)
flask_session.Session(app)

# Gracefully close connection pools on app shutdown
def _dispose_pools():
    try:
        # Close psycopg2 pooled connections
        if hasattr(database, 'pool'):
            database.pool.closeall()
    except Exception:
        pass
    try:
        # Dispose SQLAlchemy engine for session store
        sess_db = app.config.get('SESSION_SQLALCHEMY')
        if sess_db is not None and hasattr(sess_db, 'engine'):
            sess_db.engine.dispose()
    except Exception:
        pass

atexit.register(_dispose_pools)

# Test React
@app.route('/', methods=['GET'])
def index():
    return flask.send_file('../frontend/react/index.html')

# Home Page
@app.route('/api/home', methods=['GET'])
def home():
    auth.authenticate()
    restaurants = database.load_all_restaurants()
    firstname = auth.get_firstname()

    username = auth.get_username()
    user_prefs = {}
    try:
        ok_u, user = database.get_user_by_username(username)
        if ok_u and isinstance(user, dict):
            # Normalize keys if present (DB uses favorite_cuisine as array)
            favs = user.get('favorite_cuisine') or user.get('favoriteCuisine') or user.get('favorite_cuisines') or []
            user_prefs = { 'favorite_cuisines': favs or [] }
    except Exception:
        user_prefs = {}

    if restaurants[0] is False:
        return flask.jsonify({"error": restaurants[1]}), 400

    return flask.jsonify({
        "firstname": firstname,
        "restaurants": restaurants[1],
        "preferences": user_prefs
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

# Serve discover page
@app.route('/discover', methods=['GET'])
def discover_page():
    auth.authenticate()
    return flask.send_file('../frontend/react/index.html')

# Serve group page
@app.route('/group', methods=['GET'])
def group_page():
    auth.authenticate()
    return flask.send_file('../frontend/react/index.html')

# Serve individual restaurant page (client-side route)
@app.route('/restaurants/<rest_id>', methods=['GET'])
def restaurant_page(rest_id):
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

# Retrieve restaurant details and menu (JSON API)
@app.route('/api/restaurants/<rest_id>', methods=['GET'])
def restaurant_details(rest_id):
    ok_r, rest = database.load_restaurant_by_id(rest_id)
    if not ok_r:
        return flask.abort(404)

    ok_m, menu = database.load_menu_for_restaurant(rest_id)
    if not ok_m:
        menu = []

    return flask.jsonify({"restaurant": rest, "menu": menu})

@app.route('/back_office/restaurants/<rest_id>', methods=['GET'])
def back_office_restaurant_page(rest_id):
    auth.authenticate()
    ok, admin = database.get_admin_status(auth.get_username())
    if not ok:
        return flask.jsonify({"error": admin}), 400
    if not admin:
        return flask.abort(403)
    return flask.send_file('../frontend/react/index.html')


# Review endpoints

@app.route('/api/reviews', methods=['GET'])
def get_all_reviews():
    ok, reviews = database.get_all_reviews()
    if not ok:
        return flask.jsonify({"error": reviews}), 400
    return flask.jsonify({"reviews": reviews})

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
    # Enforce comment length limit
    if not isinstance(comment, str):
        comment = str(comment) if comment is not None else ''
    MAX_COMMENT_LEN = 500
    if len(comment) > MAX_COMMENT_LEN:
        return flask.jsonify({"error": f"Comment must be at most {MAX_COMMENT_LEN} characters"}), 400
    
    username = auth.get_username()
    ok, review = database.upsert_review(rest_id, username, rating, comment)
    
    if not ok:
        return flask.jsonify({"error": review}), 400
    
    return flask.jsonify({"review": review}), 201

# Feedback Endpoints
@app.route('/api/restaurants/<rest_id>/feedback', methods=['GET'])
def get_restaurant_feedback(rest_id):
    ok, feedback = database.get_feedback_by_restaurant(rest_id)
    if not ok:
        return flask.jsonify({"error": feedback}), 400
    return flask.jsonify({"reviews": feedback})


@app.route('/api/restaurants/<rest_id>/feedback', methods=['POST'])
def submit_feedback(rest_id): 
    auth.authenticate()
    data = flask.request.get_json()
    if not data:
        return flask.jsonify({"error": "No data provided"}), 400
    
    response = data.get('response', '')
    
    if not response or not isinstance(response, str) or len(response.strip()) == 0:
        return flask.jsonify({"error": "Comment must be a non-empty string"}), 400
    
    username = auth.get_username()
    ok, feedback = database.submit_feedback(rest_id, username, response)
    
    if not ok:
        return flask.jsonify({"error": feedback}), 400
    
    return flask.jsonify({"feedback": feedback}), 201

# Check if this user is a TB admin
@app.route('/api/users/admin_status', methods=['GET'])
def get_admin_status():
    auth.authenticate()
    username = auth.get_username()
    ok, is_admin = database.get_admin_status(username)
    if not ok:
        return flask.jsonify({"error": is_admin}), 400
    return flask.jsonify({"is_admin": is_admin})

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
    # Admins can delete any review; normal users can delete only their own
    ok_admin, is_admin = database.get_admin_status(username)
    if ok_admin and is_admin:
        ok, result = database.delete_review_force(review_id)
    else:
        ok, result = database.delete_review(review_id, username)
    if not ok:
        # Use 403 for unauthorized/ownership issues
        status = 403 if 'unauthorized' in str(result).lower() else 400
        return flask.jsonify({"error": result}), status
    return flask.jsonify({"message": "Review deleted"}), 200

@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    auth.authenticate()
    ok, responses = database.get_all_feedback()
    if not ok:
        return flask.jsonify({"error": responses}), 400
    return flask.jsonify({"responses": responses})

@app.route('/api/feedback/<feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    auth.authenticate()
    username = auth.get_username()
    # Only admins can delete feedback from Back Office
    ok_admin, is_admin = database.get_admin_status(username)
    if not (ok_admin and is_admin):
        return flask.jsonify({"error": "Forbidden"}), 403
    ok, result = database.delete_feedback(feedback_id)
    if not ok:
        return flask.jsonify({"error": result}), 400
    return flask.jsonify({"message": "Feedback deleted"}), 200

@app.route('/back_office', methods=['GET'])
def back_office():
    # Force CAS authentication (will redirect to CAS if needed)
    auth.authenticate()
    ok, admin = database.get_admin_status(auth.get_username())
    if not ok:
        return flask.jsonify({"error": admin}), 400
    if not admin:
        return flask.abort(403)
    return flask.send_file('../frontend/react/index.html')

@app.route('/back_office/feedback', methods=['GET'])
def back_office_feedback():
    auth.authenticate()
    ok, admin = database.get_admin_status(auth.get_username())
    if not ok:
        return flask.jsonify({"error": admin}), 400
    if not admin:
        return flask.abort(403)
    return flask.send_file('../frontend/react/index.html')

@app.route('/back_office/reviews', methods=['GET'])
def back_office_reviews():
    auth.authenticate()
    ok, admin = database.get_admin_status(auth.get_username())
    if not ok:
        return flask.jsonify({"error": admin}), 400
    if not admin:
        return flask.abort(403)
    return flask.send_file('../frontend/react/index.html')

@app.route('/api/reviews/<review_id>/admin_delete', methods=['DELETE'])
def admin_delete_review(review_id):
    auth.authenticate()
    ok, admin = database.get_admin_status(auth.get_username())
    if not ok:
        return flask.jsonify({"error": admin}), 400
    if not admin:
        return flask.abort(403)
    
    ok, result = database.delete_review_force(review_id)
    if not ok:
        return flask.jsonify({"error": result}), 400
    return flask.jsonify({"message": "Review deleted"}), 200
    


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
    # Any member can add other members; ensure the requester is in the group
    if username not in [m['netid'] for m in group['members']]:
        return flask.jsonify({"error": "Only group members can add"}), 403
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
    # Allow any member to remove others (including self), but block non-members
    if username not in [m['netid'] for m in group['members']]:
        return flask.jsonify({"error": "Only group members can remove"}), 403
    ok, err = database.remove_member_from_group(group_id, member_netid)
    if not ok:
        return flask.jsonify({"error": err}), 400
    ok, updated = database.get_group_with_members(group_id)
    if not ok:
        return flask.jsonify({"error": updated}), 400
    return flask.jsonify({"group": updated}), 200

@app.route('/api/groups/<group_id>', methods=['DELETE'])
def delete_group_api(group_id):
    """Delete a group. Any member can delete; prevents 404 for non-members with proper auth check."""
    username = _require_auth()
    ok, group = database.get_group_with_members(group_id)
    if not ok:
        return flask.jsonify({"error": group}), 404
    if username not in [m['netid'] for m in group['members']]:
        return flask.jsonify({"error": "Only group members can delete"}), 403
    ok2, msg = database.delete_group(group_id)
    if not ok2:
        return flask.jsonify({"error": msg}), 400
    return flask.jsonify({"message": "Group deleted"}), 200

@app.route('/api/groups/<group_id>/restaurant', methods=['PUT'])
def set_group_restaurant(group_id):
    username = _require_auth()
    data = flask.request.get_json() or {}
    restaurant_id = data.get('restaurant_id')
    # Allow None to clear selection, but require key in request
    if 'restaurant_id' not in data:
        return flask.jsonify({"error": "restaurant_id required"}), 400
    ok, group = database.get_group_with_members(group_id)
    if not ok:
        return flask.jsonify({"error": group}), 404
    # Any member can set restaurant; ensure requester is in the group
    if username not in [m['netid'] for m in group['members']]:
        return flask.jsonify({"error": "Only group members can set restaurant"}), 403
    ok, updated = database.update_group_selected_restaurant(group_id, restaurant_id)
    if not ok:
        return flask.jsonify({"error": updated}), 400
    ok, full = database.get_group_with_members(group_id)
    return flask.jsonify({"group": full}), 200

@app.route('/api/groups/<group_id>/meal', methods=['PUT'])
def set_group_meal(group_id):
    """Set or clear the group's scheduled meal datetime. Any group member can update it.
    Body: {"scheduled_meal_at": "YYYY-MM-DDTHH:MM"} or null to clear.
    """
    username = _require_auth()
    payload = flask.request.get_json(silent=True) or {}
    # scheduled_meal_at as ISO local string (datetime-local) or None
    scheduled = payload.get('scheduled_meal_at', None)
    # Verify membership
    ok, group = database.get_group_with_members(group_id)
    if not ok:
        return flask.jsonify({"error": group}), 404
    if username not in [m['netid'] for m in group['members']]:
        return flask.jsonify({"error": "Only group members can update meal time"}), 403
    # Normalize only naive local input to UTC; if input already includes timezone (ends with 'Z' or contains offset), trust it
    if isinstance(scheduled, str) and scheduled:
        has_tz = scheduled.endswith('Z') or ('+' in scheduled[10:] or '-' in scheduled[10:])
        if not has_tz:
            try:
                from datetime import datetime
                from zoneinfo import ZoneInfo
                # Treat naive string as America/New_York local time
                dt_local = datetime.fromisoformat(scheduled)
                dt_local = dt_local.replace(tzinfo=ZoneInfo('America/New_York'))
                dt_utc = dt_local.astimezone(ZoneInfo('UTC'))
                scheduled = dt_utc.isoformat()
            except Exception:
                # If parsing fails, leave as-is
                pass
    ok2, updated = database.update_group_meal_time(group_id, scheduled)
    if not ok2:
        return flask.jsonify({"error": updated}), 400
    # Return full group details to refresh client state
    ok3, full = database.get_group_with_members(group_id)
    if not ok3:
        return flask.jsonify({"error": full}), 400
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

@app.route('/api/cuisines', methods=['GET'])
def get_cuisines():
    """Get list of available cuisine types from restaurants database."""
    auth.authenticate()
    ok, cuisines = database.get_available_cuisines()
    if not ok:
        return flask.jsonify({"error": cuisines}), 400
    return flask.jsonify({"cuisines": cuisines})

@app.route('/api/groups/<group_id>/preferences', methods=['GET'])
def get_group_preferences(group_id):
    """Get aggregated preferences (recommended cuisines, dietary restrictions) for a group."""
    username = _require_auth()
    # Verify membership
    ok, group = database.get_group_with_members(group_id)
    if not ok:
        return flask.jsonify({"error": group}), 404
    if username not in [m['netid'] for m in group['members']]:
        return flask.jsonify({"error": "Forbidden"}), 403
    
    ok, prefs = database.get_group_preferences(group_id)
    if not ok:
        return flask.jsonify({"error": prefs}), 400
    return flask.jsonify({"preferences": prefs})

# Back Office Api Routes ----------------
@app.route('/api/restaurants/<rest_id>/update', methods=['PUT'])
def update_restaurant(rest_id):
    username = _require_auth()
    data = flask.request.get_json()
    data = data.get('editedRestaurant')
    print(data)
    
    ok, result = database.update_restaurant(data)
    if not ok:
        return flask.jsonify({"error": result}), 400
    return flask.jsonify({"group": result}), 201

@app.route('/api/restaurants/<rest_id>/menu/update', methods=['PUT'])
def update_restaurant_menu(rest_id):
    """Back Office: Update menu items for a restaurant."""
    username = _require_auth()
    # Ensure user is admin
    ok_admin, is_admin = database.get_admin_status(username)
    if not ok_admin or not is_admin:
        return flask.jsonify({"error": "Forbidden"}), 403

    payload = flask.request.get_json() or {}
    items = payload.get('items', [])
    ok, updated_count = database.update_menu_items(rest_id, items)
    if not ok:
        return flask.jsonify({"error": updated_count}), 400
    return flask.jsonify({"updated": updated_count}), 200

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)