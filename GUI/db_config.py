"""
Database connection module for GUI
Connects to the same MySQL database as the backend
"""
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables from backend
load_dotenv('/home/admin_perfect/my_PY_PROJ/KIUT_FEE_TRACKER/.env')

def get_connection():
    """
    Returns a live MySQL connection.
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        if conn.is_connected():
            return conn
        return None
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def execute_query(query, params=None, fetch=False):
    """
    Execute a query and return results if needed.
    
    Args:
        query: SQL query string
        params: Tuple of parameters
        fetch: If True, fetch and return results
    
    Returns:
        List of results if fetch=True, else True/False
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Database error: {e}")
        return None


def execute_many(query, data_list):
    """
    Execute a query with multiple data sets.
    
    Args:
        query: SQL query string
        data_list: List of tuples with data
    
    Returns:
        True if successful, None if error
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.executemany(query, data_list)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Database error: {e}")
        return None


def get_last_insert_id():
    """Get the last inserted ID"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT LAST_INSERT_ID()")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else None
    except Error as e:
        print(f"Error getting last insert ID: {e}")
        return None

