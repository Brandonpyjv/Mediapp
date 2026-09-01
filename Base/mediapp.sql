-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 01-09-2026 a las 02:51:30
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `mediapp`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cita`
--

CREATE TABLE `cita` (
  `id_cita` int(11) NOT NULL,
  `fecha` datetime NOT NULL,
  `motivo` varchar(255) NOT NULL,
  `id_paciente` int(11) NOT NULL,
  `id_medico` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `cita`
--

INSERT INTO `cita` (`id_cita`, `fecha`, `motivo`, `id_paciente`, `id_medico`) VALUES
(1, '2026-05-01 08:00:00', 'Hinchazón en la zona intima', 1, 1),
(2, '2026-08-25 10:30:00', '', 1, 1),
(3, '2026-08-27 21:06:00', '', 3, 1),
(4, '2026-08-26 10:30:00', 'gripe y mucha fiebre', 7, 2),
(5, '2026-08-26 10:31:00', 'gripe', 4, 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `consulta`
--

CREATE TABLE `consulta` (
  `id_consulta` int(11) NOT NULL,
  `fecha` datetime NOT NULL,
  `diagnostico` text NOT NULL,
  `tratamiento` varchar(255) NOT NULL,
  `id_paciente` int(11) NOT NULL,
  `id_medico` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `consulta`
--

INSERT INTO `consulta` (`id_consulta`, `fecha`, `diagnostico`, `tratamiento`, `id_paciente`, `id_medico`) VALUES
(1, '2026-03-20 11:24:00', 'tete llego', 'prueba 1', 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `especialidad`
--

CREATE TABLE `especialidad` (
  `id_especialidad` int(11) NOT NULL,
  `nombre` varchar(80) NOT NULL,
  `descripcion` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `especialidad`
--

INSERT INTO `especialidad` (`id_especialidad`, `nombre`, `descripcion`) VALUES
(1, 'Cardiólogo', 'Prevención y tratamiento de enfermedades del corazón y sistema circulatorio.'),
(4, 'Medicina General', 'Atención médica inicial y diagnóstico de enfermedades comunes.'),
(5, 'Pediatria', 'Atención médica y seguimiento de la salud de niños y adolescentes.'),
(6, 'Dermatología', 'Diagnóstico y tratamiento de enfermedades de la piel, cabello y uñas.'),
(7, 'Ginecólogo', 'Atención de la salud reproductiva y ginecológica de la mujer.'),
(8, 'Oftalmología', 'Diagnóstico y tratamiento de enfermedades y problemas de la visión.');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `examen`
--

CREATE TABLE `examen` (
  `id_examen` int(11) NOT NULL,
  `id_paciente` int(11) NOT NULL,
  `id_medico` int(11) NOT NULL,
  `tipo_examen` varchar(255) NOT NULL,
  `fecha_solicitud` datetime NOT NULL,
  `fecha_resultado` datetime DEFAULT NULL,
  `resultado` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `examen`
--

INSERT INTO `examen` (`id_examen`, `id_paciente`, `id_medico`, `tipo_examen`, `fecha_solicitud`, `fecha_resultado`, `resultado`) VALUES
(1, 1, 1, 'Examen de sangre', '2026-04-26 18:02:00', '2026-05-10 05:50:00', 'Useche\'s PetGuia');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historia`
--

CREATE TABLE `historia` (
  `id_historia` int(11) NOT NULL,
  `id_paciente` int(11) NOT NULL,
  `id_medico` int(11) NOT NULL,
  `fecha` datetime NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  `notas` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `historia`
--

INSERT INTO `historia` (`id_historia`, `id_paciente`, `id_medico`, `fecha`, `descripcion`, `notas`) VALUES
(1, 1, 1, '2026-05-21 00:00:00', 'Tos severa acompañada de flemas con sangre', 'salio resfriado y se mojo'),
(2, 7, 2, '2026-08-26 10:30:00', 'gripe', 'cuidarse');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `medicamento`
--

CREATE TABLE `medicamento` (
  `id_medicamento` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  `dosis` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `medicamento`
--

INSERT INTO `medicamento` (`id_medicamento`, `nombre`, `descripcion`, `dosis`) VALUES
(1, 'Acetaminofén', 'Analgésico y antipirético utilizado para aliviar dolor y fiebre.', 'Una pastilla cada 6-8 horas'),
(2, 'Ibuprofeno', 'Antiinflamatorio utilizado para aliviar dolor, inflamación y fiebre.', '500gm'),
(3, 'Naproxeno', 'Antiinflamatorio utilizado para el alivio de dolor e inflamación.', 'Una cada 12 Horas (500gm)'),
(4, 'Loratadina', 'Antihistamínico utilizado para aliviar síntomas de alergia.', 'Una cada 12 Horas (10gm)'),
(5, 'Losartan', 'Medicamento utilizado principalmente para el control de la presión arterial.', 'Una cada 24 Horas (20gm)');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `medico`
--

CREATE TABLE `medico` (
  `id_medico` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `numero_identidad` int(11) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `email` varchar(120) NOT NULL,
  `id_especialidad` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `medico`
--

INSERT INTO `medico` (`id_medico`, `nombre`, `numero_identidad`, `telefono`, `email`, `id_especialidad`) VALUES
(1, 'Angel Quiñones', 123456789, '3201234567', 'prueba@gmail.com', 1),
(2, 'Paulino Velandia ', 5440242, '3115313373', 'paulino123@gmail.com', 4),
(3, 'john Hernandez ', 13270125, '3134219391', 'pablo1258@gmail.com', 8);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `paciente`
--

CREATE TABLE `paciente` (
  `id_paciente` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `tipo_documento` varchar(20) NOT NULL,
  `numero_documento` varchar(30) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `direccion` varchar(150) NOT NULL,
  `email` varchar(120) NOT NULL,
  `id_usuario` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `paciente`
--

INSERT INTO `paciente` (`id_paciente`, `nombre`, `tipo_documento`, `numero_documento`, `fecha_nacimiento`, `telefono`, `direccion`, `email`, `id_usuario`) VALUES
(1, 'Tete Quiñones', 'RC', '666777', '2001-05-22', '3145907489', 'Calle 14, Av9 #14-52 Barbacoa', 'TeteQ@gmail.com', 1),
(3, 'Ruben Martinez', 'CC', '1092531608', '2007-02-17', '3212536033', 'Av 5 Sevilla KDX 506', 'xxstarck18xx@gmail.com', 3),
(4, 'franklin molina', 'PAS', '3730766', '2026-05-08', '3145907489', 'Ceiba', 'xxstarck18xx@gmail.com', 4),
(5, 'Nicoll Cruz', 'TI', '1093591827', '2005-10-27', '3173323340', 'Santa Helena niza', 'nicollcruz123@gmail.com', 5),
(6, 'Angel Hernandez', 'TI', '1091966775', '2005-02-13', '3204570285', 'Santa Helena niza', 'ah3293317@gmail.com', NULL),
(7, 'fosi', 'TI', '123554625', '2026-08-01', '3201454756', 'Santa Helena niza', 'ahsksokja@gmail.com', 6);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `receta`
--

CREATE TABLE `receta` (
  `id_receta` int(11) NOT NULL,
  `id_consulta` int(11) NOT NULL,
  `id_medicamento` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `indicaciones` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `receta`
--

INSERT INTO `receta` (`id_receta`, `id_consulta`, `id_medicamento`, `cantidad`, `indicaciones`) VALUES
(1, 1, 1, 3, 'prueba');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rol`
--

CREATE TABLE `rol` (
  `id_rol` int(11) NOT NULL,
  `nombre_rol` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `rol`
--

INSERT INTO `rol` (`id_rol`, `nombre_rol`) VALUES
(1, 'admin'),
(2, 'paciente');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `id_usuario` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `id_rol` int(11) NOT NULL DEFAULT 2
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id_usuario`, `username`, `password`, `id_rol`) VALUES
(1, 'tete', '12345', 2),
(2, 'admin', '12345', 1),
(3, 'stick', 'scrypt:32768:8:1$VfMwuMLrGxObCXPo$19429c5cea4fbe4ae40d226f4808c4002fbb9efd2818512db741752b63bd6ea02f8045dffc4c54b81a3642b87c58e2ed92a070f899c1d60956a2a23aaaa5bf62', 2),
(4, 'elmolina01', 'scrypt:32768:8:1$vMVhH0Fxc5QbjVwr$43c99c1d22670c9a48a8dac859ffc48d7cf7cd0892455708e3038ad8c334df670278dafebb9723a7b663e2fcccfd892dcdb43ad02deab4642f38d475417b3f08', 2),
(5, 'Nicoll', 'scrypt:32768:8:1$4PkWLITtrEYERFfO$845076fa7fa60cf7e9910babcfff13ddcff2ff674a7e62afa7c0921fda2bee4f6ea2d68b651a59a1f48d8b23c692dee6292c087cf66153ae262faa57b45f54ef', 2),
(6, 'Fosi', 'scrypt:32768:8:1$SdVlH75pZS1rFpEE$ed611e65fff3790aecc1f72df4885efd8634021b503d184667a79c6b702a426bb4311c1b9a675635317c1d8fc6bb18596e1f05e7fbbb17a978a5bb6d13c2bb88', 2);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `cita`
--
ALTER TABLE `cita`
  ADD PRIMARY KEY (`id_cita`),
  ADD UNIQUE KEY `uq_medico_fecha` (`id_medico`,`fecha`),
  ADD KEY `cita_ibfk_1` (`id_paciente`);

--
-- Indices de la tabla `consulta`
--
ALTER TABLE `consulta`
  ADD PRIMARY KEY (`id_consulta`),
  ADD KEY `id_paciente` (`id_paciente`),
  ADD KEY `id_medico` (`id_medico`);

--
-- Indices de la tabla `especialidad`
--
ALTER TABLE `especialidad`
  ADD PRIMARY KEY (`id_especialidad`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `examen`
--
ALTER TABLE `examen`
  ADD PRIMARY KEY (`id_examen`) USING BTREE,
  ADD UNIQUE KEY `id_examen` (`id_paciente`,`id_medico`) USING BTREE,
  ADD KEY `examen_ibfk_2` (`id_medico`);

--
-- Indices de la tabla `historia`
--
ALTER TABLE `historia`
  ADD PRIMARY KEY (`id_historia`),
  ADD KEY `id_paciente` (`id_paciente`),
  ADD KEY `id_medico` (`id_medico`);

--
-- Indices de la tabla `medicamento`
--
ALTER TABLE `medicamento`
  ADD PRIMARY KEY (`id_medicamento`);

--
-- Indices de la tabla `medico`
--
ALTER TABLE `medico`
  ADD PRIMARY KEY (`id_medico`),
  ADD UNIQUE KEY `numero_identidad` (`numero_identidad`) USING BTREE,
  ADD KEY `id_especialidad` (`id_especialidad`);

--
-- Indices de la tabla `paciente`
--
ALTER TABLE `paciente`
  ADD PRIMARY KEY (`id_paciente`),
  ADD UNIQUE KEY `numero_documento` (`numero_documento`),
  ADD KEY `fk_paciente_usuario` (`id_usuario`);

--
-- Indices de la tabla `receta`
--
ALTER TABLE `receta`
  ADD PRIMARY KEY (`id_receta`),
  ADD KEY `id_consulta` (`id_consulta`),
  ADD KEY `id_medicamento` (`id_medicamento`);

--
-- Indices de la tabla `rol`
--
ALTER TABLE `rol`
  ADD PRIMARY KEY (`id_rol`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `fk_usuario_rol` (`id_rol`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `cita`
--
ALTER TABLE `cita`
  MODIFY `id_cita` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `consulta`
--
ALTER TABLE `consulta`
  MODIFY `id_consulta` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `especialidad`
--
ALTER TABLE `especialidad`
  MODIFY `id_especialidad` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `examen`
--
ALTER TABLE `examen`
  MODIFY `id_examen` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `historia`
--
ALTER TABLE `historia`
  MODIFY `id_historia` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `medicamento`
--
ALTER TABLE `medicamento`
  MODIFY `id_medicamento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `medico`
--
ALTER TABLE `medico`
  MODIFY `id_medico` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `paciente`
--
ALTER TABLE `paciente`
  MODIFY `id_paciente` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `receta`
--
ALTER TABLE `receta`
  MODIFY `id_receta` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `rol`
--
ALTER TABLE `rol`
  MODIFY `id_rol` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `cita`
--
ALTER TABLE `cita`
  ADD CONSTRAINT `cita_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id_paciente`) ON DELETE CASCADE,
  ADD CONSTRAINT `cita_ibfk_2` FOREIGN KEY (`id_medico`) REFERENCES `medico` (`id_medico`);

--
-- Filtros para la tabla `consulta`
--
ALTER TABLE `consulta`
  ADD CONSTRAINT `consulta_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id_paciente`),
  ADD CONSTRAINT `consulta_ibfk_2` FOREIGN KEY (`id_medico`) REFERENCES `medico` (`id_medico`);

--
-- Filtros para la tabla `examen`
--
ALTER TABLE `examen`
  ADD CONSTRAINT `examen_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id_paciente`),
  ADD CONSTRAINT `examen_ibfk_2` FOREIGN KEY (`id_medico`) REFERENCES `medico` (`id_medico`);

--
-- Filtros para la tabla `historia`
--
ALTER TABLE `historia`
  ADD CONSTRAINT `historia_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id_paciente`),
  ADD CONSTRAINT `historia_ibfk_2` FOREIGN KEY (`id_medico`) REFERENCES `medico` (`id_medico`);

--
-- Filtros para la tabla `medico`
--
ALTER TABLE `medico`
  ADD CONSTRAINT `medico_ibfk_1` FOREIGN KEY (`id_especialidad`) REFERENCES `especialidad` (`id_especialidad`);

--
-- Filtros para la tabla `paciente`
--
ALTER TABLE `paciente`
  ADD CONSTRAINT `fk_paciente_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `receta`
--
ALTER TABLE `receta`
  ADD CONSTRAINT `receta_ibfk_1` FOREIGN KEY (`id_consulta`) REFERENCES `consulta` (`id_consulta`),
  ADD CONSTRAINT `receta_ibfk_2` FOREIGN KEY (`id_medicamento`) REFERENCES `medicamento` (`id_medicamento`);

--
-- Filtros para la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD CONSTRAINT `fk_usuario_rol` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
