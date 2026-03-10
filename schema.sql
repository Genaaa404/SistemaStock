CREATE DATABASE IF NOT EXISTS almacen_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE almacen_db;

CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    categoria_id INT,
    stock INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 5,
    unidad VARCHAR(50) DEFAULT 'unidad',
    precio DECIMAL(10,2) DEFAULT 0.00,
    activo TINYINT(1) DEFAULT 1,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100),
    rol ENUM('admin','empleado') DEFAULT 'empleado',
    activo TINYINT(1) DEFAULT 1,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS movimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    tipo ENUM('entrada','salida') NOT NULL,
    cantidad INT NOT NULL,
    usuario_id INT NOT NULL,
    nota TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

INSERT INTO categorias (nombre, descripcion) VALUES
    ('Herramientas', 'Herramientas manuales y eléctricas'),
    ('Materiales', 'Materiales de construcción y obra'),
    ('Eléctrico', 'Componentes y materiales eléctricos'),
    ('Plomería', 'Accesorios y tubería de plomería'),
    ('Seguridad', 'Equipo de protección personal');

INSERT INTO usuarios (username, password, nombre, rol) VALUES
    ('admin', 'admin123', 'Administrador', 'admin'),
    ('empleado1', 'emp123', 'Juan Pérez', 'empleado');

INSERT INTO productos (nombre, descripcion, categoria_id, stock, stock_minimo, unidad, precio) VALUES
    ('Martillo 16oz', 'Martillo de carpintero cabeza de acero', 1, 25, 5, 'pieza', 180.00),
    ('Destornillador Phillips', 'Juego de destornilladores Phillips', 1, 40, 10, 'juego', 95.00),
    ('Cinta métrica 5m', 'Cinta métrica retráctil de acero', 1, 30, 8, 'pieza', 65.00),
    ('Cemento 50kg', 'Cemento gris Portland tipo I', 2, 80, 20, 'saco', 145.00),
    ('Arena fina', 'Arena para mezclas y acabados', 2, 3, 10, 'tonelada', 320.00),
    ('Cable THW 12', 'Cable eléctrico THW calibre 12', 3, 500, 100, 'metro', 8.50),
    ('Contacto doble', 'Contacto eléctrico doble con tierra', 3, 60, 15, 'pieza', 35.00),
    ('Tubo PVC 1/2"', 'Tubo PVC hidráulico 1/2 pulgada 3m', 4, 45, 10, 'pieza', 28.00),
    ('Llave inglesa 12"', 'Llave ajustable 12 pulgadas', 1, 2, 5, 'pieza', 220.00),
    ('Casco protector', 'Casco de seguridad industrial blanco', 5, 15, 5, 'pieza', 85.00),
    ('Guantes de trabajo', 'Guantes de cuero para trabajo pesado', 5, 20, 8, 'par', 45.00),
    ('Lija #120', 'Papel lija grano 120 para madera', 1, 100, 30, 'pieza', 4.50);

INSERT INTO movimientos (producto_id, tipo, cantidad, usuario_id, nota) VALUES
    (1, 'entrada', 25, 1, 'Stock inicial'),
    (2, 'entrada', 40, 1, 'Stock inicial'),
    (9, 'salida', 3, 1, 'Préstamo obra norte'),
    (5, 'salida', 2, 1, 'Despacho pedido #001');

USE almacen_db;
SELECT p.nombre, p.stock, p.stock_minimo
FROM productos p
WHERE p.stock <= p.stock_minimo AND p.activo = 1;

SELECT nombre, stock, stock_minimo, activo FROM productos;

SELECT nombre, stock, stock_minimo, (stock <= stock_minimo) AS es_alerta
FROM productos
WHERE activo = 1;

SELECT nombre, stock, stock_minimo FROM productos ORDER BY nombre;