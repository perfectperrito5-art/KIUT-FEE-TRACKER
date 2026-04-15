-- Exam Clearance Fees Migration - CORRECTED
-- This migration adds the ability for finance users to set exam clearance fees per programme
-- The exam clearance fee is DIFFERENT from the full yearly/total fee for a programme

USE `My_Financials`;

-- Drop existing table if it exists (to recreate with correct structure)
DROP TABLE IF EXISTS `exam_clearance_fees`;

-- Create exam_clearance_fees table with the CORRECT column names from the actual database
-- This stores the minimum fee required to sit for a specific exam for each programme
CREATE TABLE IF NOT EXISTS `exam_clearance_fees` (
  `exam_fee_id` int NOT NULL AUTO_INCREMENT,
  `exam_name` varchar(100) NOT NULL,
  `semester` varchar(20) NOT NULL,
  `academic_year` varchar(20) NOT NULL,
  `programme_id` int NOT NULL,
  `exam_fee_amount` decimal(12,2) NOT NULL DEFAULT 0.00,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`exam_fee_id`),
  KEY `programme_id` (`programme_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Create view for student exam clearance status with fees (if not exists)
-- This view shows students their exam clearance status and amount remaining
DROP VIEW IF EXISTS v_student_exam_clearance_status;

CREATE VIEW v_student_exam_clearance_status AS
SELECT 
    s.student_id,
    s.reg_no,
    s.full_name,
    s.programme_id,
    p.name AS programme_name,
    ecf.exam_fee_id,
    ecf.exam_name,
    ecf.semester,
    ecf.academic_year,
    ecf.start_date,
    ecf.end_date,
    ecf.exam_fee_amount,
    COALESCE(SUM(pay.amount_paid), 0) AS total_paid_towards_exam,
    CASE 
        WHEN ecf.exam_fee_amount IS NULL THEN 'NOT_SET'
        WHEN COALESCE(SUM(pay.amount_paid), 0) >= ecf.exam_fee_amount THEN 'ELIGIBLE'
        ELSE 'NOT_ELIGIBLE'
    END AS eligibility_status,
    CASE 
        WHEN ecf.exam_fee_amount IS NULL THEN 0
        ELSE GREATEST(0, ecf.exam_fee_amount - COALESCE(SUM(pay.amount_paid), 0))
    END AS amount_remaining
FROM students s
JOIN programmes p ON s.programme_id = p.programme_id
LEFT JOIN exam_clearance_fees ecf ON p.programme_id = ecf.programme_id
LEFT JOIN student_fee_obligations sfo ON s.student_id = sfo.student_id
LEFT JOIN payments pay ON sfo.obligation_id = pay.obligation_id AND pay.receipt_checked = 1
GROUP BY 
    s.student_id,
    s.reg_no,
    s.full_name,
    s.programme_id,
    p.name,
    ecf.exam_fee_id,
    ecf.exam_name,
    ecf.semester,
    ecf.academic_year,
    ecf.start_date,
    ecf.end_date,
    ecf.exam_fee_amount;

-- Note: The exam_programmes table is NOT needed with this structure
-- since exam details are stored directly in exam_clearance_fees

