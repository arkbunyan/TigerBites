"""
TigerBites DB Manager
- Handles DB connection
- Ensures schema exists 
- Provides insert helpers

python -m data_management.db_manager
"""

import os
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load .env from repo root if possible, else fall back to CWD
ROOT_ENV = Path(__file__).resolve().parents[1] / ".env"
if ROOT_ENV.exists():
    load_dotenv(ROOT_ENV)
else:
    load_dotenv()

DATABASE_URL = os.getenv("TB_DATABASE_URL")


def get_conn():
    if not DATABASE_URL:
        raise RuntimeError(
            "TB_DATABASE_URL not set. Add it to your .env or environment."
        )
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
        longitude   DOUBLE PRECISION
    );
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(ddl)
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
        netid TEXT,
        fullname  TEXT,
        email TEXT,
        firstname TEXT,
        favorite_cuisine TEXT,
        fav_restaurant uuid REFERENCES public.restaurants(id)
    );
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(ddl)
        conn.commit()


def ensure_restaurants_uniqueness():
    # Avoid duplicates on repeated imports
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


def insert_restaurant(restaurant_data, menu_data=None):
    """
    restaurant_data: dict with keys
      name, description, location, hours, category, avg_price, latitude, longitude
    menu_data: list of dicts with keys name, description, avg_price (optional)
    """
    if menu_data is None:
        menu_data = []

    upsert = """
        INSERT INTO public.restaurants
            (name, description, location, hours, category, avg_price, latitude, longitude)
        VALUES
            (%(name)s, %(description)s, %(location)s, %(hours)s, %(category)s,
             %(avg_price)s, %(latitude)s, %(longitude)s)
        ON CONFLICT (name, location) DO UPDATE SET
            description = EXCLUDED.description,
            hours       = EXCLUDED.hours,
            category    = EXCLUDED.category,
            avg_price   = EXCLUDED.avg_price,
            latitude    = EXCLUDED.latitude,
            longitude   = EXCLUDED.longitude
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
    """
    rows: list[dict] with keys
      name, description, location, hours, category, avg_price, latitude, longitude
    Returns count of processed rows.
    """
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
            longitude   = EXCLUDED.longitude;
    """
    values = [tuple(r.get(c) for c in cols) for r in rows]

    with get_conn() as conn, conn.cursor() as cur:
        execute_values(cur, sql, values)
        conn.commit()
        return len(rows)


if __name__ == "__main__":
    create_restaurants_table()
    create_menu_items_table()
    create_users_table()
    ensure_restaurants_uniqueness()
    print("Tables ensured.")
