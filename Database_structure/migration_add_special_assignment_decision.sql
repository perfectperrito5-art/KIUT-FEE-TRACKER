-- Migration: Add SPECIAL_ASSIGNMENT to finance_verifications decision enum
-- This fixes the issue where SPECIAL_ASSIGNMENT decision was being rejected
-- Error: Data truncated for column 'decision' at row 1

USE `My_Financials`;

-- Modify the decision column to include SPECIAL_ASSIGNMENT
ALTER TABLE finance_verifications 
MODIFY COLUMN decision ENUM('APPROVED','REJECTED','SPECIAL_ASSIGNMENT') DEFAULT NULL;

