# database.py

import mysql.connector
from mysql.connector import Error
from config import DATABASE_CONFIG

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def execute_query(query, params=None):
    connection = get_db_connection()
    if connection is None:
        return None
    cursor = connection.cursor(buffered=True, dictionary=True)
    try:
        cursor.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
        else:
            connection.commit()
            result = None
    except mysql.connector.Error as err:
        connection.rollback()
        raise err
    finally:
        cursor.close()
        connection.close()
    return result
