import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Import the database configuration from the config file
from src.config import DATABASE_CONFIG

# Use the DATABASE_CONFIG dictionary to establish a connection
# Example: Establishing a connection using pyodbc
import pyodbc

def get_database_connection():
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DATABASE_CONFIG['server']};"
        f"UID={DATABASE_CONFIG['username']};"
        f"PWD={DATABASE_CONFIG['password']};"
        f"DATABASE={DATABASE_CONFIG['database']}"
    )
    return pyodbc.connect(connection_string)

connection = get_database_connection()
cursor = connection.cursor()

# Example query to fetch data from the database
def fetch_music_columns():
    query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{DATABASE_CONFIG['table']}'"
    cursor.execute(query)
    columns = [row[0] for row in cursor.fetchall()]
    return columns

def check_user_cred(username, password):
    query = "SELECT * FROM Users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    return user is not None
