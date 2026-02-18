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
-- Temporary view structure for view `v_student_verification_status`
--

DROP TABLE IF EXISTS `v_student_verification_status`;
/*!50001 DROP VIEW IF EXISTS `v_student_verification_status`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_student_verification_status` AS SELECT 
 1 AS `obligation_id`,
 1 AS `decision`,
 1 AS `comment`,
 1 AS `verified_at`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_student_financial_summary`
--

DROP TABLE IF EXISTS `v_student_financial_summary`;
/*!50001 DROP VIEW IF EXISTS `v_student_financial_summary`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_student_financial_summary` AS SELECT 
 1 AS `student_id`,
 1 AS `reg_no`,
 1 AS `full_name`,
 1 AS `total_required`,
 1 AS `total_paid`,
 1 AS `total_balance`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_student_fee_obligation_status`
--

DROP TABLE IF EXISTS `v_student_fee_obligation_status`;
/*!50001 DROP VIEW IF EXISTS `v_student_fee_obligation_status`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_student_fee_obligation_status` AS SELECT 
 1 AS `obligation_id`,
 1 AS `student_id`,
 1 AS `academic_year`,
 1 AS `obligation_amount`,
 1 AS `total_paid`,
 1 AS `balance`,
 1 AS `is_cleared`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_exam_financial_eligibility`
--

DROP TABLE IF EXISTS `v_exam_financial_eligibility`;
/*!50001 DROP VIEW IF EXISTS `v_exam_financial_eligibility`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_exam_financial_eligibility` AS SELECT 
 1 AS `student_id`,
 1 AS `exam_id`,
 1 AS `eligibility_status`,
 1 AS `reason`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_student_total_paid`
--

DROP TABLE IF EXISTS `v_student_total_paid`;
/*!50001 DROP VIEW IF EXISTS `v_student_total_paid`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_student_total_paid` AS SELECT 
 1 AS `obligation_id`,
 1 AS `total_paid`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `v_student_verification_status`
--

/*!50001 DROP VIEW IF EXISTS `v_student_verification_status`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_student_verification_status` AS select `fv`.`obligation_id` AS `obligation_id`,`fv`.`decision` AS `decision`,`fv`.`comment` AS `comment`,`fv`.`verified_at` AS `verified_at` from (`finance_verifications` `fv` join (select `finance_verifications`.`obligation_id` AS `obligation_id`,max(`finance_verifications`.`verified_at`) AS `last_verified` from `finance_verifications` group by `finance_verifications`.`obligation_id`) `last_fv` on(((`fv`.`obligation_id` = `last_fv`.`obligation_id`) and (`fv`.`verified_at` = `last_fv`.`last_verified`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_student_financial_summary`
--

/*!50001 DROP VIEW IF EXISTS `v_student_financial_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_student_financial_summary` AS select `s`.`student_id` AS `student_id`,`s`.`reg_no` AS `reg_no`,`s`.`full_name` AS `full_name`,sum(`fs`.`amount`) AS `total_required`,sum(coalesce(`vtp`.`total_paid`,0)) AS `total_paid`,(sum(`fs`.`amount`) - sum(coalesce(`vtp`.`total_paid`,0))) AS `total_balance` from (((`students` `s` join `student_fee_obligations` `sfo` on((`s`.`student_id` = `sfo`.`student_id`))) join `fee_structures` `fs` on((`sfo`.`fee_id` = `fs`.`fee_id`))) left join `v_student_total_paid` `vtp` on((`sfo`.`obligation_id` = `vtp`.`obligation_id`))) group by `s`.`student_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_student_fee_obligation_status`
--

/*!50001 DROP VIEW IF EXISTS `v_student_fee_obligation_status`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_student_fee_obligation_status` AS select `sfo`.`obligation_id` AS `obligation_id`,`sfo`.`student_id` AS `student_id`,`sfo`.`academic_year` AS `academic_year`,`fs`.`amount` AS `obligation_amount`,coalesce(`vtp`.`total_paid`,0) AS `total_paid`,(`fs`.`amount` - coalesce(`vtp`.`total_paid`,0)) AS `balance`,`sfo`.`is_cleared` AS `is_cleared` from ((`student_fee_obligations` `sfo` join `fee_structures` `fs` on((`sfo`.`fee_id` = `fs`.`fee_id`))) left join `v_student_total_paid` `vtp` on((`sfo`.`obligation_id` = `vtp`.`obligation_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_exam_financial_eligibility`
--

/*!50001 DROP VIEW IF EXISTS `v_exam_financial_eligibility`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_exam_financial_eligibility` AS select `s`.`student_id` AS `student_id`,`e`.`exam_id` AS `exam_id`,(case when (`vsfos`.`balance` <= 0) then 'ELIGIBLE' when (`vsvs`.`decision` = 'APPROVED') then 'ELIGIBLE' else 'NOT_ELIGIBLE' end) AS `eligibility_status`,(case when (`vsfos`.`balance` <= 0) then 'FULLY PAID' when (`vsvs`.`decision` = 'APPROVED') then 'FINANCE OVERRIDE' else 'OUTSTANDING BALANCE' end) AS `reason` from (((`students` `s` join `exams` `e`) left join `v_student_fee_obligation_status` `vsfos` on((`s`.`student_id` = `vsfos`.`student_id`))) left join `v_student_verification_status` `vsvs` on((`vsfos`.`obligation_id` = `vsvs`.`obligation_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_student_total_paid`
--

/*!50001 DROP VIEW IF EXISTS `v_student_total_paid`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_student_total_paid` AS select `payments`.`obligation_id` AS `obligation_id`,sum(`payments`.`amount_paid`) AS `total_paid` from `payments` group by `payments`.`obligation_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-18 15:36:39
