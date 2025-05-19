-- Eliminar base de datos si existe y crearla
DROP DATABASE IF EXISTS tienda;
CREATE DATABASE tienda;
USE tienda;

-- Crear tabla articulo
CREATE TABLE articulo (
	id INT AUTO_INCREMENT,	
	nombre VARCHAR(20),
	precio_actual DOUBLE,
	descripcion VARCHAR(100),
	cantidad INT NOT NULL,
	imagen VARCHAR(255),
	CONSTRAINT articulo_pk PRIMARY KEY(id, nombre, precio_actual)
);

-- Crear tabla usuario con id autoincremental como clave primaria
CREATE TABLE usuario (
	id INT AUTO_INCREMENT PRIMARY KEY,
	nombre VARCHAR(100) NOT NULL,
	email VARCHAR(100) UNIQUE NOT NULL,
	password VARCHAR(100) NOT NULL
);

-- Crear tabla carrito
CREATE TABLE carrito (
	id_carrito INT NOT NULL,
	id_usuario INT NOT NULL,
	id_articulo INT NOT NULL,
	nombre_articulo VARCHAR(20) NOT NULL,
	precio_articulo DOUBLE NOT NULL,
	cantidad INT NOT NULL,
	CONSTRAINT usuario_fk FOREIGN KEY(id_usuario) REFERENCES usuario(id),
	CONSTRAINT articulo_fk FOREIGN KEY(id_articulo, nombre_articulo, precio_articulo) REFERENCES articulo(id, nombre, precio_actual),
	PRIMARY KEY (id_carrito, id_articulo)
);

-- Crear tabla pedido
CREATE TABLE pedido (
	id INT AUTO_INCREMENT PRIMARY KEY,
	id_usuario INT NOT NULL,
	id_articulo INT NOT NULL,
	nombre_articulo VARCHAR(20),
	fecha_pedido DATE NOT NULL,
	fecha_entrega DATE NOT NULL,
	estado ENUM('procesando', 'completado', 'cancelado') NOT NULL,
	CONSTRAINT usuario_pedido_fk FOREIGN KEY(id_usuario) REFERENCES usuario(id),
	CONSTRAINT articulo_pedido_fk FOREIGN KEY(id_articulo, nombre_articulo) REFERENCES articulo(id, nombre)
);
