# exam_service.py

from db.connection import get_connection
from mysql.connector import Error
from datetime import datetime


def compute_exam_clearance(exam_id):
    """
    Computes clearance for all students for a given exam.
    Uses structured flags from student_fee_obligations.
    Optimized: fetches payments in batch, commits once.
    """

    summary = {
        "total_students": 0,
        "cleared": 0,
        "blocked": 0,
        "details": []
    }

    conn = get_connection()
    if not conn:
        return {"error": "Database connection failed"}

    try:
        cursor = conn.cursor(dictionary=True)

        # 1️⃣ Get exam details
        cursor.execute("SELECT * FROM exams WHERE exam_id=%s", (exam_id,))
        exam = cursor.fetchone()
        if not exam:
            return {"error": "Exam not found"}

        semester = exam["semester"]
        academic_year = exam["academic_year"]

        # 2️⃣ Get active students
        cursor.execute("""
            SELECT student_id, reg_no, full_name
            FROM students
            WHERE status='ACTIVE'
        """)
        students = cursor.fetchall()
        summary["total_students"] = len(students)

        for student in students:
            student_id = student["student_id"]

            # 3️⃣ Get obligations for this semester/year
            cursor.execute("""
                SELECT
                    sfo.obligation_id,
                    fs.amount AS expected_amount,
                    sfo.flag_cheating,
                    sfo.flag_duplicate,
                    sfo.flag_mismatch
                FROM student_fee_obligations sfo
                JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
                WHERE sfo.student_id=%s
                  AND fs.semester=%s
                  AND sfo.academic_year=%s
            """, (student_id, semester, academic_year))

            obligations = cursor.fetchall()
            if not obligations:
                # Skip if no obligations
                continue

            # 4️⃣ Fetch approved payments in batch
            obligation_ids = [o["obligation_id"] for o in obligations]
            format_strings = ','.join(['%s'] * len(obligation_ids))
            cursor.execute(f"""
                SELECT p.obligation_id, SUM(p.amount_paid) AS paid_sum
                FROM payments p
                JOIN finance_verifications fv
                    ON fv.obligation_id = p.obligation_id
                WHERE fv.decision='APPROVED'
                  AND p.obligation_id IN ({format_strings})
                GROUP BY p.obligation_id
            """, tuple(obligation_ids))
            payment_rows = cursor.fetchall()
            payment_map = {row["obligation_id"]: float(row["paid_sum"]) for row in payment_rows}

            # 5️⃣ Compute total_paid and check flags
            total_expected = sum(float(o["expected_amount"]) for o in obligations)
            total_paid = sum(payment_map.get(o["obligation_id"], 0.0) for o in obligations)

            blocked_by_flags = any(
                o["flag_cheating"] == 1 or
                o["flag_duplicate"] == 1 or
                o["flag_mismatch"] == 1
                for o in obligations
            )

            # 6️⃣ Decide clearance status
            if total_paid >= total_expected and not blocked_by_flags:
                clearance_status = "CLEARED"
                reason = f"Paid {total_paid} / Required {total_expected}"
                summary["cleared"] += 1
            else:
                clearance_status = "BLOCKED"
                reason = f"Paid {total_paid} / Required {total_expected}; Flags present: {blocked_by_flags}"
                summary["blocked"] += 1

            # 7️⃣ Insert / update exam_clearance
            cursor.execute("""
                INSERT INTO exam_clearance
                (student_id, exam_id, clearance_status, reason, checked_at)
                VALUES (%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    clearance_status=%s,
                    reason=%s,
                    checked_at=%s
            """, (
                student_id, exam_id, clearance_status, reason, datetime.now(),
                clearance_status, reason, datetime.now()
            ))

            summary["details"].append({
                "student_id": student_id,
                "reg_no": student["reg_no"],
                "full_name": student["full_name"],
                "status": clearance_status,
                "reason": reason
            })

        # Commit once after all students processed
        conn.commit()
        return summary

    except Error as e:
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()


class ExamService:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def update_exam_clearance(self, student_id, exam_id):
        """
        Update exam clearance for a student based on payments and structured flags.
        """
        try:
            # Fetch obligations
            self.cursor.execute("""
                SELECT obligation_id, flag_cheating, flag_duplicate, flag_mismatch
                FROM student_fee_obligations
                WHERE student_id=%s
            """, (student_id,))
            obligations = self.cursor.fetchall()

            if not obligations:
                return "NO_OBLIGATIONS"

            # Fetch approved payments
            obligation_ids = [o["obligation_id"] for o in obligations]
            format_strings = ','.join(['%s'] * len(obligation_ids))
            self.cursor.execute(f"""
                SELECT p.obligation_id, SUM(p.amount_paid) AS paid_sum
                FROM payments p
                JOIN finance_verifications fv
                    ON fv.obligation_id = p.obligation_id
                WHERE fv.decision='APPROVED'
                  AND p.obligation_id IN ({format_strings})
                GROUP BY p.obligation_id
            """, tuple(obligation_ids))
            payment_rows = self.cursor.fetchall()
            payment_map = {row["obligation_id"]: float(row["paid_sum"]) for row in payment_rows}

            total_paid = sum(payment_map.get(o["obligation_id"], 0.0) for o in obligations)
            blocked_by_flags = any(
                o["flag_cheating"] == 1 or
                o["flag_duplicate"] == 1 or
                o["flag_mismatch"] == 1
                for o in obligations
            )

            # Compute total expected
            self.cursor.execute("""
                SELECT SUM(fs.amount) AS total_expected
                FROM student_fee_obligations sfo
                JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
                WHERE sfo.student_id=%s
            """, (student_id,))
            total_expected = float(self.cursor.fetchone()["total_expected"] or 0.0)

            # Decide status
            if total_paid >= total_expected and not blocked_by_flags:
                clearance_status = "CLEARED"
                reason = f"Paid {total_paid} / Required {total_expected}"
            else:
                clearance_status = "BLOCKED"
                reason = f"Paid {total_paid} / Required {total_expected}; Flags present: {blocked_by_flags}"

            # Update exam_clearance
            self.cursor.execute("""
                UPDATE exam_clearance
                SET clearance_status=%s,
                    reason=%s,
                    checked_at=NOW()
                WHERE student_id=%s AND exam_id=%s
            """, (clearance_status, reason, student_id, exam_id))
            self.conn.commit()

            return clearance_status

        except Error as e:
            return f"ERROR: {str(e)}"
