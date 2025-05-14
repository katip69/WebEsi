DROP DATABASE IF EXISTS tienda;
CREATE DATABASE tienda;
USE tienda;

CREATE TABLE articulo (
	id INT AUTO_INCREMENT,	
	nombre VARCHAR(20),
	precio_actual DOUBLE,
	descripcion VARCHAR(100),
	cantidad INT NOT NULL,
	imagen VARCHAR(255), -- imagen
	CONSTRAINT articulo_pk PRIMARY KEY(id, nombre, precio_actual)
);

CREATE TABLE usuario(
	nombre VARCHAR(100) NOT NULL,
	email VARCHAR(100) PRIMARY KEY,
	password VARCHAR(100) NOT NULL
);

CREATE TABLE carrito(
	id_carrito INT NOT NULL,
	id_articulo INT NOT NULL,
	id_usuario VARCHAR(100) NOT NULL,
	nombre_articulo VARCHAR(20) NOT NULL,
	precio_articulo DOUBLE NOT NULL,
	cantidad INT NOT NULL,
	CONSTRAINT usuario_fk FOREIGN KEY(id_usuario) REFERENCES usuario(email),
	CONSTRAINT articulo_fk FOREIGN KEY(id_articulo, nombre_articulo, precio_articulo) REFERENCES articulo(id, nombre, precio_actual),
	PRIMARY KEY (id_carrito, id_articulo)
);

CREATE TABLE pedido(
	id INT AUTO_INCREMENT PRIMARY KEY,
	email VARCHAR(100) NOT NULL,
	fecha_pedido DATE NOT NULL,
	fecha_entrega DATE NOT NULL,
	estado ENUM('procesando', 'completado', 'cancelado') NOT NULL,
	CONSTRAINT email_usuario FOREIGN KEY(email) REFERENCES usuario(email)
);

CREATE TABLE pedido_articulo(
	id_pedido INT NOT NULL,
	id_articulo INT,
	precio DOUBLE NOT NULL,
	cantidad INT NOT NULL,
	CONSTRAINT id_p FOREIGN KEY(id_pedido) REFERENCES pedido(id) ON DELETE CASCADE,
	CONSTRAINT id_ar FOREIGN KEY(id_articulo) REFERENCES articulo(id),
	PRIMARY KEY (id_pedido, id_articulo)
);

