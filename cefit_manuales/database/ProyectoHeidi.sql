-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS `cefit_manuales` DEFAULT CHARACTER SET utf8mb4;
USE `cefit_manuales`;

-- Tabla usuarios (modificada)
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `tipo_documento` enum('TI','CC','CE','PPT') NOT NULL,
  `numero_documento` varchar(50) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `rol` enum('dueños','docentes','directivos','usuario') NOT NULL,
  `fecha_registro` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `ultima_sesion` DATETIME,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `numero_documento` (`numero_documento`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla manuales (modificada)
CREATE TABLE IF NOT EXISTS `manuales` (
  `id_manual` int(11) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(200) NOT NULL,
  `descripcion` text NOT NULL,
  PRIMARY KEY (`id_manual`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Nueva tabla manuales_version
CREATE TABLE IF NOT EXISTS `manuales_version` (
  `id_version` INT NOT NULL AUTO_INCREMENT,
  `id_manual` INT NOT NULL,
  `version` VARCHAR(50) NOT NULL,
  `fecha_creacion` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `archivo` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id_version`),
  FOREIGN KEY (`id_manual`) REFERENCES `manuales`(`id_manual`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla registros (modificada)
CREATE TABLE IF NOT EXISTS `registros` (
  `id_manual` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_version` INT NOT NULL,
  `fecha_acceso` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_manual`,`id_usuario`,`id_version`),
  FOREIGN KEY (`id_manual`) REFERENCES `manuales` (`id_manual`),
  FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  FOREIGN KEY (`id_version`) REFERENCES `manuales_version` (`id_version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Procedimientos almacenados

DELIMITER //

-- ActualizarUsuarios (modificado)
CREATE PROCEDURE `ActualizarUsuarios`(
    IN p_id_usuario INT,
    IN p_tipo_documento ENUM('TI','CC','CE','PPT'),
    IN p_numero_documento VARCHAR(50),
    IN p_nombre VARCHAR(100),
    IN p_correo VARCHAR(100),
    IN p_contrasena VARCHAR(255),
    IN p_rol ENUM('dueños','docentes','directivos','usuario')
)
BEGIN
    UPDATE usuarios
    SET 
        tipo_documento = p_tipo_documento,
        numero_documento = p_numero_documento,
        nombre = p_nombre,
        correo = p_correo,
        contrasena = p_contrasena,
        rol = p_rol
    WHERE id_usuario = p_id_usuario;
END//

-- ActualizarManuales (modificado)
CREATE PROCEDURE `ActualizarManuales`(
    IN p_id_manual INT,
    IN p_titulo VARCHAR(200),
    IN p_descripcion TEXT
)
BEGIN
    UPDATE manuales
    SET 
        titulo = p_titulo,
        descripcion = p_descripcion
    WHERE id_manual = p_id_manual;
END//

-- ActualizarRegistros (modificado)
CREATE PROCEDURE `ActualizarRegistros`(
    IN p_id_manual INT,
    IN p_id_usuario INT,
    IN p_id_version INT
)
BEGIN
    UPDATE registros
    SET 
        id_version = p_id_version,
        fecha_acceso = CURRENT_TIMESTAMP
    WHERE id_manual = p_id_manual AND id_usuario = p_id_usuario;
END//

-- BorrarManuales
CREATE PROCEDURE `BorrarManuales`(
    IN p_id_manual INT
)
BEGIN
    DELETE FROM manuales
    WHERE id_manual = p_id_manual;
END//

-- BorrarRegistros
CREATE PROCEDURE `BorrarRegistros`(
    IN p_id_manual INT,
    IN p_id_usuario INT
)
BEGIN
    DELETE FROM registros
    WHERE id_manual = p_id_manual AND id_usuario = p_id_usuario;
END//

-- BorrarUsuarios
CREATE PROCEDURE `BorrarUsuarios`(
    IN p_id_usuario INT
)
BEGIN
    DELETE FROM usuarios
    WHERE id_usuario = p_id_usuario;
END//

-- BuscarManuales (modificado)
CREATE PROCEDURE `BuscarManuales`(
    IN p_id_manual INT
)
BEGIN
    SELECT 
        m.id_manual,
        m.titulo, 
        m.descripcion, 
        mv.version,
        mv.archivo
    FROM manuales m
    JOIN manuales_version mv ON m.id_manual = mv.id_manual
    WHERE m.id_manual = p_id_manual
    ORDER BY mv.fecha_creacion DESC
    LIMIT 1;
END//

-- BuscarRegistros (modificado)
CREATE PROCEDURE `BuscarRegistros`(
    IN p_id_manual INT,
    IN p_id_usuario INT
)
BEGIN
    SELECT 
        r.id_usuario, 
        r.id_manual, 
        mv.version,
        r.fecha_acceso
    FROM registros r
    JOIN manuales_version mv ON r.id_version = mv.id_version
    WHERE r.id_manual = p_id_manual AND r.id_usuario = p_id_usuario;
END//

-- BuscarUsuarios
CREATE PROCEDURE `BuscarUsuarios`(
    IN p_id_usuario INT
)
BEGIN
    SELECT 
        tipo_documento, 
        numero_documento, 
        nombre, 
        correo,  
        rol,
        fecha_registro,
        ultima_sesion
    FROM usuarios
    WHERE id_usuario = p_id_usuario;
END//

-- InsertarManuales (modificado)
CREATE PROCEDURE `InsertarManuales`(
    IN p_titulo VARCHAR(200),
    IN p_descripcion TEXT
)
BEGIN
    INSERT INTO manuales (titulo, descripcion)
    VALUES (p_titulo, p_descripcion);
END//

-- InsertarVersionManual (nuevo)
CREATE PROCEDURE `InsertarVersionManual`(
    IN p_id_manual INT,
    IN p_version VARCHAR(50),
    IN p_archivo VARCHAR(255)
)
BEGIN
    INSERT INTO manuales_version (id_manual, version, archivo)
    VALUES (p_id_manual, p_version, p_archivo);
END//

-- InsertarRegistros (modificado)
CREATE PROCEDURE `InsertarRegistros`(
    IN p_id_manual INT,
    IN p_id_usuario INT,
    IN p_id_version INT
)
BEGIN
    INSERT INTO registros (id_manual, id_usuario, id_version)
    VALUES (p_id_manual, p_id_usuario, p_id_version);
END//

-- InsertarUsuarios
CREATE PROCEDURE `InsertarUsuarios`(
    IN p_tipo_documento ENUM('TI','CC','CE','PPT'),
    IN p_numero_documento VARCHAR(50),
    IN p_nombre VARCHAR(100),
    IN p_correo VARCHAR(100),
    IN p_contrasena VARCHAR(255),
    IN p_rol ENUM('dueños','docentes','directivos','usuario')
)
BEGIN
    INSERT INTO usuarios (tipo_documento, numero_documento, nombre, correo, contrasena, rol)
    VALUES (p_tipo_documento, p_numero_documento, p_nombre, p_correo, p_contrasena, p_rol);
END//

DELIMITER ;