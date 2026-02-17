# test_payment.py
from services.payment_service import submit_payment

def run_test():
    # Example test student + obligation (replace with real IDs in your DB)
    student_id = 1
    obligation_id = 1

    # 1️⃣ Normal exact payment
    feedback = submit_payment('BCS/3222/123/DT', obligation_id, 1200.0, 'BANK', 'REF001')
    print("Test 1 – Exact Payment:", feedback)

    # 2️⃣ Underpayment
    feedback = submit_payment('ARDHI/3234/DT', obligation_id, 1000.0, 'BANK', 'REF002')
    print("Test 2 – Underpayment:", feedback)

    # 3️⃣ Overpayment
    feedback = submit_payment(student_id, obligation_id, 1300.0, 'BANK', 'REF003')
    print("Test 3 – Overpayment:", feedback)

    # 4️⃣ Duplicate reference
    feedback = submit_payment(student_id, obligation_id, 1200.0, 'BANK', 'REF001')
    print("Test 4 – Duplicate Reference:", feedback)

    # 5️⃣ Invalid method
    feedback = submit_payment(student_id, obligation_id, 1200.0, 'CREDIT_CARD', 'REF004')
    print("Test 5 – Invalid Method:", feedback)

if __name__ == "__main__":
    run_test()
