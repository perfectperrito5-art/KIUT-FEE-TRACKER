-- Migration to add year_of_study to exam_clearance_fees table
-- This allows different exam clearance fees for different years within the same programme
-- e.g., BCS Year 2 might have different exam clearance fees than BCS Year 3

USE `My_Financials`;

-- Add year_of_study column to exam_clearance_fees table (if not exists)
-- Use a stored procedure to avoid "Duplicate column name" error
DELIMITER //
CREATE PROCEDURE add_year_of_study_column_if_not_exists()
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'My_Financials' 
        AND TABLE_NAME = 'exam_clearance_fees' 
        AND COLUMN_NAME = 'year_of_study'
    ) THEN
        ALTER TABLE `exam_clearance_fees` 
        ADD COLUMN `year_of_study` int NULL DEFAULT NULL AFTER `programme_id`,
        ADD INDEX `idx_programme_year` (`programme_id`, `year_of_study`);
    END IF;
END //
DELIMITER ;

CALL add_year_of_study_column_if_not_exists();
DROP PROCEDURE IF EXISTS add_year_of_study_column_if_not_exists;

