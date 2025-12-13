import sys
import os
from pathlib import Path
import csv
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool

load_dotenv()

# Postgres URL
DATABASE_URL = os.getenv("TB_DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "Environment variable TB_DATABASE_URL is not set. "
        "Set it to a valid Postgres URL."
    )

# Small connection pool
pool = SimpleConnectionPool(
    minconn=1,
    maxconn=2,
    dsn=DATABASE_URL,
)

# Paths for menu CSVs
BASE_DIR = Path(__file__).resolve().parents[1]
MENU_DATA_DIR = BASE_DIR / "data_management" / "menu data"


def _err_response(ex):
    msg = f"{sys.argv[0]}: {ex}"
    print(msg, file=sys.stderr)
    return [False, "A server error occurred. Please contact the system administrator."]


def _get_conn():
    return pool.getconn()


def _put_conn(conn):
    if conn is not None:
        pool.putconn(conn)


def _canonical_name(value: str) -> str:
    """Lowercase for matching."""
    if not value:
        return ""
    value = value.lower()
    return "".join(ch for ch in value if ch.isalnum())


def _load_menu_order_for_restaurant(restaurant_name: str):
    """
    Build name to index mapping from that restaurant's CSV.
    If anything fails, return None so we fall back to DB order.
    """
    try:
        if not restaurant_name or not MENU_DATA_DIR.exists():
            return None

        target_key = _canonical_name(restaurant_name)
        csv_path = None

        # Find CSV whose filename prefix matches restaurant name
        for path in MENU_DATA_DIR.iterdir():
            if not path.is_file():
                continue
            if path.suffix.lower() != ".csv":
                continue
            if "__MACOSX" in str(path):
                continue

            # Filenames look like "Thai Village - thai_village_menu.csv"
            prefix = path.name.split(" - ", 1)[0]
            if _canonical_name(prefix) == target_key:
                csv_path = path
                break

        if csv_path is None:
            return None

        order = {}
        idx = 0
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("Item") or "").strip()
                if not name:
                    continue
                if name not in order:
                    order[name] = idx
                    idx += 1

        return order or None
    except Exception:
        # Any problem: just let DB order stand
        return None


def load_all_restaurants():
    """Return all restaurants."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                c.execute("SELECT * FROM restaurants")
                rows = c.fetchall()
                out = []
                for row in rows:
                    out.append({
                        "id": row.get("id"),
                        "created_at": row.get("created_at").isoformat(),
                        "name": row.get("name"),
                        "description": row.get("description"),
                        "location": row.get("location"),
                        "category": row.get("category"),
                        "hours": row.get("hours"),
                        "avg_price": float(row.get("avg_price")) if row.get("avg_price") is not None else None,
                        "latitude": row.get("latitude"),
                        "longitude": row.get("longitude"),
                        "picture": row.get("picture"),
                        "yelp_rating": float(row.get("yelp_rating")) if row.get("yelp_rating") is not None else None,
                        "website_url": row.get("website_url"),
                    })
                return [True, out]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def restaurant_search(params):
    """Search restaurants by name and category substring."""
    name = params[0] if len(params) > 0 else ""
    category = params[1] if len(params) > 1 else ""

    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = (
                    "SELECT * "
                    "FROM restaurants "
                    "WHERE name ILIKE %s AND category ILIKE %s "
                    "ORDER BY name ASC"
                )
                c.execute(sql, (f"%{name}%", f"%{category}%"))
                rows = c.fetchall()
                out = []
                for row in rows:
                    out.append({
                        "id": row.get("id"),
                        "created_at": row.get("created_at").isoformat(),
                        "name": row.get("name"),
                        "description": row.get("description"),
                        "location": row.get("location"),
                        "category": row.get("category"),
                        "hours": row.get("hours"),
                        "avg_price": float(row.get("avg_price")) if row.get("avg_price") is not None else None,
                        "latitude": row.get("latitude"),
                        "longitude": row.get("longitude"),
                        "picture": row.get("picture"),
                        "yelp_rating": float(row.get("yelp_rating")) if row.get("yelp_rating") is not None else None,
                        "website_url": row.get("website_url"),
                    })
                return [True, out]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def load_restaurant_by_id(rest_id):
    """Return one restaurant by id."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                c.execute("SELECT * FROM restaurants WHERE id = %s", (rest_id,))
                row = c.fetchone()
                if not row:
                    return [False, "Not found"]

                data = {
                    "id": row.get("id"),
                    "created_at": row.get("created_at").isoformat(),
                    "name": row.get("name"),
                    "description": row.get("description"),
                    "location": row.get("location"),
                    "category": row.get("category"),
                    "hours": row.get("hours"),
                    "avg_price": float(row.get("avg_price")) if row.get("avg_price") is not None else None,
                    "latitude": row.get("latitude"),
                    "longitude": row.get("longitude"),
                    "picture": row.get("picture"),
                    "yelp_rating": float(row.get("yelp_rating")) if row.get("yelp_rating") is not None else None,
                    "website_url": row.get("website_url"),
                }
                return [True, data]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def load_menu_for_restaurant(rest_id):
    """
    Return menu items for a restaurant.
    Each item: id, restaurant_id, name, description, price.
    Order tries to match the CSV for that restaurant.
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                    SELECT
                        m.id,
                        m.restaurant_id,
                        m.name,
                        m.description,
                        m.avg_price,
                        r.name AS restaurant_name
                    FROM menu_items m
                    JOIN restaurants r ON m.restaurant_id = r.id
                    WHERE m.restaurant_id = %s
                """
                c.execute(sql, (rest_id,))
                rows = c.fetchall()

                items = []
                restaurant_name = None
                for row in rows:
                    if restaurant_name is None:
                        restaurant_name = row.get("restaurant_name")
                    items.append({
                        "id": str(row.get("id")) if row.get("id") is not None else None,
                        "restaurant_id": str(row.get("restaurant_id")) if row.get("restaurant_id") is not None else None,
                        "name": row.get("name"),
                        "description": row.get("description"),
                        "price": float(row.get("avg_price")) if row.get("avg_price") is not None else None,
                    })

                # Try to apply CSV order
                order_map = _load_menu_order_for_restaurant(restaurant_name)
                if order_map:
                    default_index = len(order_map)
                    items.sort(key=lambda item: order_map.get(item.get("name"), default_index))

                return [True, items]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def update_restaurant(restaurant):
    """Update one restaurant row."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
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
                    restaurant.get("avg_price"),
                    restaurant.get("category"),
                    restaurant.get("description"),
                    restaurant.get("hours"),
                    restaurant.get("latitude"),
                    restaurant.get("location"),
                    restaurant.get("longitude"),
                    restaurant.get("name"),
                    restaurant.get("picture"),
                    restaurant.get("yelp_rating"),
                    restaurant.get("id"),
                )
                c.execute(sql, values)
                updated = c.fetchone()
                conn.commit()
                return [True, dict(updated)]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def update_menu_items(restaurant_id, items):
    """
    Update menu items for a restaurant.
    items: list of dicts {id, name, description, price}.
    """
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                updated = 0
                for item in items or []:
                    c.execute(
                        """
                        UPDATE public.menu_items
                        SET name = %s,
                            description = %s,
                            avg_price = %s
                        WHERE id = %s AND restaurant_id = %s
                        RETURNING id
                        """,
                        (
                            item.get("name"),
                            item.get("description"),
                            item.get("price"),
                            item.get("id"),
                            restaurant_id,
                        ),
                    )
                    if c.fetchone():
                        updated += 1
                conn.commit()
                return [True, updated]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


# ---------- user helpers ----------

def _user_row_to_dict(row):
    """Convert a users row into the standard dict with lists."""
    user = dict(row)
    user["favorite_cuisine"] = list(user.get("favorite_cuisine") or [])
    user["allergies"] = list(user.get("allergies") or [])
    user["dietary_restrictions"] = list(user.get("dietary_restrictions") or [])
    return user


def upsert_user(username, email, firstname, fullname):
    """Insert or update a user from CAS info."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                INSERT INTO public.users (netid, email, firstname, fullname)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (netid) DO UPDATE
                SET email = EXCLUDED.email,
                    firstname = EXCLUDED.firstname,
                    fullname = EXCLUDED.fullname
                RETURNING id, netid, email, firstname, fullname,
                          favorite_cuisine, allergies, dietary_restrictions
                """
                print(
                    "DEBUG upsert_user: Executing SQL with values - "
                    f"netid: {username}, email: {email}, firstname: {firstname}, fullname: {fullname}"
                )
                c.execute(sql, (username, email, firstname, fullname))
                row = c.fetchone()
                print(f"DEBUG upsert_user: Query result row: {row}")
                conn.commit()
                if row:
                    return [True, _user_row_to_dict(row)]
                return [False, "Failed to insert/update user"]
        finally:
            _put_conn(conn)
    except Exception as ex:
        print(f"DEBUG upsert_user: Exception occurred: {ex}")
        return _err_response(ex)


def get_user_by_username(username):
    """Get one user by netid."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                SELECT id, netid, email, firstname, fullname,
                       favorite_cuisine, allergies, dietary_restrictions, admin_status
                FROM public.users
                WHERE netid = %s
                """
                c.execute(sql, (username,))
                row = c.fetchone()
                if row:
                    return [True, _user_row_to_dict(row)]
                return [False, "User not found"]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def update_favorite_cuisine(username, favorite_cuisine):
    """Update favorite_cuisine array for a user."""
    try:
        conn = _get_conn()
        try:
            if isinstance(favorite_cuisine, list):
                cuisine_array = favorite_cuisine
            else:
                cuisine_array = [favorite_cuisine] if favorite_cuisine else []

            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                UPDATE public.users
                SET favorite_cuisine = %s
                WHERE netid = %s
                RETURNING id, netid, email, firstname, fullname,
                          favorite_cuisine, allergies, dietary_restrictions
                """
                c.execute(sql, (cuisine_array, username))
                row = c.fetchone()
                conn.commit()
                if row:
                    return [True, _user_row_to_dict(row)]
                return [False, "User not found"]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def update_allergies(username, allergies):
    """Update allergies array for a user."""
    try:
        conn = _get_conn()
        try:
            if isinstance(allergies, list):
                arr = allergies
            else:
                arr = [allergies] if allergies else []

            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                UPDATE public.users
                SET allergies = %s
                WHERE netid = %s
                RETURNING id, netid, email, firstname, fullname,
                          favorite_cuisine, allergies, dietary_restrictions
                """
                c.execute(sql, (arr, username))
                row = c.fetchone()
                conn.commit()
                if row:
                    return [True, _user_row_to_dict(row)]
                return [False, "User not found"]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def update_dietary_restrictions(username, dietary_restrictions):
    """Update dietary_restrictions array for a user."""
    try:
        conn = _get_conn()
        try:
            if isinstance(dietary_restrictions, list):
                arr = dietary_restrictions
            else:
                arr = [dietary_restrictions] if dietary_restrictions else []

            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                UPDATE public.users
                SET dietary_restrictions = %s
                WHERE netid = %s
                RETURNING id, netid, email, firstname, fullname,
                          favorite_cuisine, allergies, dietary_restrictions
                """
                c.execute(sql, (arr, username))
                row = c.fetchone()
                conn.commit()
                if row:
                    return [True, _user_row_to_dict(row)]
                return [False, "User not found"]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


# ---------- reviews ----------

def upsert_review(rest_id, username, rating, comment):
    """Insert a review for a restaurant by a user."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                c.execute(
                    "SELECT id FROM public.users WHERE netid = %s",
                    (username,),
                )
                user_row = c.fetchone()
                if not user_row:
                    return [False, "User not found"]

                user_id = user_row["id"]
                sql = """
                INSERT INTO public.reviews (restaurant_id, user_id, rating, comment)
                VALUES (%s, %s, %s, %s)
                RETURNING id, restaurant_id, user_id, rating, comment, created_at
                """
                c.execute(sql, (rest_id, user_id, rating, comment))
                row = c.fetchone()
                conn.commit()

                if row:
                    review = dict(row)
                    review["created_at"] = review["created_at"].isoformat()
                    review["user_id"] = str(review["user_id"])
                    review["restaurant_id"] = str(review["restaurant_id"])
                    review["id"] = str(review["id"])
                    return [True, review]
                return [False, "Failed to insert review"]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def get_all_reviews():
    """Get all reviews with user and restaurant info."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                SELECT r.id, r.restaurant_id, r.rating, r.comment, r.created_at,
                       u.netid AS username, u.firstname, u.fullname,
                       rest.name AS restaurant_name, rest.category
                FROM public.reviews r
                JOIN public.users u ON r.user_id = u.id
                JOIN public.restaurants rest ON r.restaurant_id = rest.id
                ORDER BY r.created_at DESC
                """
                c.execute(sql)
                rows = c.fetchall()

                reviews = []
                for row in rows:
                    review = dict(row)
                    review["created_at"] = review["created_at"].isoformat()
                    review["id"] = str(review["id"])
                    review["restaurant_id"] = str(review["restaurant_id"])
                    reviews.append(review)

                return [True, reviews]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def get_reviews_by_restaurant(rest_id):
    """Get all reviews for a given restaurant."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                SELECT r.id, r.restaurant_id, r.rating, r.comment, r.created_at,
                       u.netid AS username, u.firstname, u.fullname
                FROM public.reviews r
                JOIN public.users u ON r.user_id = u.id
                WHERE r.restaurant_id = %s
                ORDER BY r.created_at DESC
                """
                c.execute(sql, (rest_id,))
                rows = c.fetchall()

                reviews = []
                for row in rows:
                    review = dict(row)
                    review["created_at"] = review["created_at"].isoformat()
                    review["id"] = str(review["id"])
                    review["restaurant_id"] = str(review["restaurant_id"])
                    reviews.append(review)

                return [True, reviews]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def get_reviews_by_user(username):
    """Get all reviews written by one user."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                SELECT r.id, r.restaurant_id, r.rating, r.comment, r.created_at,
                       rest.name AS restaurant_name, rest.category
                FROM public.reviews r
                JOIN public.users u ON r.user_id = u.id
                JOIN public.restaurants rest ON r.restaurant_id = rest.id
                WHERE u.netid = %s
                ORDER BY r.created_at DESC
                """
                c.execute(sql, (username,))
                rows = c.fetchall()

                reviews = []
                for row in rows:
                    review = dict(row)
                    review["created_at"] = review["created_at"].isoformat()
                    review["id"] = str(review["id"])
                    review["restaurant_id"] = str(review["restaurant_id"])
                    reviews.append(review)

                return [True, reviews]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def delete_review(review_id, username):
    """Delete one review if it belongs to the given user."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                DELETE FROM public.reviews r
                USING public.users u
                WHERE r.id = %s AND r.user_id = u.id AND u.netid = %s
                RETURNING r.id
                """
                c.execute(sql, (review_id, username))
                row = c.fetchone()
                conn.commit()
                if row:
                    return [True, None]
                return [False, "Review not found or unauthorized"]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def delete_review_force(review_id):
    """Delete any review by id."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                DELETE FROM public.reviews
                WHERE id = %s
                RETURNING id
                """
                c.execute(sql, (review_id,))
                row = c.fetchone()
                conn.commit()
                if row:
                    return [True, None]
                return [False, "Review not found"]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


# ---------- feedback ----------

def get_all_feedback():
    """Get all feedback entries with user info."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                SELECT f.id, f.created_at, f.restaurant_id, f.user_id, f.response,
                       u.netid AS username, u.firstname, u.fullname
                FROM public.feedback f
                JOIN public.users u ON f.user_id = u.id
                ORDER BY f.created_at DESC
                """
                c.execute(sql)
                rows = c.fetchall()

                feedback_list = []
                for row in rows:
                    feedback = dict(row)
                    feedback["created_at"] = feedback["created_at"].isoformat()
                    feedback["id"] = str(feedback["id"])
                    feedback_list.append(feedback)

                return [True, feedback_list]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def get_feedback_by_restaurant(rest_id):
    """Get feedback entries for one restaurant."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                SELECT f.id, f.created_at, f.restaurant_id, f.user_id, f.response,
                       u.netid AS username, u.firstname, u.fullname
                FROM public.feedback f
                JOIN public.users u ON f.user_id = u.id
                WHERE f.restaurant_id = %s
                ORDER BY f.created_at DESC
                """
                c.execute(sql, (rest_id,))
                rows = c.fetchall()

                feedback_list = []
                for row in rows:
                    feedback = dict(row)
                    feedback["created_at"] = feedback["created_at"].isoformat()
                    feedback["id"] = str(feedback["id"])
                    feedback_list.append(feedback)

                return [True, feedback_list]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def submit_feedback(rest_id, username, response):
    """Insert feedback for a restaurant by a user."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                c.execute("SELECT id FROM public.users WHERE netid = %s", (username,))
                user_row = c.fetchone()
                if not user_row:
                    return [False, "User not found"]
                user_id = user_row["id"]

                sql = """
                INSERT INTO public.feedback (restaurant_id, user_id, response)
                VALUES (%s, %s, %s)
                RETURNING id, created_at, restaurant_id, user_id, response
                """
                c.execute(sql, (rest_id, user_id, response))
                row = c.fetchone()
                conn.commit()

                if row:
                    feedback = dict(row)
                    feedback["created_at"] = feedback["created_at"].isoformat()
                    feedback["user_id"] = str(feedback["user_id"])
                    feedback["restaurant_id"] = str(feedback["restaurant_id"])
                    feedback["id"] = str(feedback["id"])
                    return [True, feedback]
                return [False, "Failed to submit feedback"]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def delete_feedback(feedback_id):
    """Delete a feedback entry by id."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                sql = """
                DELETE FROM public.feedback f
                USING public.users u
                WHERE f.id = %s
                RETURNING f.id
                """
                c.execute(sql, (feedback_id,))
                row = c.fetchone()
                conn.commit()
                if row:
                    return [True, None]
                return [False, "Feedback not found or unauthorized"]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


# ---------- groups ----------

def create_group(group_name, creator_netid, selected_restaurant_id=None):
    """Create a group and add creator as leader."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                c.execute("SELECT netid FROM users WHERE netid = %s", (creator_netid,))
                if c.fetchone() is None:
                    return [False, "Creator user not found"]

                if selected_restaurant_id is not None:
                    c.execute(
                        "SELECT id FROM restaurants WHERE id = %s",
                        (selected_restaurant_id,),
                    )
                    if c.fetchone() is None:
                        return [False, "Selected restaurant not found"]

                c.execute(
                    """
                    INSERT INTO groups (group_name, creator_netid, selected_restaurant_id)
                    VALUES (%s, %s, %s)
                    RETURNING id, group_name, creator_netid, selected_restaurant_id,
                              created_at, scheduled_meal_at
                    """,
                    (group_name, creator_netid, selected_restaurant_id),
                )
                g_row = c.fetchone()

                c.execute(
                    """
                    INSERT INTO group_members (group_id, user_netid, role)
                    VALUES (%s, %s, 'leader')
                    ON CONFLICT (group_id, user_netid) DO NOTHING
                    """,
                    (g_row["id"], creator_netid),
                )
                conn.commit()

                data = dict(g_row)
                data["id"] = str(data["id"])
                data["created_at"] = data["created_at"].isoformat()
                if data.get("scheduled_meal_at"):
                    data["scheduled_meal_at"] = data["scheduled_meal_at"].isoformat()
                return [True, data]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def add_member_to_group(group_id, member_netid):
    """Add a member to a group by netid."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                c.execute("SELECT netid FROM users WHERE netid = %s", (member_netid,))
                if c.fetchone() is None:
                    return [False, "User not found"]

                c.execute("SELECT id FROM groups WHERE id = %s", (group_id,))
                if c.fetchone() is None:
                    return [False, "Group not found"]

                c.execute(
                    """
                    INSERT INTO group_members (group_id, user_netid, role)
                    VALUES (%s, %s, 'member')
                    ON CONFLICT (group_id, user_netid) DO NOTHING
                    """,
                    (group_id, member_netid),
                )
                conn.commit()
                return [True, None]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def remove_member_from_group(group_id, member_netid):
    """Remove a member from a group."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                c.execute(
                    """
                    DELETE FROM group_members
                    WHERE group_id = %s AND user_netid = %s
                    RETURNING group_id
                    """,
                    (group_id, member_netid),
                )
                row = c.fetchone()
                conn.commit()
                if row:
                    return [True, None]
                return [False, "Membership not found"]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def delete_group(group_id):
    """Delete a group and its memberships."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor() as c:
                c.execute("SELECT 1 FROM groups WHERE id = %s", (group_id,))
                if not c.fetchone():
                    return [False, "Group not found"]

                c.execute("DELETE FROM group_members WHERE group_id = %s", (group_id,))
                c.execute("DELETE FROM groups WHERE id = %s", (group_id,))
                conn.commit()
                return [True, "deleted"]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def update_group_selected_restaurant(group_id, restaurant_id):
    """Set or clear selected_restaurant_id for a group."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                if restaurant_id is not None:
                    c.execute(
                        "SELECT id FROM restaurants WHERE id = %s",
                        (restaurant_id,),
                    )
                    if c.fetchone() is None:
                        return [False, "Restaurant not found"]

                c.execute(
                    """
                    UPDATE groups
                    SET selected_restaurant_id = %s
                    WHERE id = %s
                    RETURNING id, group_name, creator_netid, selected_restaurant_id,
                              created_at, scheduled_meal_at
                    """,
                    (restaurant_id, group_id),
                )
                row = c.fetchone()
                conn.commit()
                if not row:
                    return [False, "Group not found"]

                data = dict(row)
                data["id"] = str(data["id"])
                data["created_at"] = data["created_at"].isoformat()
                if data.get("scheduled_meal_at"):
                    data["scheduled_meal_at"] = data["scheduled_meal_at"].isoformat()
                return [True, data]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def get_group_with_members(group_id):
    """Return group details and member list."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                c.execute(
                    """
                    SELECT g.id, g.group_name, g.creator_netid,
                           g.selected_restaurant_id, g.created_at, g.scheduled_meal_at,
                           r.name AS restaurant_name
                    FROM groups g
                    LEFT JOIN restaurants r ON g.selected_restaurant_id = r.id
                    WHERE g.id = %s
                    """,
                    (group_id,),
                )
                g_row = c.fetchone()
                if not g_row:
                    return [False, "Group not found"]

                c.execute(
                    """
                    SELECT gm.user_netid AS netid, gm.role, gm.joined_at,
                           u.firstname, u.fullname
                    FROM group_members gm
                    JOIN users u ON gm.user_netid = u.netid
                    WHERE gm.group_id = %s
                    ORDER BY gm.joined_at ASC
                    """,
                    (group_id,),
                )
                members_rows = c.fetchall()
                members = []
                for mr in members_rows:
                    d = dict(mr)
                    d["joined_at"] = d["joined_at"].isoformat()
                    members.append(d)

                data = dict(g_row)
                data["id"] = str(data["id"])
                data["created_at"] = data["created_at"].isoformat()
                if data.get("scheduled_meal_at"):
                    data["scheduled_meal_at"] = data["scheduled_meal_at"].isoformat()
                data["members"] = members
                return [True, data]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def update_group_meal_time(group_id, scheduled_meal_at):
    """Update scheduled_meal_at for a group (string ISO or None)."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                c.execute(
                    """
                    UPDATE groups
                    SET scheduled_meal_at = %s
                    WHERE id = %s
                    RETURNING id, group_name, creator_netid, selected_restaurant_id,
                              created_at, scheduled_meal_at
                    """,
                    (scheduled_meal_at, group_id),
                )
                row = c.fetchone()
                conn.commit()
                if not row:
                    return [False, "Group not found"]
                data = dict(row)
                data["id"] = str(data["id"])
                data["created_at"] = data["created_at"].isoformat()
                if data.get("scheduled_meal_at"):
                    data["scheduled_meal_at"] = data["scheduled_meal_at"].isoformat()
                return [True, data]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def list_groups_for_user(netid):
    """List groups that this user belongs to."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                c.execute(
                    """
                    SELECT g.id, g.group_name, g.creator_netid,
                           g.selected_restaurant_id, g.created_at, g.scheduled_meal_at
                    FROM group_members gm
                    JOIN groups g ON gm.group_id = g.id
                    WHERE gm.user_netid = %s
                    ORDER BY g.created_at DESC
                    """,
                    (netid,),
                )
                rows = c.fetchall()
                groups = []
                for r in rows:
                    d = dict(r)
                    d["id"] = str(d["id"])
                    d["created_at"] = d["created_at"].isoformat()
                    if d.get("scheduled_meal_at"):
                        d["scheduled_meal_at"] = d["scheduled_meal_at"].isoformat()
                    groups.append(d)
                return [True, groups]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


# ---------- misc ----------

def search_users(query, limit=10):
    """Search users by partial match on netid, firstname, or fullname."""
    q = (query or "").strip()
    if not q:
        return [True, []]
    like = f"%{q}%"
    try:
        conn = _get_conn()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as c:
                c.execute(
                    """
                    SELECT netid, firstname, fullname
                    FROM users
                    WHERE netid ILIKE %s OR firstname ILIKE %s OR fullname ILIKE %s
                    ORDER BY firstname ASC
                    LIMIT %s
                    """,
                    (like, like, like, limit),
                )
                rows = c.fetchall()
                results = []
                for row in rows:
                    results.append(
                        {
                            "netid": row["netid"],
                            "firstname": row.get("firstname"),
                            "fullname": row.get("fullname"),
                        }
                    )
                return [True, results]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def get_available_cuisines():
    """Get distinct category values from restaurants."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(
                cursor_factory=psycopg2.extras.DictCursor
            ) as c:
                c.execute(
                    """
                    SELECT DISTINCT category
                    FROM restaurants
                    WHERE category IS NOT NULL AND category <> ''
                    ORDER BY category ASC
                    """
                )
                rows = c.fetchall()
                cuisines = [row["category"] for row in rows]
                return [True, cuisines]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def get_group_preferences(group_id):
    """Aggregate preferences for all members in a group."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor(
                cursor_factory=psycopg2.extras.DictCursor
            ) as c:
                c.execute(
                    """
                    SELECT u.favorite_cuisine, u.dietary_restrictions, u.allergies
                    FROM group_members gm
                    JOIN users u ON gm.user_netid = u.netid
                    WHERE gm.group_id = %s
                    """,
                    (group_id,),
                )
                rows = c.fetchall()

                if not rows:
                    return [
                        True,
                        {
                            "recommended_cuisines": [],
                            "dietary_restrictions": [],
                            "allergies": [],
                            "cuisine_counts": {},
                        },
                    ]

                cuisine_count = {}
                dietary_set = set()
                allergies_set = set()

                for row in rows:
                    cuisines = row["favorite_cuisine"] or []
                    restrictions = row["dietary_restrictions"] or []
                    allergies = row["allergies"] or []

                    for c_item in cuisines:
                        if c_item:
                            name = c_item.strip().title()
                            cuisine_count[name] = cuisine_count.get(name, 0) + 1

                    for d_item in restrictions:
                        if d_item:
                            dietary_set.add(d_item.strip().title())

                    for a_item in allergies:
                        if a_item:
                            allergies_set.add(a_item.strip().title())

                sorted_cuisines = sorted(
                    cuisine_count.items(), key=lambda x: (-x[1], x[0])
                )
                top_cuisines = [c_name for c_name, _ in sorted_cuisines[:3]]

                return [
                    True,
                    {
                        "recommended_cuisines": top_cuisines,
                        "dietary_restrictions": sorted(list(dietary_set)),
                        "allergies": sorted(list(allergies_set)),
                        "cuisine_counts": cuisine_count,
                    },
                ]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


def get_admin_status(username):
    """Check if a user is admin."""
    try:
        conn = _get_conn()
        try:
            with conn.cursor() as c:
                sql = """
                SELECT admin_status
                FROM public.users
                WHERE netid = %s
                """
                c.execute(sql, (username,))
                row = c.fetchone()
                if row:
                    return [True, row[0]]
                return [False, "User not found"]
        finally:
            _put_conn(conn)
    except Exception as ex:
        return _err_response(ex)


if __name__ == "__main__":
    pass
