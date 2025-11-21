import sys
import os
import contextlib
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

load_dotenv()
# Read-only access for the web app layer (Postgres)
DATABASE_URL = os.getenv("TB_DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "Environment variable TB_DATABASE_URL is not set. "
        "Set it to a valid Postgres URL (eg. postgresql://user:pass@host:port/db)."
    )
def _err_response(ex):
    error_message = str(sys.argv[0] + ': ')
    print(f"{error_message} {str(ex)}", file=sys.stderr)
    return [False, 'A server error occurred. Please contact the system administrator.']

def _get_conn():
    # Return a new psycopg2 connection. Caller should use context manager.
    return psycopg2.connect(DATABASE_URL)

def load_all_restaurants():
    """
    Return all restaurants with id, name, category, hours, avg_price.
    """
    try:
        with _get_conn() as conn:
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
                        'yelp_rating': float(row.get('yelp_rating')) if row.get('yelp_rating') is not None else None
                    }
                    response.append(entry)

                return [True, response]
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
        with _get_conn() as conn:
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
                        'yelp_rating': float(row.get('yelp_rating')) if row.get('yelp_rating') is not None else None
                    }
                    response.append(entry)

                return [True, response]
    except Exception as ex:
        return _err_response(ex)

def load_restaurant_by_id(rest_id):
    # return one restaurant dict by id.
    try:
        with _get_conn() as conn:
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
                    'yelp_rating': float(row.get('yelp_rating')) if row.get('yelp_rating') is not None else None
                }
                return [True, data]
    except Exception as ex:
        return _err_response(ex)

def load_menu_for_restaurant(rest_id):
    """
    Return list of menu items for a restaurant id.
    Each item has: name, description, price_cents, price (formatted or None)
    """
    try:
        with _get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = (
                    "SELECT * "
                    "FROM menu_items WHERE restaurant_id = %s "
                    "ORDER BY name ASC"
                )
                cursor.execute(sql, (rest_id,))
                rows = cursor.fetchall()

                items = []
                for row in rows:
                    items.append({
                        'name': row.get('name'),
                        'description': row.get('description'), 
                        'price': float(row.get('avg_price')) if row.get('avg_price') is not None else None,
                    })

                return [True, items]
    except Exception as ex:
        return _err_response(ex)

def upsert_user(username, email, firstname, fullname):
    """
    Insert or update a user record with CAS login info.
    Username is stored as 'netid'. Returns [True, user_data] or [False, error_msg].
    """
    try:
        with _get_conn() as conn:
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
    except Exception as ex:
        print(f"DEBUG upsert_user: Exception occurred: {ex}")
        return _err_response(ex)

def get_user_by_username(username):
    """
    Retrieve a user record by netid (username).
    Returns [True, user_data] or [False, error_msg].
    """
    try:
        with _get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = "SELECT id, netid, email, firstname, fullname, favorite_cuisine, allergies, dietary_restrictions FROM public.users WHERE netid = %s"
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
    except Exception as ex:
        return _err_response(ex)

def update_favorite_cuisine(username, favorite_cuisine):
    """
    Update a user's favorite cuisines by netid (username).
    favorite_cuisine can be a list (for arrays) or a single string.
    Returns [True, user_data] or [False, error_msg].
    """
    try:
        with _get_conn() as conn:
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
    except Exception as ex:
        return _err_response(ex)

def update_allergies(username, allergies):
    """
    Update a user's allergies by netid (username).
    allergies can be a list (for arrays) or a single string.
    Returns [True, user_data] or [False, error_msg].
    """
    try:
        with _get_conn() as conn:
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
    except Exception as ex:
        return _err_response(ex)

def update_dietary_restrictions(username, dietary_restrictions):
    """
    Update a user's dietary restrictions by netid (username).
    dietary_restrictions can be a list (for arrays) or a single string.
    Returns [True, user_data] or [False, error_msg].
    """
    try:
        with _get_conn() as conn:
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
    except Exception as ex:
        return _err_response(ex)
    
def upsert_review(rest_id, username, rating, comment):
    """
    Insert or update a review for a restaurant by a user.
    Gets user_id from username (netid), then inserts/updates review.
    Returns [True, review_data] or [False, error_msg].
    """
    try:
        with _get_conn() as conn:
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
    except Exception as ex:
        return _err_response(ex)

def get_reviews_by_restaurant(rest_id):
    """
    Get all reviews for a specific restaurant with user info.
    Returns [True, reviews_list] or [False, error_msg].
    """
    try:
        with _get_conn() as conn:
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
    except Exception as ex:
        return _err_response(ex)

def get_reviews_by_user(username):
    """
    Get all reviews by a specific user (by netid) with restaurant info.
    Returns [True, reviews_list] or [False, error_msg].
    """
    try:
        with _get_conn() as conn:
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
    except Exception as ex:
        return _err_response(ex)

def delete_review(review_id, username):
    """
    Delete a review by id, but only if it belongs to the given user.
    Returns [True, None] or [False, error_msg].
    """
    try:
        with _get_conn() as conn:
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
    except Exception as ex:
        return _err_response(ex)