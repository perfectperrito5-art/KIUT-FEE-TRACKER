# test_exam_clearance.py
from services.exam_service import compute_exam_clearance

exam_id = 3

result = compute_exam_clearance(exam_id)
print(result)
