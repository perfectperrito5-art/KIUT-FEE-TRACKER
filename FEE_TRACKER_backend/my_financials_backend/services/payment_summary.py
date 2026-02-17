class PaymentSummary:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def total_paid_per_student(self, student_id):
        self.cursor.execute("""
            SELECT SUM(amount_paid) AS total_paid
            FROM payments p
            JOIN student_fee_obligations sfo ON p.obligation_id = sfo.obligation_id
            WHERE sfo.student_id = %s
        """, (student_id,))
        return self.cursor.fetchone()['total_paid'] or 0

    def pending_obligations(self, student_id):
        self.cursor.execute("""
            SELECT sfo.obligation_id, fs.amount, sfo.is_cleared
            FROM student_fee_obligations sfo
            JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            WHERE sfo.student_id = %s AND sfo.is_cleared = FALSE
        """, (student_id,))
        return self.cursor.fetchall()
