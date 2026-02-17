# services/payment_service.py
from db.connection import get_connection
from mysql.connector import Error
from datetime import datetime

# allowed methods
ALLOWED_METHODS = ['WAKALA/CASH', 'BANK', 'MOBILE_BANKING']

def submit_payment(student_id, obligation_id, amount, method, reference_no):
    """
    Handles a single payment submission.
    Returns dict with status, message, flags
    """
    feedback = {
        "status": None,
        "message": "",
        "flags": []
    }

    # Basic validation
    if method not in ALLOWED_METHODS:
        feedback["status"] = "error"
        feedback["message"] = f"Invalid payment method: {method}"
        return feedback

    if amount <= 0:
        feedback["status"] = "error"
        feedback["message"] = f"Amount must be positive: {amount}"
        return feedback

    conn = get_connection()
    if not conn:
        feedback["status"] = "error"
        feedback["message"] = "Database connection failed"
        return feedback

    try:
        cursor = conn.cursor(dictionary=True)

        # 1️⃣ Check expected obligation amount
        cursor.execute("""
            SELECT sfo.obligation_id, fs.amount AS expected_amount, sfo.is_cleared
            FROM student_fee_obligations sfo
            JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            WHERE sfo.obligation_id=%s AND sfo.student_id=%s
        """, (obligation_id, student_id))
        obligation = cursor.fetchone()
        if not obligation:
            feedback["status"] = "error"
            feedback["message"] = "Obligation not found for this student"
            return feedback

        expected_amount = float(obligation["expected_amount"])
        cleared = obligation["is_cleared"]

        if cleared:
            feedback["status"] = "error"
            feedback["message"] = "This obligation is already cleared"
            return feedback

        # 2️⃣ Check for duplicate reference_no
        cursor.execute("""
            SELECT * FROM payments
            WHERE obligation_id=%s AND reference_no=%s
        """, (obligation_id, reference_no))
        duplicate = cursor.fetchone()
        if duplicate:
            feedback["status"] = "warning"
            feedback["message"] = "Duplicate payment reference detected"
            feedback["flags"].append("DUPLICATE_REFERENCE")
            # Optionally: still allow insert or block
            return feedback

        # 3️⃣ Insert payment
        cursor.execute("""
            INSERT INTO payments (obligation_id, amount_paid, payment_date, method, reference_no, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            obligation_id,
            amount,
            datetime.today().date(),
            method,
            reference_no,
            datetime.now()
        ))
        conn.commit()

        # 4️⃣ Check for amount mismatch
        if amount < expected_amount:
            feedback["flags"].append("UNDERPAID")
            feedback["message"] = f"Payment received, but underpaid: Expected {expected_amount}, Paid {amount}"
            feedback["status"] = "warning"
        elif amount > expected_amount:
            feedback["flags"].append("OVERPAID")
            feedback["message"] = f"Payment received, but overpaid: Expected {expected_amount}, Paid {amount}"
            feedback["status"] = "warning"
        else:
            feedback["status"] = "success"
            feedback["message"] = f"Payment received ✅: {amount} matches expected {expected_amount}"

        return feedback

    except Error as e:
        feedback["status"] = "error"
        feedback["message"] = str(e)
        return feedback

    finally:
        cursor.close()
        conn.close()
