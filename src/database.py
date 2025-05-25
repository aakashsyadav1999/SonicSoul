import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Import the database configuration from the config file
from src.config import DATABASE_CONFIG

# Use PyMySQL instead of mysql-connector-python
import pymysql
from pydantic import BaseModel, ValidationError

# Define a function to create tables if they don't exist
def create_tables_if_not_exist(conn):
    try:
        with conn.cursor() as cursor:
            # Create Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Insert a default test user if it doesn't exist
            cursor.execute("""
                INSERT IGNORE INTO users (username, password) VALUES (%s, %s)
            """, ("testuser", "testpassword"))
            conn.commit()
            print("Tables checked/created successfully.")
    except pymysql.MySQLError as e:
        print(f"Error creating tables: {e}")
        # Depending on the desired behavior, you might want to raise the exception
        # or handle it in a way that allows the application to continue or exit gracefully.
        raise

class UserLogin(BaseModel):
    username: str
    password: str

def get_database_connection():
    connection = pymysql.connect(
        host=DATABASE_CONFIG['host'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password'],
        database=DATABASE_CONFIG['database'],
        port=DATABASE_CONFIG['port'] # Ensure port is used from config
    )
    # Call the function to create tables
    #create_tables_if_not_exist(connection) # Uncomment this line if you want to create tables on connection
    return connection

connection = get_database_connection()
cursor = connection.cursor()

# Example query to fetch data from the database
def fetch_music_columns():
    query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{DATABASE_CONFIG['table']}'"
    cursor.execute(query)
    columns = [row[0] for row in cursor.fetchall()]
    return columns

def check_user_cred(username, password):
    try:
        # Validate the input data
        UserLogin(username=username, password=password)
    except ValidationError as e:
        print(f"Validation error: {e}")
        return False
    # Check if the user exists in the database
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    return user is not None


# Example usage
if __name__ == "__main__":
    # Fetch music columns
    columns = fetch_music_columns()
    print("Music Columns:", columns)

    # Check user credentials
    username = "testuser"
    password = "testpassword"
    if check_user_cred(username, password):
        print("User credentials are valid.")
    else:
        print("Invalid user credentials.")
    
    # Close the database connection
    cursor.close()
    connection.close()