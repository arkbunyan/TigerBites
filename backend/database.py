import sys
import os
import contextlib
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool

load_dotenv()
# Read-only access for the web app layer (Postgres)
DATABASE_URL = os.getenv("TB_DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "Environment variable TB_DATABASE_URL is not set. "
        "Set it to a valid Postgres URL (eg. postgresql://user:pass@host:port/db)."
    )

# Initialize a global connection pool for Postgres connections
# Keep maxconn within hosting/database limits
pool = SimpleConnectionPool(
    minconn=1,
    maxconn=2,  # ultra-conservative to respect role limits
    dsn=DATABASE_URL
)
def _err_response(ex):
    error_message = str(sys.argv[0] + ': ')
    print(f"{error_message} {str(ex)}", file=sys.stderr)
    return [False, 'A server error occurred. Please contact the system administrator.']

def _get_conn():
    """Borrow a connection from the pool."""
    return pool.getconn()

def _put_conn(conn):
    """Return a connection to the pool."""
    if conn is not None:
        pool.putconn(conn)

def load_all_restaurants():
    """
    Return all restaurants with id, name, category, hours, avg_price.
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = "SELECT * FROM restaurants"
                cursor.execute(sql)
                rows = cursor.fetchall()

                response = []
                for row in rows:
                    entry = {
                        'id': row.get('id'),
                        'created_at': row.get('created_at').isoformat(),
                        'name': row.get('name'),
                        'description': row.get('description'), 
                        'location': row.get('location'), 
                        'category': row.get('category'), 
                        'hours': row.get('hours'), 
                        'avg_price': float(row.get('avg_price')) if row.get('avg_price') is not None else None, 
                        'latitude': row.get('latitude'),
                        'longitude': row.get('longitude'),
                        'picture': row.get('picture'),
                        'yelp_rating': float(row.get('yelp_rating')) if row.get('yelp_rating') is not None else None,
                        'website_url': row.get('website_url')
                    }
                    response.append(entry)
                return [True, response]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def restaurant_search(params):
    """
    Search by name and category. Both are substring matches.
    params = [name, category]
    """
    name = params[0] if len(params) > 0 else ''
    category = params[1] if len(params) > 1 else ''

    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Use ILIKE for case-insensitive substring match in Postgres
                sql = (
                    "SELECT * "
                    "FROM restaurants "
                    "WHERE name ILIKE %s AND category ILIKE %s "
                    "ORDER BY name ASC"
                )
                cursor.execute(sql, (f"%{name}%", f"%{category}%"))
                rows = cursor.fetchall()

                response = []
                for row in rows:
                    entry = {
                        'id': row.get('id'),
                        'created_at': row['created_at'].isoformat(),
                        'name': row['name'],
                        'description': row['description'],
                        'location': row['location'],
                        'category': row.get('category'), 
                        'hours': row.get('hours'), 
                        'avg_price': float(row.get('avg_price')) if row['avg_price'] is not None else None,
                        'latitude': row.get('latitude'),
                        'longitude': row.get('longitude'),
                        'picture': row.get('picture'),
                        'yelp_rating': float(row.get('yelp_rating')) if row.get('yelp_rating') is not None else None,
                        'website_url': row.get('website_url')
                    }
                    response.append(entry)
                return [True, response]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def load_restaurant_by_id(rest_id):
    # return one restaurant dict by id.
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = "SELECT * FROM restaurants WHERE id = %s"
                cursor.execute(sql, (rest_id,))
                row = cursor.fetchone()
                if not row:
                    return [False, 'Not found']

                data = {
                    'id': row.get('id'), 
                    'created_at': row.get('created_at').isoformat(),
                    'name': row.get('name'),
                    'description': row.get('description'), 
                    'location': row.get('location'), 
                    'category': row.get('category'), 
                    'hours': row.get('hours'), 
                    'avg_price': float(row.get('avg_price')) if row['avg_price'] is not None else None,
                    'latitude': row.get('latitude'),
                    'longitude': row.get('longitude'),
                    'picture': row.get('picture'),
                    'yelp_rating': float(row.get('yelp_rating')) if row.get('yelp_rating') is not None else None,
                    'website_url': row.get('website_url')
                }
                return [True, data]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def load_menu_for_restaurant(rest_id):
    """
    Return list of menu items for a restaurant id.
    Each item has: name, description, price_cents, price (formatted or None)
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = (
                    "SELECT id, restaurant_id, name, description, avg_price "
                    "FROM menu_items WHERE restaurant_id = %s "
                    "ORDER BY name ASC"
                )
                cursor.execute(sql, (rest_id,))
                rows = cursor.fetchall()

                items = []
                for row in rows:
                    items.append({
                        'id': str(row.get('id')) if row.get('id') is not None else None,
                        'restaurant_id': str(row.get('restaurant_id')) if row.get('restaurant_id') is not None else None,
                        'name': row.get('name'),
                        'description': row.get('description'), 
                        'price': float(row.get('avg_price')) if row.get('avg_price') is not None else None,
                    })

                return [True, items]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)
    
def update_restaurant(restaurant):
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = """
                UPDATE restaurants
                SET
                    avg_price = %s,
                    category = %s,
                    description = %s,
                    hours = %s,
                    latitude = %s,
                    location = %s,
                    longitude = %s,
                    name = %s,
                    picture = %s,
                    yelp_rating = %s 
                WHERE id = %s
                RETURNING *;
                """

                values = (
                    restaurant.get('avg_price'),
                    restaurant.get('category'),
                    restaurant.get('description'),
                    restaurant.get('hours'),
                    restaurant.get('latitude'),
                    restaurant.get('location'),
                    restaurant.get('longitude'),
                    restaurant.get('name'),
                    restaurant.get('picture'),
                    restaurant.get('yelp_rating'),
                    # restaurant.get('website_url'),
                    restaurant.get('id')
                )

                cursor.execute(sql, values)
                updated_restaurant = cursor.fetchone()
                conn.commit()
                return [True, dict(updated_restaurant)]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def update_menu_items(restaurant_id, items):
    """Update menu items for a restaurant. Supports updating name, description, and price.
    Items should be a list of dicts: {id, name, description, price}.
    Returns [True, updated_count] or [False, error_msg]."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                updated = 0
                for item in items or []:
                    # Determine price column name in DB (assuming 'avg_price' per existing select)
                    cursor.execute(
                        """
                        UPDATE public.menu_items
                        SET name = %s,
                            description = %s,
                            avg_price = %s
                        WHERE id = %s AND restaurant_id = %s
                        RETURNING id
                        """,
                        (
                            item.get('name'),
                            item.get('description'),
                            item.get('price'),
                            item.get('id'),
                            restaurant_id,
                        ),
                    )
                    if cursor.fetchone():
                        updated += 1
                conn.commit()
                return [True, updated]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def upsert_user(username, email, firstname, fullname):
    """
    Insert or update a user record with CAS login info.
    Username is stored as 'netid'. Returns [True, user_data] or [False, error_msg].
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = """
                INSERT INTO public.users (netid, email, firstname, fullname)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (netid) DO UPDATE
                SET email = EXCLUDED.email, 
                    firstname = EXCLUDED.firstname, 
                    fullname = EXCLUDED.fullname
                RETURNING id, netid, email, firstname, fullname, favorite_cuisine, allergies, dietary_restrictions
                """
                print(f"DEBUG upsert_user: Executing SQL with values - netid: {username}, email: {email}, firstname: {firstname}, fullname: {fullname}")
                cursor.execute(sql, (username, email, firstname, fullname))
                row = cursor.fetchone()
                print(f"DEBUG upsert_user: Query result row: {row}")
                conn.commit()
                
                if row:
                    user_dict = dict(row)
                    # Convert PostgreSQL arrays to Python lists
                    if user_dict.get('favorite_cuisine'):
                        user_dict['favorite_cuisine'] = list(user_dict['favorite_cuisine'])
                    else:
                        user_dict['favorite_cuisine'] = []
                    if user_dict.get('allergies'):
                        user_dict['allergies'] = list(user_dict['allergies'])
                    else:
                        user_dict['allergies'] = []
                    if user_dict.get('dietary_restrictions'):
                        user_dict['dietary_restrictions'] = list(user_dict['dietary_restrictions'])
                    else:
                        user_dict['dietary_restrictions'] = []
                    return [True, user_dict]
                return [False, 'Failed to insert/update user']
        finally:
            _put_conn(conn)
    except Exception as ex:
        print(f"DEBUG upsert_user: Exception occurred: {ex}")
        return _err_response(ex)

def get_user_by_username(username):
    """
    Retrieve a user record by netid (username).
    Returns [True, user_data] or [False, error_msg].
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = "SELECT id, netid, email, firstname, fullname, favorite_cuisine, allergies, dietary_restrictions, admin_status FROM public.users WHERE netid = %s"
                cursor.execute(sql, (username,))
                row = cursor.fetchone()
                
                if row:
                    user_dict = dict(row)
                    # Convert PostgreSQL arrays to Python lists
                    if user_dict.get('favorite_cuisine'):
                        user_dict['favorite_cuisine'] = list(user_dict['favorite_cuisine'])
                    else:
                        user_dict['favorite_cuisine'] = []
                    if user_dict.get('allergies'):
                        user_dict['allergies'] = list(user_dict['allergies'])
                    else:
                        user_dict['allergies'] = []
                    if user_dict.get('dietary_restrictions'):
                        user_dict['dietary_restrictions'] = list(user_dict['dietary_restrictions'])
                    else:
                        user_dict['dietary_restrictions'] = []
                    return [True, user_dict]
                return [False, 'User not found']
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def update_favorite_cuisine(username, favorite_cuisine):
    """
    Update a user's favorite cuisines by netid (username).
    favorite_cuisine can be a list (for arrays) or a single string.
    Returns [True, user_data] or [False, error_msg].
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # If favorite_cuisine is a list, use it as-is; otherwise convert to list
                if isinstance(favorite_cuisine, list):
                    cuisine_array = favorite_cuisine
                else:
                    cuisine_array = [favorite_cuisine] if favorite_cuisine else []
                
                sql = """
                UPDATE public.users 
                SET favorite_cuisine = %s
                WHERE netid = %s
                RETURNING id, netid, email, firstname, fullname, favorite_cuisine, allergies, dietary_restrictions
                """
                cursor.execute(sql, (cuisine_array, username))
                row = cursor.fetchone()
                conn.commit()
                
                if row:
                    user_dict = dict(row)
                    # Convert PostgreSQL arrays to Python lists
                    if user_dict.get('favorite_cuisine'):
                        user_dict['favorite_cuisine'] = list(user_dict['favorite_cuisine'])
                    else:
                        user_dict['favorite_cuisine'] = []
                    if user_dict.get('allergies'):
                        user_dict['allergies'] = list(user_dict['allergies'])
                    else:
                        user_dict['allergies'] = []
                    if user_dict.get('dietary_restrictions'):
                        user_dict['dietary_restrictions'] = list(user_dict['dietary_restrictions']) 
                    else:
                        user_dict['dietary_restrictions'] = []
                    return [True, user_dict]
                return [False, 'User not found']
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def update_allergies(username, allergies):
    """
    Update a user's allergies by netid (username).
    allergies can be a list (for arrays) or a single string.
    Returns [True, user_data] or [False, error_msg].
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # If allergies is a list, use it as-is; otherwise convert to list
                if isinstance(allergies, list):
                    allergies_array = allergies
                else:
                    allergies_array = [allergies] if allergies else []
                
                sql = """
                UPDATE public.users 
                SET allergies = %s
                WHERE netid = %s
                RETURNING id, netid, email, firstname, fullname, favorite_cuisine, allergies, dietary_restrictions
                """
                cursor.execute(sql, (allergies_array, username))
                row = cursor.fetchone()
                conn.commit()
                
                if row:
                    user_dict = dict(row)
                    # Convert PostgreSQL arrays to Python lists
                    if user_dict.get('favorite_cuisine'):
                        user_dict['favorite_cuisine'] = list(user_dict['favorite_cuisine'])
                    else:
                        user_dict['favorite_cuisine'] = []
                    if user_dict.get('allergies'):
                        user_dict['allergies'] = list(user_dict['allergies'])
                    else:
                        user_dict['allergies'] = []
                    if user_dict.get('dietary_restrictions'):       
                        user_dict['dietary_restrictions'] = list(user_dict['dietary_restrictions']) 
                    else:
                        user_dict['dietary_restrictions'] = []
                    return [True, user_dict]
                return [False, 'User not found']
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def update_dietary_restrictions(username, dietary_restrictions):
    """
    Update a user's dietary restrictions by netid (username).
    dietary_restrictions can be a list (for arrays) or a single string.
    Returns [True, user_data] or [False, error_msg].
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # If dietary_restrictions is a list, use it as-is; otherwise convert to list
                if isinstance(dietary_restrictions, list):
                    dietary_restrictions_array = dietary_restrictions
                else:
                    dietary_restrictions_array = [dietary_restrictions] if dietary_restrictions else []

                sql = """
                UPDATE public.users 
                SET dietary_restrictions = %s
                WHERE netid = %s
                RETURNING id, netid, email, firstname, fullname, favorite_cuisine, allergies, dietary_restrictions
                """
                cursor.execute(sql, (dietary_restrictions_array, username))
                row = cursor.fetchone()
                conn.commit()
                
                if row:
                    user_dict = dict(row)
                    # Convert PostgreSQL arrays to Python lists
                    if user_dict.get('favorite_cuisine'):
                        user_dict['favorite_cuisine'] = list(user_dict['favorite_cuisine'])
                    else:
                        user_dict['favorite_cuisine'] = []
                    if user_dict.get('allergies'):
                        user_dict['allergies'] = list(user_dict['allergies'])
                    else:
                        user_dict['allergies'] = []
                    if user_dict.get('dietary_restrictions'):       
                        user_dict['dietary_restrictions'] = list(user_dict['dietary_restrictions']) 
                    else:
                        user_dict['dietary_restrictions'] = []
                    return [True, user_dict]
                return [False, 'User not found']
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)
    
def upsert_review(rest_id, username, rating, comment):
    """
    Insert or update a review for a restaurant by a user.
    Gets user_id from username (netid), then inserts/updates review.
    Returns [True, review_data] or [False, error_msg].
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # First get the user_id from netid
                cursor.execute("SELECT id FROM public.users WHERE netid = %s", (username,))
                user_row = cursor.fetchone()
                if not user_row:
                    return [False, 'User not found']
                
                user_id = user_row['id']
                
                # Insert or update the review
                sql = """
                INSERT INTO public.reviews (restaurant_id, user_id, rating, comment)
                VALUES (%s, %s, %s, %s)
                RETURNING id, restaurant_id, user_id, rating, comment, created_at
                """
                cursor.execute(sql, (rest_id, user_id, rating, comment))
                row = cursor.fetchone()
                conn.commit()
                
                if row:
                    review_data = dict(row)
                    review_data['created_at'] = review_data['created_at'].isoformat()
                    review_data['user_id'] = str(review_data['user_id'])
                    review_data['restaurant_id'] = str(review_data['restaurant_id'])
                    review_data['id'] = str(review_data['id'])
                    return [True, review_data]
                return [False, 'Failed to insert review']
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)
    
def get_all_reviews():  
    """Get all reviews with user and restaurant info."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = """
                SELECT r.id, r.restaurant_id, r.rating, r.comment, r.created_at,
                       u.netid as username, u.firstname, u.fullname,
                       rest.name as restaurant_name, rest.category
                FROM public.reviews r
                JOIN public.users u ON r.user_id = u.id
                JOIN public.restaurants rest ON r.restaurant_id = rest.id
                ORDER BY r.created_at DESC
                """
                cursor.execute(sql)
                rows = cursor.fetchall()
                
                reviews = []
                for row in rows:
                    review = dict(row)
                    review['created_at'] = review['created_at'].isoformat()
                    review['id'] = str(review['id'])
                    review['restaurant_id'] = str(review['restaurant_id'])
                    reviews.append(review)
            
                return [True, reviews]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def get_reviews_by_restaurant(rest_id):
    """
    Get all reviews for a specific restaurant with user info.
    Returns [True, reviews_list] or [False, error_msg].
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = """
                SELECT r.id, r.restaurant_id, r.rating, r.comment, r.created_at,
                       u.netid as username, u.firstname, u.fullname
                FROM public.reviews r
                JOIN public.users u ON r.user_id = u.id
                WHERE r.restaurant_id = %s
                ORDER BY r.created_at DESC
                """
                cursor.execute(sql, (rest_id,))
                rows = cursor.fetchall()
                
                reviews = []
                for row in rows:
                    review = dict(row)
                    review['created_at'] = review['created_at'].isoformat()
                    review['id'] = str(review['id'])
                    review['restaurant_id'] = str(review['restaurant_id'])
                    reviews.append(review)
                
                return [True, reviews]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def get_reviews_by_user(username):
    """
    Get all reviews by a specific user (by netid) with restaurant info.
    Returns [True, reviews_list] or [False, error_msg].
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = """
                SELECT r.id, r.restaurant_id, r.rating, r.comment, r.created_at,
                       rest.name as restaurant_name, rest.category
                FROM public.reviews r
                JOIN public.users u ON r.user_id = u.id
                JOIN public.restaurants rest ON r.restaurant_id = rest.id
                WHERE u.netid = %s
                ORDER BY r.created_at DESC
                """
                cursor.execute(sql, (username,))
                rows = cursor.fetchall()
                
                reviews = []
                for row in rows:
                    review = dict(row)
                    review['created_at'] = review['created_at'].isoformat()
                    review['id'] = str(review['id'])
                    review['restaurant_id'] = str(review['restaurant_id'])
                    reviews.append(review)
                
                return [True, reviews]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def delete_review(review_id, username):
    """
    Delete a review by id, but only if it belongs to the given user.
    Returns [True, None] or [False, error_msg].
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = """
                DELETE FROM public.reviews r
                USING public.users u
                WHERE r.id = %s AND r.user_id = u.id AND u.netid = %s
                RETURNING r.id
                """
                cursor.execute(sql, (review_id, username))
                row = cursor.fetchone()
                conn.commit()
                
                if row:
                    return [True, None]
                return [False, 'Review not found or unauthorized']
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)
    
def delete_review_force(review_id):
    """Delete a review by id (admin only)."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = """
                DELETE FROM public.reviews
                WHERE id = %s
                RETURNING id
                """
                cursor.execute(sql, (review_id,))
                row = cursor.fetchone()
                conn.commit()
                
                if row:
                    return [True, None]
                return [False, 'Review not found']
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)
    

def get_all_feedback():
    """Retrieve all feedback entries with user info."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = """
                SELECT f.id, f.created_at, f.restaurant_id, f.user_id, f.response,
                       u.netid as username, u.firstname, u.fullname
                FROM public.feedback f
                JOIN public.users u ON f.user_id = u.id
                ORDER BY f.created_at DESC
                """
                cursor.execute(sql)
                rows = cursor.fetchall()
                
                feedback_list = []
                for row in rows:
                    feedback = dict(row)
                    feedback['created_at'] = feedback['created_at'].isoformat()
                    feedback['id'] = str(feedback['id'])
                    feedback_list.append(feedback)
                
                return [True, feedback_list]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)
    
def get_feedback_by_restaurant(rest_id):   
    """Retrieve feedback entries for a specific restaurant."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = """
                SELECT f.id, f.created_at, f.restaurant_id, f.user_id, f.response,
                       u.netid as username, u.firstname, u.fullname
                FROM public.feedback f
                JOIN public.users u ON f.user_id = u.id
                WHERE f.restaurant_id = %s
                ORDER BY f.created_at DESC
                """
                cursor.execute(sql, (rest_id,))
                rows = cursor.fetchall()
                
                feedback_list = []
                for row in rows:
                    feedback = dict(row)
                    feedback['created_at'] = feedback['created_at'].isoformat()
                    feedback['id'] = str(feedback['id'])
                    feedback_list.append(feedback)
                
                return [True, feedback_list]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)
    
def submit_feedback(rest_id, username, response):
    """Submit feedback for a restaurant by a user."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # First get the user_id from netid
                cursor.execute("SELECT id FROM public.users WHERE netid = %s", (username,))
                user_row = cursor.fetchone()
                if not user_row:
                    return [False, 'User not found']
                
                user_id = user_row['id']
                
                # Insert the feedback
                sql = """
                INSERT INTO public.feedback (restaurant_id, user_id, response)
                VALUES (%s, %s, %s)
                RETURNING id, created_at, restaurant_id, user_id, response
                """
                cursor.execute(sql, (rest_id, user_id, response))
                row = cursor.fetchone()
                conn.commit()
                
                if row:
                    feedback_data = dict(row)
                    feedback_data['created_at'] = feedback_data['created_at'].isoformat()
                    feedback_data['user_id'] = str(feedback_data['user_id'])
                    feedback_data['restaurant_id'] = str(feedback_data['restaurant_id'])
                    feedback_data['id'] = str(feedback_data['id'])
                    return [True, feedback_data]
                return [False, 'Failed to submit feedback']
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)
    

def delete_feedback(feedback_id):
    """Delete feedback by id, even if it belongs to another user (admin feature)"""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = """
                DELETE FROM public.feedback f
                USING public.users u
                WHERE f.id = %s 
                RETURNING f.id
                """
                cursor.execute(sql, (feedback_id, ))
                row = cursor.fetchone()
                conn.commit()
                
                if row:
                    return [True, None]
                return [False, 'Feedback not found or unauthorized']
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def create_group(group_name, creator_netid, selected_restaurant_id=None):
    """Create a new group and add creator (netid) as leader."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Validate creator exists
                cursor.execute("SELECT netid FROM users WHERE netid = %s", (creator_netid,))
                if cursor.fetchone() is None:
                    return [False, 'Creator user not found']
                # Restaurant validation
                if selected_restaurant_id is not None:
                    cursor.execute("SELECT id FROM restaurants WHERE id = %s", (selected_restaurant_id,))
                    if cursor.fetchone() is None:
                        return [False, 'Selected restaurant not found']
                cursor.execute(
                    """
                    INSERT INTO groups (group_name, creator_netid, selected_restaurant_id)
                    VALUES (%s, %s, %s)
                    RETURNING id, group_name, creator_netid, selected_restaurant_id, created_at, scheduled_meal_at
                    """,
                    (group_name, creator_netid, selected_restaurant_id)
                )
                g_row = cursor.fetchone()
                # Add creator as leader member
                cursor.execute(
                    """
                    INSERT INTO group_members (group_id, user_netid, role)
                    VALUES (%s, %s, 'leader')
                    ON CONFLICT (group_id, user_netid) DO NOTHING
                    """,
                    (g_row['id'], creator_netid)
                )
                conn.commit()
                data = dict(g_row)
                data['id'] = str(data['id'])
                data['created_at'] = data['created_at'].isoformat()
                if data.get('scheduled_meal_at'):
                    data['scheduled_meal_at'] = data['scheduled_meal_at'].isoformat()
                return [True, data]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def add_member_to_group(group_id, member_netid):
    """Add user by netid to group."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT netid FROM users WHERE netid = %s", (member_netid,))
                if cursor.fetchone() is None:
                    return [False, 'User not found']
                cursor.execute("SELECT id FROM groups WHERE id = %s", (group_id,))
                if cursor.fetchone() is None:
                    return [False, 'Group not found']
                cursor.execute(
                    """
                    INSERT INTO group_members (group_id, user_netid, role)
                    VALUES (%s, %s, 'member')
                    ON CONFLICT (group_id, user_netid) DO NOTHING
                    """,
                    (group_id, member_netid)
                )
                conn.commit()
                return [True, None]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def remove_member_from_group(group_id, member_netid):
    """Remove member by netid."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    "DELETE FROM group_members WHERE group_id = %s AND user_netid = %s RETURNING group_id",
                    (group_id, member_netid)
                )
                del_row = cursor.fetchone()
                conn.commit()
                if del_row:
                    return [True, None]
                return [False, 'Membership not found']
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def delete_group(group_id):
    """Delete a group and its memberships. Also clears any dependent references like selected_restaurant_id.
    Returns [True, 'deleted'] or [False, error].
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor() as cursor:
                # Ensure group exists
                cursor.execute("SELECT 1 FROM groups WHERE id = %s", (group_id,))
                exists = cursor.fetchone()
                if not exists:
                    return [False, 'Group not found']
                # Delete memberships first due to FK constraints
                cursor.execute("DELETE FROM group_members WHERE group_id = %s", (group_id,))
                # Delete the group row
                cursor.execute("DELETE FROM groups WHERE id = %s", (group_id,))
                conn.commit()
                return [True, 'deleted']
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def update_group_selected_restaurant(group_id, restaurant_id):
    """Update the selected restaurant for a group with option to clear the selection."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Validate restaurant if not None
                if restaurant_id is not None:
                    cursor.execute("SELECT id FROM restaurants WHERE id = %s", (restaurant_id,))
                    if cursor.fetchone() is None:
                        return [False, 'Restaurant not found']
                
                cursor.execute(
                    "UPDATE groups SET selected_restaurant_id = %s WHERE id = %s RETURNING id, group_name, creator_netid, selected_restaurant_id, created_at, scheduled_meal_at",
                    (restaurant_id, group_id)
                )
                row = cursor.fetchone()
                conn.commit()
                if not row:
                    return [False, 'Group not found']
                data = dict(row)
                data['id'] = str(data['id'])
                data['created_at'] = data['created_at'].isoformat()
                if data.get('scheduled_meal_at'):
                    data['scheduled_meal_at'] = data['scheduled_meal_at'].isoformat()
                return [True, data]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def get_group_with_members(group_id):
    """Return group details plus member list."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT g.id, g.group_name, g.creator_netid, g.selected_restaurant_id, g.created_at, g.scheduled_meal_at,
                           r.name AS restaurant_name
                    FROM groups g
                    LEFT JOIN restaurants r ON g.selected_restaurant_id = r.id
                    WHERE g.id = %s
                """, (group_id,))
                g_row = cursor.fetchone()
                if not g_row:
                    return [False, 'Group not found']
                cursor.execute("""
                    SELECT gm.user_netid AS netid, gm.role, gm.joined_at, u.firstname, u.fullname
                    FROM group_members gm
                    JOIN users u ON gm.user_netid = u.netid
                    WHERE gm.group_id = %s
                    ORDER BY gm.joined_at ASC
                """, (group_id,))
                members_rows = cursor.fetchall()
                members = []
                for mr in members_rows:
                    md = dict(mr)
                    md['joined_at'] = md['joined_at'].isoformat()
                    members.append(md)
                data = dict(g_row)
                data['id'] = str(data['id'])
                data['created_at'] = data['created_at'].isoformat()
                if data.get('scheduled_meal_at'):
                    data['scheduled_meal_at'] = data['scheduled_meal_at'].isoformat()
                data['members'] = members
                return [True, data]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def update_group_meal_time(group_id, scheduled_meal_at):
    """Update the group's scheduled_meal_at timestamp. Accepts ISO 8601 string or None to clear."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Allow None to clear the field
                cursor.execute(
                    "UPDATE groups SET scheduled_meal_at = %s WHERE id = %s RETURNING id, group_name, creator_netid, selected_restaurant_id, created_at, scheduled_meal_at",
                    (scheduled_meal_at, group_id)
                )
                row = cursor.fetchone()
                conn.commit()
                if not row:
                    return [False, 'Group not found']
                data = dict(row)
                data['id'] = str(data['id'])
                data['created_at'] = data['created_at'].isoformat()
                if data.get('scheduled_meal_at'):
                    data['scheduled_meal_at'] = data['scheduled_meal_at'].isoformat()
                return [True, data]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def list_groups_for_user(netid):
    """List groups for which netid is a member."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT g.id, g.group_name, g.creator_netid, g.selected_restaurant_id, g.created_at, g.scheduled_meal_at
                    FROM group_members gm
                    JOIN groups g ON gm.group_id = g.id
                    WHERE gm.user_netid = %s
                    ORDER BY g.created_at DESC
                """, (netid,))
                rows = cursor.fetchall()
                groups = []
                for r in rows:
                    d = dict(r)
                    d['id'] = str(d['id'])
                    d['created_at'] = d['created_at'].isoformat()
                    if d.get('scheduled_meal_at'):
                        d['scheduled_meal_at'] = d['scheduled_meal_at'].isoformat()
                    groups.append(d)
                return [True, groups]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def search_users(query, limit=10):
    """Search users by partial match on netid, firstname, or fullname. Returns list of {netid, firstname, fullname}."""
    q = (query or '').strip()
    if not q:
        return [True, []]
    like = f"%{q}%"
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT netid, firstname, fullname
                    FROM users
                    WHERE netid ILIKE %s OR firstname ILIKE %s OR fullname ILIKE %s
                    ORDER BY firstname ASC
                    LIMIT %s
                    """,
                    (like, like, like, limit)
                )
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append({
                        'netid': row['netid'],
                        'firstname': row.get('firstname'),
                        'fullname': row.get('fullname')
                    })
                return [True, results]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def get_available_cuisines():
    """Get distinct cuisine/category values from restaurants table."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT DISTINCT category
                    FROM restaurants
                    WHERE category IS NOT NULL AND category <> ''
                    ORDER BY category ASC
                """)
                rows = cursor.fetchall()
                cuisines = [row['category'] for row in rows]
                return [True, cuisines]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

def get_group_preferences(group_id):
    """
    Aggregate favorite cuisines, dietary restrictions, and allergies for all members in a group.
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Get all members' preferences
                cursor.execute("""
                    SELECT u.favorite_cuisine, u.dietary_restrictions, u.allergies
                    FROM group_members gm
                    JOIN users u ON gm.user_netid = u.netid
                    WHERE gm.group_id = %s
                """, (group_id,))
                rows = cursor.fetchall()
                
                if not rows:
                    return [True, {
                        'recommended_cuisines': [],
                        'dietary_restrictions': [],
                        'allergies': [],
                        'cuisine_counts': {}
                    }]
                
                # Aggregate cuisines for group(count frequency)
                cuisine_count = {}
                dietary_set = set()
                allergies_set = set()
                
                for row in rows:
                    cuisines = row['favorite_cuisine'] or []
                    restrictions = row['dietary_restrictions'] or []
                    allergies = row['allergies'] or []
                    
                    # Count each cuisine (case-insensitive, normalize to title case)
                    for c in cuisines:
                        if c:
                            normalized = c.strip().title()
                            cuisine_count[normalized] = cuisine_count.get(normalized, 0) + 1
                    
                    # Union of dietary restrictions
                    for d in restrictions:
                        if d:
                            dietary_set.add(d.strip().title())
                    
                    # Union of allergies
                    for a in allergies:
                        if a:
                            allergies_set.add(a.strip().title())
                
                # Sort cuisines by count desc, then alphabetically
                sorted_cuisines = sorted(cuisine_count.items(), key=lambda x: (-x[1], x[0]))
                top_cuisines = [c[0] for c in sorted_cuisines[:3]]
                
                return [True, {
                    'recommended_cuisines': top_cuisines,
                    'dietary_restrictions': sorted(list(dietary_set)),
                    'allergies': sorted(list(allergies_set)),
                    'cuisine_counts': cuisine_count
                }]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)
    

def get_admin_status(username):
    """
    Check if a user is an admin by netid (username).
    Returns [True, is_admin] or [False, error_msg].
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT admin_status
                FROM public.users 
                WHERE netid = %s
                """
                cursor.execute(sql, (username,))
                row = cursor.fetchone()
                
                if row:
                    is_admin = row[0]
                    return [True, is_admin]
                return [False, 'User not found']
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)

if __name__ == "__main__":
    pass