CREATE DATABASE  IF NOT EXISTS `My_Financials` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `My_Financials`;
-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: My_Financials
-- ------------------------------------------------------
-- Server version	8.0.45-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `obligation_id` int NOT NULL,
  `amount_paid` decimal(10,3) NOT NULL,
  `payment_date` date NOT NULL,
  `method` enum('WAKALA/CASH','BANK','MOBILE_BANKING') DEFAULT NULL,
  `reference_no` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `receipt_path` varchar(255) DEFAULT NULL COMMENT 'File path or URL to uploaded receipt',
  `receipt_uploaded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Time student uploaded receipt',
  `receipt_checked` tinyint(1) DEFAULT '0' COMMENT 'If receipt has been verified by system or finance',
  `receipt_flags` json DEFAULT NULL COMMENT 'Array of flags generated for this receipt',
  `receipt_file_size` int DEFAULT NULL COMMENT 'File size in KB or bytes',
  `receipt_file_type` varchar(20) DEFAULT NULL COMMENT 'Image format (jpg, png, pdf)',
  `receipt_ocr_text` text COMMENT 'Optional OCR text for automated comparison',
  `receipt_hash` varchar(64) DEFAULT NULL COMMENT 'SHA256 hash of file to detect duplicates/edits',
  `receipt_reference_no` varchar(50) DEFAULT NULL COMMENT 'Reference number from receipt to validate with system',
  `receipt_payment_date` date DEFAULT NULL COMMENT 'Date from receipt itself',
  `receipt_student_name` varchar(100) DEFAULT NULL COMMENT 'Student name as written on receipt',
  `receipt_student_id` varchar(30) DEFAULT NULL COMMENT 'Student id as written on receipt',
  PRIMARY KEY (`payment_id`),
  KEY `idx_payments_obligation` (`obligation_id`),
  KEY `idx_payments_date` (`payment_date`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`obligation_id`) REFERENCES `student_fee_obligations` (`obligation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-18 15:36:38
