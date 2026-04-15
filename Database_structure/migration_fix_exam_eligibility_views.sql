-- ============================================================================
-- Migration: Fix Exam Clearance Eligibility Views
-- ============================================================================
-- Purpose: Fix the exam clearance report bug where admin dashboard shows
--          ELIGIBLE for students who haven't paid the required amount.
--
-- Root Cause:
-- 1. v_student_total_paid was counting ALL payments including unverified ones
-- 2. v_exam_financial_eligibility wasn't properly filtering by academic_year
--
-- This fix ensures:
-- 1. Only verified payments (receipt_checked = 1) are counted
-- 2. The eligibility view properly joins on academic_year
--
-- Run this migration against your MySQL database to fix the bug
-- ============================================================================

USE My_Financials;

-- ============================================================================
-- Step 1: Fix v_student_total_paid view
-- ============================================================================
-- This view now filters by receipt_checked = 1 to only count VERIFIED payments
-- This matches the logic used in student dashboard

DROP VIEW IF EXISTS v_student_total_paid;

CREATE VIEW v_student_total_paid AS 
SELECT 
    payments.obligation_id AS obligation_id,
    SUM(payments.amount_paid) AS total_paid
FROM payments
WHERE payments.receipt_checked = 1
GROUP BY payments.obligation_id;

-- ============================================================================
-- Step 2: Fix v_exam_financial_eligibility view
-- ============================================================================
-- This view now properly matches the exam's academic_year with the 
-- student's fee obligation academic_year

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

-- ============================================================================
-- Verification: Check the views are working correctly
-- ============================================================================

-- Test: Check total paid for a specific obligation (should only show verified payments)
-- SELECT * FROM v_student_total_paid WHERE obligation_id = YOUR_OBLIGATION_ID;

-- Test: Check exam eligibility for a specific student
-- SELECT * FROM v_exam_financial_eligibility WHERE student_id = YOUR_STUDENT_ID;

-- ============================================================================
-- End of Migration
-- ============================================================================

