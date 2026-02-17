# Example simulation
from my_financials_backend.services.receipt_service import ReceiptService
from my_financials_backend.services.exam_service import ExamService

receipt_svc = ReceiptService()
exam_svc = ExamService()

# 1. Student submits receipt
result = receipt_svc.submit_receipt(
    student_id=1,
    obligation_id=5,
    receipt_path="receipts/2026_sem1.jpg",
    amount_paid=1200.00,
    reference_no="TXN123456",
    payment_date="2026-02-10",
    student_name="Perfect User",
    student_reg_no="CS2026001"
)
print("Receipt submission result:", result)

# 2. Update exam clearance automatically
status = exam_svc.update_exam_clearance(student_id=1, exam_id=3)
print("Updated exam clearance status:", status)
