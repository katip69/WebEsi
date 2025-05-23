-- Eliminar base de datos si existe y crearla
DROP DATABASE IF EXISTS tienda;
CREATE DATABASE tienda;
USE tienda;

-- Crear tabla articulo
CREATE TABLE articulo (
	id INT AUTO_INCREMENT PRIMARY KEY,
	nombre VARCHAR(20) NOT NULL,
	precio_actual DOUBLE NOT NULL,
	descripcion VARCHAR(100),
	cantidad INT NOT NULL,
	puntuacion INT NOT NULL 
	
);

-- Crear tabla usuario con id autoincremental como clave primaria
CREATE TABLE usuario (
	id INT AUTO_INCREMENT PRIMARY KEY,
	nombre VARCHAR(100) NOT NULL,
	email VARCHAR(100) UNIQUE NOT NULL,
	password VARCHAR(100) NOT NULL,
	admin INT NOT NULL
);

-- Crear tabla carrito
CREATE TABLE carrito (
	id_usuario INT NOT NULL,
	id_articulo INT NOT NULL,
	nombre_articulo VARCHAR(20) NOT NULL,
	precio_articulo DOUBLE NOT NULL,
	cantidad INT NOT NULL,
	PRIMARY KEY (id_usuario, id_articulo),
	CONSTRAINT usuario_fk FOREIGN KEY(id_usuario) REFERENCES usuario(id),
	CONSTRAINT articulo_fk FOREIGN KEY(id_articulo) REFERENCES articulo(id)
);

-- Crear tabla pedido (información general del pedido)
CREATE TABLE pedido (
	id INT AUTO_INCREMENT PRIMARY KEY,
	id_usuario INT NOT NULL,
	fecha_pedido DATETIME NOT NULL,
	fecha_entrega DATETIME NOT NULL,
	estado ENUM('procesando', 'completado', 'cancelado') NOT NULL,
	CONSTRAINT usuario_pedido_fk FOREIGN KEY(id_usuario) REFERENCES usuario(id)
);

CREATE TABLE detalle_pedido (
    id_pedido INT NOT NULL,
    id_articulo INT NOT NULL,
    nombre_articulo VARCHAR(20) NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    CONSTRAINT pedido_detalle_fk 
        FOREIGN KEY(id_pedido) 
        REFERENCES pedido(id)
        ON DELETE CASCADE,
    CONSTRAINT articulo_detalle_fk 
        FOREIGN KEY(id_articulo) 
        REFERENCES articulo(id)
);


-- Crear tabla con la información de la página 
CREATE TABLE info (
	id INT PRIMARY KEY,
	descripcion VARCHAR(200) NOT NULL
);
