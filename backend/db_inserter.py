import sqlite3
import contextlib

DATABASE_URL = 'file:proto_db.sqlite?mode=rw'
# Connect to (or create) the database file
try:
    with sqlite3.connect(DATABASE_URL, isolation_level=None,
            uri=True) as connection:

        with contextlib.closing(connection.cursor()) as cursor:

            # Create the table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                hours TEXT,
                avg_price REAL
            );
            """)

            # Optionally, insert some example rows
            cursor.executemany("""
            INSERT INTO restaurants (name, category, hours, avg_price)
            VALUES (?, ?, ?, ?);
            """, [
                ("Chuck's Spring Street Cafe", "American Cuisine", "11:00 AM - 9:00 PM", 25.50),
                ("Tacoria", "Mexican Cuisine", "12:00 PM - 9:00 PM", 30.00),
                ("Conte's Pizza and Bar", "Bar", "10:00 AM - 8:00 PM", 18.00)
            ])

            # Commit changes and close connection
            connection.commit()
            connection.close()
    
except Exception as e:
    print(f"An error occurred: {e}")    