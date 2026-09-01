-- =====================================================================
-- MediApp - Volcado de la base de datos `mediapp`
-- Generado: 2026-09-01 11:35
-- Servidor: MariaDB 10.4.28 (XAMPP)
--
-- Incluye las migraciones 001, 002 y 003 (UNIQUE en medicamento.nombre),
-- cuentas de acceso de los 3 medicos originales, la correccion de datos
-- de la cita 5, y el hasheo (scrypt) de las 2 contrasenas que aun
-- estaban en texto plano (tete, admin). Ya no queda ninguna contrasena
-- sin hashear y el login ya no acepta texto plano como fallback.
-- =====================================================================

-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: localhost    Database: mediapp
-- ------------------------------------------------------
-- Server version	5.5.5-10.4.28-MariaDB

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
-- Current Database: `mediapp`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `mediapp` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `mediapp`;

--
-- Table structure for table `cita`
--

DROP TABLE IF EXISTS `cita`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cita` (
  `id_cita` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL,
  `motivo` varchar(255) NOT NULL,
  `estado` enum('agendada','cancelada') NOT NULL DEFAULT 'agendada',
  `id_paciente` int(11) NOT NULL,
  `id_medico` int(11) NOT NULL,
  PRIMARY KEY (`id_cita`),
  KEY `cita_ibfk_1` (`id_paciente`),
  KEY `idx_cita_medico_fecha` (`id_medico`,`fecha`),
  CONSTRAINT `cita_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id_paciente`) ON DELETE CASCADE,
  CONSTRAINT `cita_ibfk_2` FOREIGN KEY (`id_medico`) REFERENCES `medico` (`id_medico`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cita`
--

LOCK TABLES `cita` WRITE;
/*!40000 ALTER TABLE `cita` DISABLE KEYS */;
INSERT INTO `cita` VALUES (1,'2026-05-01 08:00:00','Hinchazón en la zona intima','agendada',1,1),(2,'2026-08-25 10:30:00','','agendada',1,1),(3,'2026-08-27 21:06:00','','agendada',3,1),(4,'2026-08-26 10:30:00','gripe y mucha fiebre','agendada',7,2),(5,'2026-08-26 11:00:00','gripe','agendada',4,2);
/*!40000 ALTER TABLE `cita` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `consulta`
--

DROP TABLE IF EXISTS `consulta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consulta` (
  `id_consulta` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL,
  `diagnostico` text NOT NULL,
  `tratamiento` varchar(255) NOT NULL,
  `id_paciente` int(11) NOT NULL,
  `id_medico` int(11) NOT NULL,
  PRIMARY KEY (`id_consulta`),
  KEY `id_paciente` (`id_paciente`),
  KEY `id_medico` (`id_medico`),
  CONSTRAINT `consulta_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id_paciente`),
  CONSTRAINT `consulta_ibfk_2` FOREIGN KEY (`id_medico`) REFERENCES `medico` (`id_medico`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consulta`
--

LOCK TABLES `consulta` WRITE;
/*!40000 ALTER TABLE `consulta` DISABLE KEYS */;
INSERT INTO `consulta` VALUES (1,'2026-03-20 11:24:00','tete llego','prueba 1',1,1);
/*!40000 ALTER TABLE `consulta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `especialidad`
--

DROP TABLE IF EXISTS `especialidad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `especialidad` (
  `id_especialidad` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  PRIMARY KEY (`id_especialidad`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `especialidad`
--

LOCK TABLES `especialidad` WRITE;
/*!40000 ALTER TABLE `especialidad` DISABLE KEYS */;
INSERT INTO `especialidad` VALUES (1,'Cardiólogo','Prevención y tratamiento de enfermedades del corazón y sistema circulatorio.'),(4,'Medicina General','Atención médica inicial y diagnóstico de enfermedades comunes.'),(5,'Pediatria','Atención médica y seguimiento de la salud de niños y adolescentes.'),(6,'Dermatología','Diagnóstico y tratamiento de enfermedades de la piel, cabello y uñas.'),(7,'Ginecólogo','Atención de la salud reproductiva y ginecológica de la mujer.'),(8,'Oftalmología','Diagnóstico y tratamiento de enfermedades y problemas de la visión.');
/*!40000 ALTER TABLE `especialidad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `examen`
--

DROP TABLE IF EXISTS `examen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `examen` (
  `id_examen` int(11) NOT NULL AUTO_INCREMENT,
  `id_paciente` int(11) NOT NULL,
  `id_medico` int(11) NOT NULL,
  `tipo_examen` varchar(255) NOT NULL,
  `fecha_solicitud` datetime NOT NULL,
  `fecha_resultado` datetime DEFAULT NULL,
  `resultado` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_examen`) USING BTREE,
  KEY `examen_ibfk_2` (`id_medico`),
  KEY `idx_examen_paciente` (`id_paciente`),
  CONSTRAINT `examen_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id_paciente`),
  CONSTRAINT `examen_ibfk_2` FOREIGN KEY (`id_medico`) REFERENCES `medico` (`id_medico`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `examen`
--

LOCK TABLES `examen` WRITE;
/*!40000 ALTER TABLE `examen` DISABLE KEYS */;
INSERT INTO `examen` VALUES (1,1,1,'Examen de sangre','2026-04-26 18:02:00','2026-05-10 05:50:00','Useche\'s PetGuia');
/*!40000 ALTER TABLE `examen` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historia`
--

DROP TABLE IF EXISTS `historia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historia` (
  `id_historia` int(11) NOT NULL AUTO_INCREMENT,
  `id_paciente` int(11) NOT NULL,
  `id_medico` int(11) NOT NULL,
  `fecha` datetime NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  `notas` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_historia`),
  KEY `id_paciente` (`id_paciente`),
  KEY `id_medico` (`id_medico`),
  CONSTRAINT `historia_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id_paciente`),
  CONSTRAINT `historia_ibfk_2` FOREIGN KEY (`id_medico`) REFERENCES `medico` (`id_medico`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historia`
--

LOCK TABLES `historia` WRITE;
/*!40000 ALTER TABLE `historia` DISABLE KEYS */;
INSERT INTO `historia` VALUES (1,1,1,'2026-05-21 00:00:00','Tos severa acompañada de flemas con sangre','salio resfriado y se mojo'),(2,7,2,'2026-08-26 10:30:00','gripe','cuidarse');
/*!40000 ALTER TABLE `historia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medicamento`
--

DROP TABLE IF EXISTS `medicamento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicamento` (
  `id_medicamento` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  `dosis` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_medicamento`),
  UNIQUE KEY `idx_medicamento_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medicamento`
--

LOCK TABLES `medicamento` WRITE;
/*!40000 ALTER TABLE `medicamento` DISABLE KEYS */;
INSERT INTO `medicamento` VALUES (1,'Acetaminofén','Analgésico y antipirético utilizado para aliviar dolor y fiebre.','Una pastilla cada 6-8 horas'),(2,'Ibuprofeno','Antiinflamatorio utilizado para aliviar dolor, inflamación y fiebre.','500gm'),(3,'Naproxeno','Antiinflamatorio utilizado para el alivio de dolor e inflamación.','Una cada 12 Horas (500gm)'),(4,'Loratadina','Antihistamínico utilizado para aliviar síntomas de alergia.','Una cada 12 Horas (10gm)'),(5,'Losartan','Medicamento utilizado principalmente para el control de la presión arterial.','Una cada 24 Horas (20gm)');
/*!40000 ALTER TABLE `medicamento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medico`
--

DROP TABLE IF EXISTS `medico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medico` (
  `id_medico` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `numero_identidad` int(11) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `email` varchar(120) NOT NULL,
  `id_especialidad` int(11) NOT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_medico`),
  UNIQUE KEY `numero_identidad` (`numero_identidad`) USING BTREE,
  KEY `id_especialidad` (`id_especialidad`),
  KEY `fk_medico_usuario` (`id_usuario`),
  CONSTRAINT `fk_medico_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `medico_ibfk_1` FOREIGN KEY (`id_especialidad`) REFERENCES `especialidad` (`id_especialidad`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medico`
--

LOCK TABLES `medico` WRITE;
/*!40000 ALTER TABLE `medico` DISABLE KEYS */;
INSERT INTO `medico` VALUES (1,'Angel Quiñones',123456789,'3201234567','prueba@gmail.com',1,9),(2,'Paulino Velandia ',5440242,'3115313373','paulino123@gmail.com',4,10),(3,'john Hernandez ',13270125,'3134219391','pablo1258@gmail.com',8,11);
/*!40000 ALTER TABLE `medico` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paciente`
--

DROP TABLE IF EXISTS `paciente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `paciente` (
  `id_paciente` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `tipo_documento` varchar(20) NOT NULL,
  `numero_documento` varchar(30) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `direccion` varchar(150) NOT NULL,
  `email` varchar(120) NOT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_paciente`),
  UNIQUE KEY `numero_documento` (`numero_documento`),
  KEY `fk_paciente_usuario` (`id_usuario`),
  CONSTRAINT `fk_paciente_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paciente`
--

LOCK TABLES `paciente` WRITE;
/*!40000 ALTER TABLE `paciente` DISABLE KEYS */;
INSERT INTO `paciente` VALUES (1,'Tete Quiñones','RC','666777','2001-05-22','3145907489','Calle 14, Av9 #14-52 Barbacoa','TeteQ@gmail.com',1),(3,'Ruben Martinez','CC','1092531608','2007-02-17','3212536033','Av 5 Sevilla KDX 506','xxstarck18xx@gmail.com',3),(4,'franklin molina','PAS','3730766','2026-05-08','3145907489','Ceiba','xxstarck18xx@gmail.com',4),(5,'Nicoll Cruz','TI','1093591827','2005-10-27','3173323340','Santa Helena niza','nicollcruz123@gmail.com',5),(6,'Angel Hernandez','TI','1091966775','2005-02-13','3204570285','Santa Helena niza','ah3293317@gmail.com',NULL),(7,'fosi','TI','123554625','2026-08-01','3201454756','Santa Helena niza','ahsksokja@gmail.com',6);
/*!40000 ALTER TABLE `paciente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `receta`
--

DROP TABLE IF EXISTS `receta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `receta` (
  `id_receta` int(11) NOT NULL AUTO_INCREMENT,
  `id_consulta` int(11) NOT NULL,
  `id_medicamento` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `indicaciones` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_receta`),
  KEY `id_consulta` (`id_consulta`),
  KEY `id_medicamento` (`id_medicamento`),
  CONSTRAINT `receta_ibfk_1` FOREIGN KEY (`id_consulta`) REFERENCES `consulta` (`id_consulta`),
  CONSTRAINT `receta_ibfk_2` FOREIGN KEY (`id_medicamento`) REFERENCES `medicamento` (`id_medicamento`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `receta`
--

LOCK TABLES `receta` WRITE;
/*!40000 ALTER TABLE `receta` DISABLE KEYS */;
INSERT INTO `receta` VALUES (1,1,1,3,'prueba');
/*!40000 ALTER TABLE `receta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `id_rol` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_rol` varchar(50) NOT NULL,
  PRIMARY KEY (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (1,'admin'),(2,'paciente'),(3,'medico');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `id_rol` int(11) NOT NULL DEFAULT 2,
  `estado` enum('activo','inactivo') NOT NULL DEFAULT 'activo',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `username` (`username`),
  KEY `fk_usuario_rol` (`id_rol`),
  CONSTRAINT `fk_usuario_rol` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (1,'tete','scrypt:32768:8:1$Z9xcX8etUswiR67x$cba338b5f0bcdd4b696a401e1d8984f4ba8c6f48abd97e2c2df64f7a91226f3eb8c627571ab99be668620a85bb00ad1d73b7beb313893e358d46f634026020c3',2,'activo'),(2,'admin','scrypt:32768:8:1$gKQrvExZ83GVZI7h$a0ad380df1e8f6c635ad86c1e72a525f8eeddeb542bb5dc15bb8a4f2cbab559e11c55e2edef57e22c7b7f2c27be3fd5466ba6fb1d9bd549aed2602df4df97bbb',1,'activo'),(3,'stick','scrypt:32768:8:1$VfMwuMLrGxObCXPo$19429c5cea4fbe4ae40d226f4808c4002fbb9efd2818512db741752b63bd6ea02f8045dffc4c54b81a3642b87c58e2ed92a070f899c1d60956a2a23aaaa5bf62',2,'activo'),(4,'elmolina01','scrypt:32768:8:1$vMVhH0Fxc5QbjVwr$43c99c1d22670c9a48a8dac859ffc48d7cf7cd0892455708e3038ad8c334df670278dafebb9723a7b663e2fcccfd892dcdb43ad02deab4642f38d475417b3f08',2,'activo'),(5,'Nicoll','scrypt:32768:8:1$4PkWLITtrEYERFfO$845076fa7fa60cf7e9910babcfff13ddcff2ff674a7e62afa7c0921fda2bee4f6ea2d68b651a59a1f48d8b23c692dee6292c087cf66153ae262faa57b45f54ef',2,'activo'),(6,'Fosi','scrypt:32768:8:1$SdVlH75pZS1rFpEE$ed611e65fff3790aecc1f72df4885efd8634021b503d184667a79c6b702a426bb4311c1b9a675635317c1d8fc6bb18596e1f05e7fbbb17a978a5bb6d13c2bb88',2,'activo'),(9,'angel.quinones','scrypt:32768:8:1$99QbeOwXXWG2jIA0$26d6d0f52a802c8965d82a98be80bc6ace7f72c8efb48b34c0a9ba18caaf8c3020434ad04e2d89543a3a80ab062b81412147cfb6a02d8ce92625ff53f1a44e5b',3,'activo'),(10,'paulino.velandia','scrypt:32768:8:1$Is7Rk9V0jZSQ11Hj$c0d95c94396198f7b84d4cefb68db7a9ca5b74cbd3449f67f38b80317088e82c274cafb4266fd4f02170779b30f55996513a7931de8e4c4a7f6d10084e6f37c0',3,'activo'),(11,'john.hernandez','scrypt:32768:8:1$1bPUcxRAgNNguvnS$022ef7966636c220e9b93a9966e547fdbffbc1fe744625f075667669ec39000434ab46bb1a8dc326c9da6ed501e3d304cc9ef27f96c7c298648099e734efb243',3,'activo');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-01 11:35:53
