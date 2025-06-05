import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import DATABASE_CONFIG
import pymysql
from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

def get_database_connection():
    """Get a database connection with retry logic"""
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            connection = pymysql.connect(
                host=DATABASE_CONFIG['host'],
                user=DATABASE_CONFIG['user'],
                password=DATABASE_CONFIG['password'],
                database=DATABASE_CONFIG['database'],
                port=DATABASE_CONFIG['port'],
                connect_timeout=5
            )
            # Test the connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print(f"Database connection successful to {DATABASE_CONFIG['host']}!")
            return connection
        except pymysql.Error as e:
            retry_count += 1
            print(f"Database connection attempt {retry_count} failed: {str(e)}")
            if retry_count == max_retries:
                raise Exception(f"Failed to connect to database after {max_retries} attempts: {str(e)}")
            time.sleep(5)  # Wait 5 seconds before retrying

def check_user_cred(username: str, password: str) -> bool:
    """Check user credentials"""
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            # For demo purposes, allow a test user
            if username == "testuser" and password == "testpassword":
                return True
                
            # Check real user credentials
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE username = %s AND password = %s",
                (username, password)
            )
            result = cursor.fetchone()[0]
            return result > 0
    except Exception as e:
        print(f"Error checking credentials: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def create_tables_if_not_exist():
    """Create necessary database tables"""
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
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
            connection.commit()
            print("Tables checked/created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()

# Only try to create tables if this module is run directly
if __name__ == "__main__":
    create_tables_if_not_exist()