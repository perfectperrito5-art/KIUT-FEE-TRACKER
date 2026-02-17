# main.py
from db.connection import get_connection

def test_db():
    conn = get_connection()
    if conn:
        print("Connected to DB successfully!")
        conn.close()
    else:
        print("Connection failed.")

if __name__ == "__main__":
    test_db()
