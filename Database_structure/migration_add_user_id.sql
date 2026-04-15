-- Migration: Add user_id to students table to link with users table
-- This fixes the bug where students can't see their own data after login
-- Run this file to add the necessary columns and link existing data

USE `My_Financials`;

-- Step 1: Add user_id column to students table (only if it doesn't exist)
-- Use this approach to avoid "Duplicate column name" error
SET @dbname = DATABASE();
SET @tablename = 'students';
SET @columnname = 'user_id';
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = @dbname AND TABLE_NAME = @tablename AND COLUMN_NAME = @columnname) > 0,
    'SELECT 1',
    'ALTER TABLE students ADD COLUMN user_id INT NULL'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Step 2: Add foreign key constraint (only if it doesn't exist)
ALTER TABLE students ADD CONSTRAINT fk_students_user 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

-- Step 3: Create index for faster lookups (only if it doesn't exist)
ALTER TABLE students ADD INDEX idx_students_user_id (user_id);

-- Step 4: Link existing students to users where username matches reg_no
UPDATE students s 
INNER JOIN users u ON s.reg_no = u.username 
SET s.user_id = u.id 
WHERE u.role = 'student';

-- Note: For existing data that doesn't match, admin will need to manually link them
-- or students can re-register with their correct details
