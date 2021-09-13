-- This is a dump of the environment transforms from a database
-- that has them correctly entered. This can be used to populate
-- them in a new database instead of re-entering them by hand.

-- MySQL dump 10.13  Distrib 5.5.29, for debian-linux-gnu (i686)
--
-- Host: localhost    Database: device_cfg_portal
-- ------------------------------------------------------
-- Server version	5.5.29-0ubuntu0.12.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `env_transform`
--

DROP TABLE IF EXISTS `env_transform`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `env_transform` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order` int(11) NOT NULL,
  `env_pat` varchar(255) NOT NULL,
  `hwtype_pat` varchar(255) NOT NULL,
  `carrier_region_pat` varchar(255) NOT NULL,
  `setting_name_pat` varchar(1000) NOT NULL,
  `value_pat` varchar(1000) NOT NULL,
  `value_sub` varchar(8000) DEFAULT NULL,
  `comment` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `env_transform`
--

LOCK TABLES `env_transform` WRITE;
/*!40000 ALTER TABLE `env_transform` DISABLE KEYS */;
INSERT INTO `env_transform` VALUES (1,10,'^(qa|sdc).*','.*','.*','^blur\\.service\\.checkin.*','.*',NULL,'Only production has checkin settings.'),(2,20,'^(qa|sdc).*','.*','.*\\.CN$','.*(zerorated|gratis).*','.*',NULL,'Remove all non-prod zero-rating settings for deployments in China.'),(3,30,'^qa.*','.*','.*(Verizon\\.US|\\.CN|\\.KR)$','.*(zerorated|gratis).*','.*',NULL,'Remove all QA zero-rating settings of deployments for Verizon, Korea and China.'),(4,40,'^qa.*','.*','.*','.*heartbeatTimeCarrierSpecific$','.*',NULL,'Remove heartbeatTimeCarrierSpecific in QA environments.'),(5,50,'^(qa|sdc).*','.*','.*','.*','zc-dlmgr\\.gtm\\.svcmot\\.com','zc.svcmot.com',NULL),(6,60,'^(qa|sdc).*','.*','.*','.*','um\\.svcmot\\.com','um-sso.svcmot.com',NULL),(7,70,'^(qa|sdc).*','.*','.*','.*','blur\\.svcmot\\.com','{{env}}.blurdev.com',NULL),(8,80,'^(qa|sdc).*','.*','.*','.*','blur\\.motorola\\.com','{{env}}.blurdev.com',NULL),(9,90,'^(qa|sdc).*','.*','.*','.*','\\.svcmot\\.com','-{{env}}.blurdev.com',NULL),(10,100,'^(qa|sdc).*','.*','.*','.*','\\.motorola\\.com','-{{env}}.blurdev.com',NULL);
/*!40000 ALTER TABLE `env_transform` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2013-04-20 10:43:29
