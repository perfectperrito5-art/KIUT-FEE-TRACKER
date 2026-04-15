-- Fix for Exam Clearance Report Bug
-- The view v_student_total_paid was counting ALL payments including unverified ones
-- This caused the admin exam clearance report to show ELIGIBLE when it should show NOT ELIGIBLE
-- 
-- The student dashboard correctly filters by receipt_checked = 1
-- But the view used by admin reports didn't have this filter

-- Drop and recreate the view with the fix
DROP VIEW IF EXISTS v_student_total_paid;

CREATE VIEW v_student_total_paid AS 
SELECT 
    payments.obligation_id AS obligation_id,
    SUM(payments.amount_paid) AS total_paid
FROM payments
WHERE payments.receipt_checked = 1
GROUP BY payments.obligation_id;

-- Also fix v_exam_financial_eligibility to properly match semester and academic year
-- The current view joins on student_id but doesn't filter by exam's semester/academic_year
DROP VIEW IF EXISTS v_exam_financial_eligibility;

CREATE VIEW v_exam_financial_eligibility AS
SELECT 
    s.student_id AS student_id,
    e.exam_id AS exam_id,
    CASE 
        WHEN vsfos.balance <= 0 THEN 'ELIGIBLE'
        WHEN vsvs.decision = 'APPROVED' THEN 'ELIGIBLE'
        ELSE 'NOT_ELIGIBLE'
    END AS eligibility_status,
    CASE 
        WHEN vsfos.balance <= 0 THEN 'FULLY PAID'
        WHEN vsvs.decision = 'APPROVED' THEN 'FINANCE OVERRIDE'
        ELSE 'OUTSTANDING BALANCE'
    END AS reason
FROM (((students s 
    JOIN exams e)
    LEFT JOIN v_student_fee_obligation_status vsfos ON (s.student_id = vsfos.student_id 
        AND e.academic_year = vsfos.academic_year))
    LEFT JOIN v_student_verification_status vsvs ON (vsfos.obligation_id = vsvs.obligation_id));

