-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: localhost    Database: task_scheduler
-- ------------------------------------------------------
-- Server version	8.0.36

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `tasks`
--

DROP TABLE IF EXISTS `tasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tasks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `time` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `action` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notification_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `channels` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `event_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `event_sender` varchar(320) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `event_contact` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `event_keyword` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_window_start` date DEFAULT NULL,
  `date_window_end` date DEFAULT NULL,
  `repeat_rule` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `user_id` int NOT NULL,
  `notify_enabled` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tasks_ibfk_1` (`user_id`),
  CONSTRAINT `tasks_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tasks`
--

LOCK TABLES `tasks` WRITE;
/*!40000 ALTER TABLE `tasks` DISABLE KEYS */;
INSERT INTO `tasks` VALUES (3,'meeting','06:00','placement cell meeting','banner','',NULL,NULL,NULL,NULL,NULL,NULL,'one-time',1,'2025-09-12 07:02:37',2,1),(4,'assignment','11:00','launch to global assignment completion','push','',NULL,NULL,NULL,NULL,NULL,NULL,'one-time',1,'2025-09-12 07:03:06',2,1),(6,'meeting','18:21','meeting with boss','banner','',NULL,NULL,NULL,NULL,NULL,NULL,'one-time',1,'2025-09-12 10:30:16',1,0),(7,'prepare grocery list','16:30','rice tomato, milk milk','push','',NULL,NULL,NULL,NULL,NULL,NULL,'one-time',1,'2025-09-12 10:31:09',1,1),(10,'furniture purchase','18:24','sofa purchase','push','',NULL,NULL,NULL,NULL,NULL,NULL,'one-time',1,'2025-09-12 12:08:53',1,1),(11,'reminder','18:23','BSNL bill reminder','push','',NULL,NULL,NULL,NULL,NULL,NULL,'one-time',1,'2025-09-12 12:10:24',1,0),(12,'bill pay','03:00','electricity bill','push','',NULL,NULL,NULL,NULL,NULL,NULL,'one-time',1,'2025-09-12 12:16:29',1,1),(13,'link Aadhar','05:00','SBI','push','',NULL,NULL,NULL,NULL,NULL,NULL,'one-time',1,'2025-09-12 12:49:29',1,1);
/*!40000 ALTER TABLE `tasks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','$2b$12$ObgfVJ/Ke0pkBEhOOpU6gezCS0Y8wdQ2SmvDVVzFy2w/mPbCBF3/O'),(2,'ramya','$2b$12$K7ckH04xwaolOSRTAbGwo.cdd9FEOUk9kf7fxwV91hFf61NhstT5m');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-12 18:54:45
