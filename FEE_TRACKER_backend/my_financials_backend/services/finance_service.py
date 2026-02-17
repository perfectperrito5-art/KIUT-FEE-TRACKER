# finance_service.py

from db.connection import get_connection
from mysql.connector import Error

class FinanceService:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def list_flagged_receipts(self):
        """
        Returns all receipts that have any flags for finance review.
        Includes structured flags for easier processing.
        """
        try:
            self.cursor.execute("""
                SELECT
                    p.payment_id,
                    s.full_name,
                    s.reg_no,
                    p.amount_paid,
                    p.receipt_path,
                    p.receipt_flags,
                    p.payment_date
                FROM payments p
                JOIN student_fee_obligations sfo ON p.obligation_id = sfo.obligation_id
                JOIN students s ON sfo.student_id = s.student_id
                WHERE p.receipt_flags IS NOT NULL
            """)
            return self.cursor.fetchall()
        except Error as e:
            return {"error": str(e)}

    def approve_receipt(self, payment_id):
        """
        Approve a flagged receipt manually.
        Updates finance_verifications table and marks as approved.
        """
        try:
            # Ensure a verification record exists
            self.cursor.execute("""
                INSERT INTO finance_verifications (obligation_id, decision, verified_at)
                SELECT obligation_id, 'APPROVED', NOW()
                FROM payments
                WHERE payment_id = %s
                ON DUPLICATE KEY UPDATE decision='APPROVED', verified_at=NOW()
            """, (payment_id,))
            self.conn.commit()
            return {"success": True, "message": "Receipt approved"}
        except Error as e:
            return {"error": str(e)}

    def reject_receipt(self, payment_id, comment="Rejected by finance"):
        """
        Reject a flagged receipt manually.
        Updates finance_verifications table with rejection comment.
        """
        try:
            # Ensure a verification record exists
            self.cursor.execute("""
                INSERT INTO finance_verifications (obligation_id, decision, comment, verified_at)
                SELECT obligation_id, 'REJECTED', %s, NOW()
                FROM payments
                WHERE payment_id = %s
                ON DUPLICATE KEY UPDATE
                    decision='REJECTED',
                    comment=%s,
                    verified_at=NOW()
            """, (comment, payment_id, comment))
            self.conn.commit()
            return {"success": True, "message": "Receipt rejected"}
        except Error as e:
            return {"error": str(e)}

    def get_payment_flags(self, payment_id):
        """
        Returns structured flags for a specific payment.
        Useful for automatic exam clearance checks.
        """
        try:
            self.cursor.execute("""
                SELECT receipt_flags
                FROM payments
                WHERE payment_id=%s
            """, (payment_id,))
            row = self.cursor.fetchone()
            if row and row["receipt_flags"]:
                import json
                return json.loads(row["receipt_flags"])
            return []
        except Error as e:
            return {"error": str(e)}
