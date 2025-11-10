## --------------------------------
## Database Manager Module
## This module provides functionality to connect to a PostgreSQL database
## using credentials stored in environment variables.
## 
## This should be used when we need to update the schema or manage data
## in our PostgreSQL database (stored in the cloud on Heroku)
## --------------------------------


import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
# Default fallback (used if TB_DATABASE_URL is missing)
# NOTE: for testing link is hardcoded, will set .env variable in deployment
DATABASE_URL = os.getenv("TB_DATABASE_URL")

#NOTE: Hardcoded for our specific db schema
# Helper function to create the Restaurants Table
def create_restaurants_table():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                stmt_str = '''
                    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
                    CREATE TABLE IF NOT EXISTS restaurants 
                    (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), 
                    created_at timestamptz NOT NULL DEFAULT now(), 
                    name TEXT, 
                    description TEXT, 
                    location TEXT, 
                    hours TEXT, 
                    category TEXT, 
                    avg_price FLOAT);
                '''
                cur.execute(stmt_str)
                conn.commit()
                print("Table 'restaurants' created successfully.")
    except Exception as e:
        print(f"An error occurred in the creation of the restaurants table; {e}")

# Helper function to create the Menu_Items Table
def create_menu_items_table():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                stmt_str = '''
                    CREATE EXTENSION IF NOT EXISTS "pgcrypto"; 
                    CREATE TABLE IF NOT EXISTS menu_items 
                    (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), 
                    created_at timestamptz NOT NULL DEFAULT now(), 
                    restaurant_id uuid, 
                    name TEXT, 
                    description TEXT, 
                    avg_price FLOAT);
                '''
                cur.execute(stmt_str)
                conn.commit()
                print(f"Table 'menu_items' created successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

# Helper function to create the Users Table
def create_users_table():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                stmt_str = '''
                    CREATE EXTENSION IF NOT EXISTS "pgcrypto"; 
                    CREATE TABLE IF NOT EXISTS users 
                    (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), 
                    created_at timestamptz NOT NULL DEFAULT now(), 
                    netid TEXT, 
                    name TEXT,
                    fav_restaurant uuid REFERENCES restaurants(id));
                '''
                cur.execute(stmt_str)
                conn.commit()
                print(f"Table 'users' created successfully")
    except Exception as e:
        print(f"An error occurred: {e}")
        
# Function for inserting a single row of restaurant data and its corresponding menu data
# Params:
#       - restaurant_data: a dict with the following key/value pairs:
#         {
#           'name': string
#           'description': string
#           'location': string
#           'hours': string
#           'category': string
#           'avg_price': float
#         }
#       - menu_data: A list of dicts, each list item corresponding to a singular menu item
def insert_restaurant(restaurant_data, menu_data):
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                stmt_str = '''
                    INSERT INTO restaurants (name, description, location, hours, category, avg_price) 
                    VALUES (%s, %s, %s, %s, %s, %s) 
                    RETURNING id
                '''
                cur.execute(stmt_str, restaurant_data)
                rest_id = cur.fetchone()[0]
                for item in menu_data:
                    stmt_str = ''' 
                        INSERT INTO menu_items (restaurant_id, name, description, avg_price) 
                        VALUES (%s, %s, %s, %s)
                    '''
                    cur.execute(stmt_str, (
                        rest_id, 
                        item.get('name'), 
                        item.get('description'), 
                        item.get('avg_price')
                    )) 
                conn.commit()
                print("Restaurant data inserted successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    create_restaurants_table()
    create_menu_items_table()
    create_users_table()