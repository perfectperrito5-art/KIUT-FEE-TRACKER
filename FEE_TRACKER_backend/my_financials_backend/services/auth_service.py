from database import get_connection


def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, role FROM users WHERE username=%s AND password=%s",
        (username, password)
    )

    user = cursor.fetchone()

    conn.close()

    if user:
        return {
            "status": True,
            "user_id": user[0],
            "role": user[1]
        }
    else:
        return {
            "status": False
        }
