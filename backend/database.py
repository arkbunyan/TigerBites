import sys
import os
import contextlib
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

load_dotenv()  # Load environment variables from .env file

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
                sql = "SELECT id, name, category, hours, avg_price FROM restaurants"
                cursor.execute(sql)
                rows = cursor.fetchall()

                response = []
                for row in rows:
                    entry = {
                        'id': str(row['id']),
                        'created_at': row['created_at'].isoformat(),
                        'name': row['name'],
                        'description': row['description'],
                        'location': row['location'],
                        'category': row['category'],
                        'hours': row['hours'],
                        'avg_price': float(row['avg_price']) if row['avg_price'] is not None else None,
                        'lat_long': row['lat_long']
    
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
                    "SELECT id, name, category, hours, avg_price "
                    "FROM restaurants "
                    "WHERE name ILIKE %s AND category ILIKE %s "
                    "ORDER BY name ASC"
                )
                cursor.execute(sql, (f"%{name}%", f"%{category}%"))
                rows = cursor.fetchall()

                response = []
                for row in rows:
                    entry = {
                        'id': str(row['id']),
                        'created_at': row['created_at'].isoformat(),
                        'name': row['name'],
                        'description': row['description'],
                        'location': row['location'],
                        'category': row['category'],
                        'hours': row['hours'],
                        'avg_price': float(row['avg_price']) if row['avg_price'] is not None else None,
                        'lat_long': row['lat_long']
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
                sql = "SELECT id, name, category, hours, avg_price FROM restaurants WHERE id = %s"
                cursor.execute(sql, (rest_id,))
                row = cursor.fetchone()
                if not row:
                    return [False, 'Not found']

                data = {
                    'id': str(row['id']),
                        'created_at': row['created_at'].isoformat(),
                        'name': row['name'],
                        'description': row['description'],
                        'location': row['location'],
                        'category': row['category'],
                        'hours': row['hours'],
                        'avg_price': float(row['avg_price']) if row['avg_price'] is not None else None,
                        'lat_long': row['lat_long']
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
                    "SELECT name, COALESCE(description, '') AS description, price_cents "
                    "FROM menu_items WHERE restaurant_id = %s "
                    "ORDER BY name ASC"
                )
                cursor.execute(sql, (rest_id,))
                rows = cursor.fetchall()

                items = []
                for row in rows:
                    cents = row['price_cents']
                    price_str = None if cents is None else f"${cents/100:.2f}"
                    items.append({
                        'name': row['name'],
                        'description': row['description'],
                        'avg_price': float(row['avg_price']) if row['avg_price'] is not None else None,
                    })

                return [True, items]
    except Exception as ex:
        return _err_response(ex)
