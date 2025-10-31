import sys
import sqlite3
import contextlib

# Read-only access for the web app layer
DATABASE_URL = 'file:proto_db.sqlite?mode=ro'

def _err_response(ex):
    error_message = str(sys.argv[0] + ': ')
    print(f"{error_message} {str(ex)}", file=sys.stderr)
    return [False, 'A server error occurred. Please contact the system administrator.']

def load_all_restaurants():
    """
    Return all restaurants with id, name, category, hours, avg_price.
    """
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None, uri=True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                sql = "SELECT id, name, category, hours, avg_price FROM restaurants"
                cursor.execute(sql, [])
                rows = cursor.fetchall()

                response = []
                for row in rows:
                    entry = {
                        'id': row[0],
                        'name': row[1],
                        'category': row[2],
                        'hours': row[3],
                        'avg_price': row[4]
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
        with sqlite3.connect(DATABASE_URL, isolation_level=None, uri=True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                sql = (
                    "SELECT id, name, category, hours, avg_price "
                    "FROM restaurants "
                    "WHERE name LIKE ? AND category LIKE ?"
                )
                cursor.execute(sql, [f'%{name}%', f'%{category}%'])
                rows = cursor.fetchall()

                response = []
                for row in rows:
                    entry = {
                        'id': row[0],
                        'name': row[1],
                        'category': row[2],
                        'hours': row[3],
                        'avg_price': row[4]
                    }
                    response.append(entry)

                return [True, response]
    except Exception as ex:
        return _err_response(ex)

def load_restaurant_by_id(rest_id):
    # return one restaurant dict by id.
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None, uri=True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                sql = "SELECT id, name, category, hours, avg_price FROM restaurants WHERE id = ?"
                cursor.execute(sql, [rest_id])
                row = cursor.fetchone()
                if not row:
                    return [False, 'Not found']

                data = {
                    'id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'hours': row[3],
                    'avg_price': row[4]
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
        with sqlite3.connect(DATABASE_URL, isolation_level=None, uri=True) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                sql = (
                    "SELECT name, COALESCE(description, ''), price_cents "
                    "FROM menu_items WHERE restaurant_id = ? "
                    "ORDER BY name ASC"
                )
                cursor.execute(sql, [rest_id])
                rows = cursor.fetchall()

                items = []
                for name, desc, cents in rows:
                    price_str = None if cents is None else f"${cents/100:.2f}"
                    items.append({
                        'name': name,
                        'description': desc,
                        'price_cents': cents,
                        'price': price_str
                    })

                return [True, items]
    except Exception as ex:
        return _err_response(ex)
