DROP DATABASE IF EXISTS tienda;
CREATE DATABASE tienda;
USE tienda;

CREATE TABLE articulo (
	id INT AUTO_INCREMENT PRIMARY KEY,	
	nombre VARCHAR(20) NOT NULL,
	precio_actual DOUBLE NOT NULL,
	descripcion VARCHAR(100),
	cantidad INT NOT NULL,
	imagen VARCHAR(255) -- imagen
);

CREATE TABLE usuario(
        nombre VARCHAR(100) NOT NULL,
        email VARCHAR(100) PRIMARY KEY,
        password VARCHAR(100) NOT NULL
);

CREATE TABLE carrito(
	num_carrito INT PRIMARY KEY,
	email VARCHAR(100),
	CONSTRAINT email_user FOREIGN KEY(email) REFERENCES usuario(email)
);

CREATE TABLE pedido(
	id INT AUTO_INCREMENT PRIMARY KEY,
	email VARCHAR(100) NOT NULL,
	fecha_pedido DATE NOT NULL,
	fecha_entrega DATE NOT NULL,
	estado ENUM('procesando', 'completado', 'cancelado') NOT NULL,
	CONSTRAINT email_usuario FOREIGN KEY(email) REFERENCES usuario(email)
);

CREATE TABLE carrito_articulo(
	id_carrito INT NOT NULL,
	id_articulo INT NOT NULL,
	cantidad INT NOT NULL,
	CONSTRAINT id_c FOREIGN KEY(id_carrito) REFERENCES carrito(num_carrito) ON DELETE CASCADE,
	CONSTRAINT id_a FOREIGN KEY(id_articulo) REFERENCES articulo(id),
	PRIMARY KEY (id_carrito, id_articulo)
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

