CREATE TABLE Usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL DEFAULT 'CLIENTE'
);

CREATE TABLE Marcas (
    id_marca INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Vehiculos (
    matricula VARCHAR(20) PRIMARY KEY,
    id_marca INT NOT NULL,
    anio INT,
    FOREIGN KEY (id_marca) REFERENCES Marcas(id_marca)
);

CREATE TABLE Controles (
    id_control INT PRIMARY KEY AUTO_INCREMENT,
    descripcion VARCHAR(255) NOT NULL
);

CREATE TABLE Resultados (
    id_resultado INT PRIMARY KEY AUTO_INCREMENT,
    resultado VARCHAR(50),
    puntaje_total INT,
    observaciones TEXT
);

CREATE TABLE ResultadosPorControl (
    id_resultado INT NOT NULL,
    id_control INT NOT NULL,
    calificacion INT,
    observaciones TEXT,
    PRIMARY KEY (id_resultado, id_control),
    FOREIGN KEY (id_resultado) REFERENCES Resultados(id_resultado),
    FOREIGN KEY (id_control) REFERENCES Controles(id_control)
);

CREATE TABLE Turnos (
    id_turno INT PRIMARY KEY AUTO_INCREMENT,
    matricula VARCHAR(20) NULL,
    fecha DATETIME NOT NULL,
    id_resultado INT NULL,
    estado VARCHAR(50) NOT NULL,
    FOREIGN KEY (matricula) REFERENCES Vehiculos(matricula),
    FOREIGN KEY (id_resultado) REFERENCES Resultados(id_resultado)
);

INSERT INTO Controles (descripcion) VALUES
('Frenos'), ('Luces'), ('Neumáticos'), ('Suspensión'),
('Dirección'), ('Emisiones'), ('Vidrios'), ('Carrocería');

INSERT INTO Marcas (nombre) VALUES
('Ford'),
('Chevrolet'),
('Renault');

-- La contraseña es 'test' hasheada con bcrypt
INSERT INTO Usuarios (username, password_hash, rol) VALUES
('cliente_test', '$2b$12$EUeZhTmRfR/h4YeS2M7VH.x7aCJnK7RynCvzQJU4mM/g2EzDxsL06', 'CLIENTE'),
('inspector_test', '$2b$12$EUeZhTmRfR/h4YeS2M7VH.x7aCJnK7RynCvzQJU4mM/g2EzDxsL06', 'INSPECTOR'),
('administrador_test', '$2b$12$EUeZhTmRfR/h4YeS2M7VH.x7aCJnK7RynCvzQJU4mM/g2EzDxsL06', 'ADMINISTRADOR');

-- Función de SQL que me permite cargar horarios de disponibilidad de 9:00 a 18:00 cada 30 minutos
-- El enfoque que se utilizo para el trabajo práctico es el de bloques fijos existentes en el día en la tabla de Turnos
SET @start_time = CAST(DATE(NOW()) AS DATETIME) + INTERVAL 9 HOUR;
SET @end_time = CAST(DATE(NOW()) AS DATETIME) + INTERVAL 18 HOUR;
SET @i = -30;

INSERT INTO Turnos (matricula, fecha, estado)
SELECT
    NULL,
    DATE_ADD(@start_time, INTERVAL t.hora_slot MINUTE),
    'LIBRE'
FROM
    (
        SELECT (@i := @i + 30) AS hora_slot
        FROM information_schema.columns AS a, information_schema.columns AS b
        LIMIT 36
    ) AS t
WHERE
    DATE_ADD(@start_time, INTERVAL t.hora_slot MINUTE) < @end_time;