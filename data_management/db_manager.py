
"""
TigerBites DB Manager
- Handles DB connection
- Ensures schema exists
- Provides insert helpers (single and bulk)
- Adds helpers for menu item bulk upsert and restaurant lookup by name
"""

import os
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

ROOT_ENV = Path(__file__).resolve().parents[1] / ".env"
if ROOT_ENV.exists():
    load_dotenv(ROOT_ENV)
else:
    load_dotenv()

DATABASE_URL = os.getenv("TB_DATABASE_URL")


def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("TB_DATABASE_URL not set. Add it to your .env or environment.")
    return psycopg2.connect(DATABASE_URL)


def create_restaurants_table():
    ddl = """
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE TABLE IF NOT EXISTS public.restaurants (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        created_at timestamptz NOT NULL DEFAULT now(),
        name        TEXT,
        description TEXT,
        location    TEXT,
        hours       TEXT,
        category    TEXT,
        avg_price   DOUBLE PRECISION,
        latitude    DOUBLE PRECISION,
        longitude   DOUBLE PRECISION,
        picture     TEXT,
        yelp_rating DOUBLE PRECISION
    );
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(ddl)
        conn.commit()

def migrate_restaurant_new_columns():
    """Add picture (TEXT), yelp_rating (DOUBLE PRECISION), and website_url (TEXT) if missing."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            ALTER TABLE public.restaurants
            ADD COLUMN IF NOT EXISTS picture TEXT;
        """)
        cur.execute("""
            ALTER TABLE public.restaurants
            ADD COLUMN IF NOT EXISTS yelp_rating DOUBLE PRECISION;
        """)
        cur.execute("""
            ALTER TABLE public.restaurants
            ADD COLUMN IF NOT EXISTS website_url TEXT;
        """)
        conn.commit()

def create_menu_items_table():
    ddl = """
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE TABLE IF NOT EXISTS public.menu_items (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        created_at timestamptz NOT NULL DEFAULT now(),
        restaurant_id uuid REFERENCES public.restaurants(id),
        name        TEXT,
        description TEXT,
        avg_price   DOUBLE PRECISION
    );
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(ddl)
        conn.commit()


def create_users_table():
    ddl = """
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE TABLE IF NOT EXISTS public.users (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        created_at timestamptz NOT NULL DEFAULT now(),
        netid TEXT UNIQUE,
        email TEXT,
        firstname TEXT,
        fullname TEXT,
        favorite_cuisine TEXT[],
        allergies TEXT[],
        dietary_restrictions TEXT[],
        admin_status BOOLEAN DEFAULT FALSE
    );
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(ddl)
        conn.commit()

def ensure_restaurants_uniqueness():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'restaurants_name_location_unique'
                ) THEN
                    ALTER TABLE public.restaurants
                    ADD CONSTRAINT restaurants_name_location_unique
                    UNIQUE (name, location);
                END IF;
            END$$;
            """
        )
        conn.commit()


def ensure_menu_items_uniqueness():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                      FROM pg_indexes
                     WHERE indexname = 'menu_items_restaurant_name_unique_ci'
                ) THEN
                    CREATE UNIQUE INDEX menu_items_restaurant_name_unique_ci
                      ON public.menu_items (restaurant_id, lower(name));
                END IF;
            END$$;
            """
        )
        conn.commit()


def find_restaurant_id_by_name(restaurant_name: str):
    sql = """
        SELECT id FROM public.restaurants
        WHERE lower(name) = lower(%s)
        ORDER BY created_at DESC
        LIMIT 1;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (restaurant_name,))
        row = cur.fetchone()
        return row[0] if row else None


def insert_restaurant(restaurant_data, menu_data=None):
    if menu_data is None:
        menu_data = []

    upsert = """
        INSERT INTO public.restaurants
            (name, description, location, hours, category, avg_price, latitude, longitude, picture, yelp_rating, website_url)
        VALUES
            (%(name)s, %(description)s, %(location)s, %(hours)s, %(category)s,
             %(avg_price)s, %(latitude)s, %(longitude)s, %(picture)s, %(yelp_rating)s, %(website_url)s)
        ON CONFLICT (name, location) DO UPDATE SET
            description = EXCLUDED.description,
            hours       = EXCLUDED.hours,
            category    = EXCLUDED.category,
            avg_price   = EXCLUDED.avg_price,
            latitude    = EXCLUDED.latitude,
            longitude   = EXCLUDED.longitude,
            picture     = EXCLUDED.picture,
            yelp_rating = EXCLUDED.yelp_rating,
            website_url = EXCLUDED.website_url
        RETURNING id;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(upsert, restaurant_data)
        rest_id = cur.fetchone()[0]

        for item in menu_data:
            cur.execute(
                """
                INSERT INTO public.menu_items
                    (restaurant_id, name, description, avg_price)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (restaurant_id, lower(name))
                DO UPDATE SET
                    description = EXCLUDED.description,
                    avg_price   = EXCLUDED.avg_price;
                """,
                (
                    rest_id,
                    item.get("name"),
                    item.get("description"),
                    item.get("avg_price"),
                ),
            )

        conn.commit()
        return rest_id


def bulk_insert_restaurants(rows):
    if not rows:
        return 0

    cols = [
        "name",
        "description",
        "location",
        "hours",
        "category",
        "avg_price",
        "latitude",
        "longitude",
        "picture",
        "yelp_rating",
        "website_url",
    ]
    sql = f"""
        INSERT INTO public.restaurants ({",".join(cols)})
        VALUES %s
        ON CONFLICT (name, location) DO UPDATE SET
            description = EXCLUDED.description,
            hours       = EXCLUDED.hours,
            category    = EXCLUDED.category,
            avg_price   = EXCLUDED.avg_price,
            latitude    = EXCLUDED.latitude,
            longitude   = EXCLUDED.longitude,
            picture     = EXCLUDED.picture,
            yelp_rating = EXCLUDED.yelp_rating,
            website_url = EXCLUDED.website_url;
    """
    values = [tuple(r.get(c) for c in cols) for r in rows]

    with get_conn() as conn, conn.cursor() as cur:
        execute_values(cur, sql, values)
        conn.commit()
        return len(rows)


def bulk_upsert_menu_items(restaurant_id, items):
    if not items:
        return 0

    sql = """
        INSERT INTO public.menu_items (restaurant_id, name, description, avg_price)
        VALUES %s
        ON CONFLICT (restaurant_id, lower(name)) DO UPDATE SET
            description = EXCLUDED.description,
            avg_price   = EXCLUDED.avg_price;
    """
    values = [(restaurant_id,
               i.get("name"),
               i.get("description"),
               i.get("avg_price")) for i in items]

    with get_conn() as conn, conn.cursor() as cur:
        execute_values(cur, sql, values)
        conn.commit()
        return len(items)


if __name__ == "__main__":
    create_restaurants_table()
    migrate_restaurant_new_columns()
    create_menu_items_table()
    create_users_table()
    ensure_restaurants_uniqueness()
    ensure_menu_items_uniqueness()
    print("Tables and indexes ensured.")