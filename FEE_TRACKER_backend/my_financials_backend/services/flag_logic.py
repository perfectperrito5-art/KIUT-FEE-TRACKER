# flag_logic.py

from db.connection import get_connection
import json

class FlagLogic:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor(dictionary=True)

    def update_flags(self, student_id, obligation_id, flags):
        """
        Update the structured flags in student_fee_obligations based on receipt analysis.
        flags: list of strings ['DUPLICATE_RECEIPT', 'AMOUNT_MISMATCH', ...]
        """
        # Initialize flags
        flag_cheating = 1 if 'CHEATING_SUSPECTED' in flags else 0
        flag_duplicate = 1 if 'DUPLICATE_RECEIPT' in flags else 0
        flag_mismatch = 1 if any(f in flags for f in ['AMOUNT_MISMATCH', 'NAME_MISMATCH', 'ID_MISMATCH']) else 0

        try:
            self.cursor.execute("""
                UPDATE student_fee_obligations
                SET flag_cheating=%s,
                    flag_duplicate=%s,
                    flag_mismatch=%s
                WHERE student_id=%s AND obligation_id=%s
            """, (
                flag_cheating,
                flag_duplicate,
                flag_mismatch,
                student_id,
                obligation_id
            ))
            self.conn.commit()
            return {"success": True, "message": "Flags updated"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def determine_flags(self, receipt_flags):
        """
        Optional helper: convert receipt flags JSON string to structured flag list.
        """
        if not receipt_flags:
            return []
        if isinstance(receipt_flags, str):
            import json
            return json.loads(receipt_flags)
        return receipt_flags
