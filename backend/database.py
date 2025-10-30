import sys
import json
import sqlite3
import contextlib

DATABASE_URL = 'file:proto_db.sqlite?mode=ro'

def load_all_restaurants():
    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
            uri=True) as connection:

            with contextlib.closing(connection.cursor()) as cursor:
                # Main Query
                stmt_str = "SELECT * FROM restaurants " 
                cursor.execute(stmt_str, [])
                table = cursor.fetchall()
           
                response = []
                for row in table:   
                    entry = {'name': row[1],
                            'category': row[2],
                            'hours': row[3],
                            'avg_price': row[4]}
                    response.append(entry)
                response = [True, response]
                return response
    except Exception as ex:
        error_message = str(sys.argv[0] + ': ')
        print(f"{error_message} {str(ex)}", file=sys.stderr)
        response = [False, 'A server error occurred. ' +
        'Please contact the system administrator.']
        return response


def restaurant_search(params):

    name = params[0]
    category = params[1]

    try:
        with sqlite3.connect(DATABASE_URL, isolation_level=None,
            uri=True) as connection:

            with contextlib.closing(connection.cursor()) as cursor:
                # Main Query
                stmt_str = "SELECT name, category, hours, avg_price " 
                stmt_str += "FROM restaurants "
                stmt_str += "WHERE name LIKE ? "
                stmt_str += "AND category LIKE ? "
                cursor.execute(stmt_str, ['%' + name + '%', '%' + category + '%'])
                table = cursor.fetchall()
                response = []
                for row in table:
                    entry = {'name': row[0],
                                'category': row[1],
                                'hours': row[2],
                                'avg_price': row[3]}      
                    response.append(entry) 

                response = [True, response]
                return response
    except Exception as ex:
        error_message = str(sys.argv[0] + ': ')
        print(f"{error_message} {str(ex)}", file=sys.stderr)
        response = [False, 'A server error occurred. ' +
        'Please contact the system administrator.']
        return response
