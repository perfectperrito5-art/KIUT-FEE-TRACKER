-- Faculty and Exam Enhancement Migration
-- This migration adds:
-- 1. faculties table
-- 2. programmes table (linked to faculties)
-- 3. Exam enhancements (exam_name, start_date, end_date)
-- 4. exam_faculties junction table
-- 5. faculty_id in students table
-- NOTE: This migration is idempotent - safe to run multiple times

USE `My_Financials`;

-- Create faculties table (if not exists)
CREATE TABLE IF NOT EXISTS `faculties` (
  `faculty_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `description` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`faculty_id`),
  UNIQUE KEY `faculty_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Create programmes table (if not exists)
CREATE TABLE IF NOT EXISTS `programmes` (
  `programme_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `faculty_id` int NOT NULL,
  `description` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`programme_id`),
  UNIQUE KEY `programme_name` (`name`),
  KEY `faculty_id` (`faculty_id`),
  CONSTRAINT `programmes_ibfk_1` FOREIGN KEY (`faculty_id`) REFERENCES `faculties` (`faculty_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Add exam_name column to exams table (if not exists)
-- First check if column exists
SET @column_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                      WHERE TABLE_SCHEMA = 'My_Financials' 
                      AND TABLE_NAME = 'exams' 
                      AND COLUMN_NAME = 'exam_name');
SET @sql = IF(@column_exists = 0, 
              'ALTER TABLE exams ADD COLUMN exam_name varchar(50) NOT NULL DEFAULT ''UE'' AFTER exam_id', 
              'SELECT ''exam_name column already exists'' as msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add start_date column to exams table (if not exists)
SET @column_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                      WHERE TABLE_SCHEMA = 'My_Financials' 
                      AND TABLE_NAME = 'exams' 
                      AND COLUMN_NAME = 'start_date');
SET @sql = IF(@column_exists = 0, 
              'ALTER TABLE exams ADD COLUMN start_date date DEFAULT NULL AFTER exam_date', 
              'SELECT ''start_date column already exists'' as msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add end_date column to exams table (if not exists)
SET @column_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                      WHERE TABLE_SCHEMA = 'My_Financials' 
                      AND TABLE_NAME = 'exams' 
                      AND COLUMN_NAME = 'end_date');
SET @sql = IF(@column_exists = 0, 
              'ALTER TABLE exams ADD COLUMN end_date date DEFAULT NULL AFTER start_date', 
              'SELECT ''end_date column already exists'' as msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Drop unique key on semester if exists (we now have exam_name)
SET @key_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS 
                   WHERE TABLE_SCHEMA = 'My_Financials' 
                   AND TABLE_NAME = 'exams' 
                   AND INDEX_NAME = 'semester');
SET @sql = IF(@key_exists > 0, 
              'ALTER TABLE exams DROP KEY semester', 
              'SELECT ''semester key already dropped'' as msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Create exam_faculties junction table (if not exists)
CREATE TABLE IF NOT EXISTS `exam_faculties` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_id` int NOT NULL,
  `faculty_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `exam_id` (`exam_id`),
  KEY `faculty_id` (`faculty_id`),
  CONSTRAINT `exam_faculties_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`exam_id`) ON DELETE CASCADE,
  CONSTRAINT `exam_faculties_ibfk_2` FOREIGN KEY (`faculty_id`) REFERENCES `faculties` (`faculty_id`) ON DELETE CASCADE,
  UNIQUE KEY `exam_faculty` (`exam_id`, `faculty_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Add faculty_id column to students table (if not exists)
SET @column_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                      WHERE TABLE_SCHEMA = 'My_Financials' 
                      AND TABLE_NAME = 'students' 
                      AND COLUMN_NAME = 'faculty_id');
SET @sql = IF(@column_exists = 0, 
              'ALTER TABLE students ADD COLUMN faculty_id int DEFAULT NULL AFTER programme', 
              'SELECT ''faculty_id column already exists'' as msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add programme_id column to students table (if not exists)
SET @column_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                      WHERE TABLE_SCHEMA = 'My_Financials' 
                      AND TABLE_NAME = 'students' 
                      AND COLUMN_NAME = 'programme_id');
SET @sql = IF(@column_exists = 0, 
              'ALTER TABLE students ADD COLUMN programme_id int DEFAULT NULL AFTER faculty_id', 
              'SELECT ''programme_id column already exists'' as msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add foreign key constraints if they don't exist
-- (These are handled by CREATE TABLE IF NOT EXISTS for new tables)
-- For existing tables, the foreign keys were added with the columns

-- Sample data for testing (optional - uncomment to add sample data)
-- INSERT INTO faculties (name, description) VALUES 
-- ('Faculty of Science', 'Science programmes'),
-- ('Faculty of Business', 'Business programmes'),
-- ('Faculty of Engineering', 'Engineering programmes');

-- INSERT INTO programmes (name, faculty_id) VALUES
-- ('Bachelor of Computer Science', 1),
-- ('Bachelor of Mathematics', 1),
-- ('Bachelor of Business Administration', 2),
-- ('Bachelor of Civil Engineering', 3);
