# db/connection.py
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error


load_dotenv()


def get_connection():
    """
    Returns a live MySQL connection.
    Raises an error if connection fails.
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        if conn.is_connected():
            print("✅ MySQL connection successful")
        return conn
    except Error as e:
        print("❌ Error connecting to MySQL:", e)
        return None

if __name__ == "__main__":
    get_connection()
