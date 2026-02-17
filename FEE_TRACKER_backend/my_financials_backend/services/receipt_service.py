# services/receipt_service.py

import hashlib
import os
from datetime import datetime
from db.connection import get_connection
from flag_logic import FlagLogic

class ReceiptService:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)
        self.flagger = FlagLogic()  # handle structured flags

    def _compute_file_hash(self, file_path):
        """Compute SHA256 hash of the receipt file"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def submit_receipt(
        self,
        student_id,
        obligation_id,
        receipt_path,
        amount_paid,
        reference_no,
        payment_date,
        student_name,
        student_reg_no
    ):
        """
        Submit a receipt, validate it, generate flags, update DB, and apply structured flags.
        """
        flags = []

        # 1️⃣ Basic validations
        if not receipt_path:
            flags.append("MISSING_FILE")

        if receipt_path:
            # Compute file hash
            file_hash = self._compute_file_hash(receipt_path)

            # File size/type checks
            file_size = os.path.getsize(receipt_path)
            if file_size > 5 * 1024 * 1024:  # 5MB
                flags.append("FILE_TOO_LARGE")

            ext = os.path.splitext(receipt_path)[1].lower()
            if ext not in [".jpg", ".jpeg", ".png", ".pdf"]:
                flags.append("UNSUPPORTED_FILE_TYPE")
        else:
            file_hash = None
            file_size = 0
            ext = None

        # 2️⃣ Fetch obligation info
        self.cursor.execute(
            """
            SELECT sfo.student_id, sfo.fee_id, sfo.is_cleared, fs.amount
            FROM student_fee_obligations sfo
            JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            WHERE sfo.obligation_id = %s
            """,
            (obligation_id,)
        )
        obligation = self.cursor.fetchone()
        if not obligation:
            flags.append("INVALID_OBLIGATION")
            expected_amount = 0
        else:
            expected_amount = float(obligation["amount"])
            if amount_paid != expected_amount:
                flags.append("AMOUNT_MISMATCH")

        # 3️⃣ Check for duplicate receipt
        if file_hash:
            self.cursor.execute(
                "SELECT * FROM payments WHERE obligation_id=%s AND receipt_hash=%s",
                (obligation_id, file_hash)
            )
            duplicate = self.cursor.fetchone()
            if duplicate:
                flags.append("DUPLICATE_RECEIPT")

        # 4️⃣ Compare student info
        self.cursor.execute(
            "SELECT full_name, reg_no FROM students WHERE student_id=%s",
            (student_id,)
        )
        student = self.cursor.fetchone()
        if student_name != student["full_name"]:
            flags.append("NAME_MISMATCH")
        if student_reg_no != student["reg_no"]:
            flags.append("ID_MISMATCH")

        # 5️⃣ Insert payment record
        self.cursor.execute(
            """
            INSERT INTO payments
            (obligation_id, amount_paid, payment_date, method, reference_no,
             receipt_path, receipt_uploaded_at, receipt_checked, receipt_flags,
             receipt_file_size, receipt_file_type, receipt_hash,
             receipt_payment_date, receipt_student_name, receipt_student_id)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                obligation_id,
                amount_paid,
                payment_date,
                "WAKALA/CASH",  # or dynamic
                reference_no,
                receipt_path,
                False,
                str(flags),
                file_size,
                ext.replace(".", "") if ext else None,
                file_hash,
                payment_date,
                student_name,
                student_reg_no
            )
        )
        self.conn.commit()

        # 6️⃣ Update structured flags in student_fee_obligations
        self.flagger.update_flags(student_id, obligation_id, flags)

        return {
            "success": True,
            "flags": flags,
            "message": "Receipt submitted and structured flags updated. Pending finance verification."
        }
