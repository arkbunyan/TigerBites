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
                        'avg_price': float(row.get('avg_price')), 
                        'latitude': row.get('latitude'),
                        'longitude': row.get('longitude')
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
                        'longitude': row.get('longitude')
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
                    'longitude': row.get('longitude')
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
                RETURNING id, netid, email, firstname, fullname, favorite_cuisine
                """
                print(f"DEBUG upsert_user: Executing SQL with values - netid: {username}, email: {email}, firstname: {firstname}, fullname: {fullname}")
                cursor.execute(sql, (username, email, firstname, fullname))
                row = cursor.fetchone()
                print(f"DEBUG upsert_user: Query result row: {row}")
                conn.commit()
                
                if row:
                    return [True, dict(row)]
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
                sql = "SELECT id, netid, email, firstname, fullname, favorite_cuisine FROM public.users WHERE netid = %s"
                cursor.execute(sql, (username,))
                row = cursor.fetchone()
                
                if row:
                    return [True, dict(row)]
                return [False, 'User not found']
    except Exception as ex:
        return _err_response(ex)

def update_favorite_cuisine(username, favorite_cuisine):
    """
    Update a user's favorite cuisine by netid (username).
    Returns [True, user_data] or [False, error_msg].
    """
    try:
        with _get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                sql = """
                UPDATE public.users 
                SET favorite_cuisine = %s
                WHERE netid = %s
                RETURNING id, netid, email, firstname, fullname, favorite_cuisine
                """
                cursor.execute(sql, (favorite_cuisine, username))
                row = cursor.fetchone()
                conn.commit()
                
                if row:
                    return [True, dict(row)]
                return [False, 'User not found']
    except Exception as ex:
        return _err_response(ex)