CREATE TABLE TABLE_A (
    ID NUMBER,
    NOMBRE VARCHAR2(500),
    Email_1 VARCHAR2(500),
    Email_2 VARCHAR2(500),
    Telefono VARCHAR2(50),
    Cedula VARCHAR2(50),
    CONSTRAINT pk_table_a PRIMARY KEY (ID)
);

CREATE TABLE TABLE_B (
    ID NUMBER,
    NOMBRE VARCHAR2(500),
    Email_1 VARCHAR2(500),
    Email_2 VARCHAR2(500),
    Telefono VARCHAR2(50),
    Cedula VARCHAR2(50),
    UUID RAW(16),
    CONSTRAINT pk_table_b PRIMARY KEY (ID)
);

CREATE TABLE TABLE_C (
    ID NUMBER,
    NOMBRE VARCHAR2(500),
    Email_1 VARCHAR2(500),
    Email_2 VARCHAR2(500),
    Telefono VARCHAR2(50),
    Cedula VARCHAR2(50),
    UUID RAW(16),
    CONSTRAINT pk_table_c PRIMARY KEY (ID)
);

INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (1, 'Johan Pool', 'Johan.Pool.2024@seti.com.co', 'Johan.Pool.seti@microsoft.com.co', '323 593 3317', '1108789359');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (2, 'Ana Torres', 'Ana.Torres.2024@seti.com.co', 'Ana.Torres.seti@microsoft.com.co', '325 593 2317', '1108789360');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (3, 'Carlos Gomez', 'Carlos.Gomez.2024@seti.com.co', 'Carlos.Gomez.seti@microsoft.com.co', '324 593 3318', '1108789361');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (4, 'Diana Ruiz', 'Diana.Ruiz.2024@seti.com.co', 'Diana.Ruiz.seti@microsoft.com.co', '323 593 3319', '1108789362');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (5, 'Eduardo Pérez', 'Eduardo.Perez.2024@seti.com.co', 'Eduardo.Perez.seti@microsoft.com.co', '322 593 3320', '1108789363');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (6, 'Fabiola Quintero', 'Fabiola.Quintero.2024@seti.com.co', 'Fabiola.Quintero.seti@microsoft.com.co', '321 593 3321', '1108789364');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (7, 'Gustavo Morales', 'Gustavo.Morales.2024@seti.com.co', 'Gustavo.Morales.seti@microsoft.com.co', '320 593 3322', '1108789365');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (8, 'Hilda Castro', 'Hilda.Castro.2024@seti.com.co', 'Hilda.Castro.seti@microsoft.com.co', '319 593 3323', '1108789366');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (9, 'Iván López', 'Ivan.Lopez.2024@seti.com.co', 'Ivan.Lopez.seti@microsoft.com.co', '318 593 3324', '1108789367');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (10, 'Julia Martínez', 'Julia.Martinez.2024@seti.com.co', 'Julia.Martinez.seti@microsoft.com.co', '317 593 3325', '1108789368');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (11, 'Kevin Ramírez', 'Kevin.Ramirez.2024@seti.com.co', 'Kevin.Ramirez.seti@microsoft.com.co', '316 593 3326', '1108789369');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (12, 'Lorena Sánchez', 'Lorena.Sanchez.2024@seti.com.co', 'Lorena.Sanchez.seti@microsoft.com.co', '315 593 3327', '1108789370');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (13, 'Mario Vargas', 'Mario.Vargas.2024@seti.com.co', 'Mario.Vargas.seti@microsoft.com.co', '314 593 3328', '1108789371');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (14, 'María Martínez', 'maria.martinez@example.com', 'maria.martinez.personal@example.com', '555-555-5555', '1234567890');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (15, 'John Smith', 'john.smith@example.com', 'jsmith@example.com', '555-123-4567', '0987654321');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (16, 'Ana García', 'ana.garcia@example.com', 'ana.garcia.personal@example.com', '555-987-6543', '1357924680');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (17, 'Michael Johnson', 'michael.johnson@example.com', 'mjohnson@example.com', '555-111-2222', '2468013579');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (18, 'Emily Brown', 'emily.brown@example.com', 'ebrown@example.com', '555-333-4444', '3692581470');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (19, 'Daniel Rodríguez', 'daniel.rodriguez@example.com', 'drodriguez@example.com', '555-555-7777', '1472583690');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (20, 'Jessica Lee', 'jessica.lee@example.com', 'jlee@example.com', '555-888-9999', '2583691470');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (21, 'David García', 'david.garcia@example.com', 'dgarcia@example.com', '555-000-1111', '3691472580');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (22, 'Sarah Martinez', 'sarah.martinez@example.com', 'smartinez@example.com', '555-222-3333', '7894561230');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (23, 'Christopher Taylor', 'christopher.taylor@example.com', 'ctaylor@example.com', '555-444-5555', '3691472580');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (24, 'Emma Wilson', 'emma.wilson@example.com', 'ewilson@example.com', '555-666-7777', '7896541230');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (25, 'James Anderson', 'james.anderson@example.com', 'janderson@example.com', '555-888-9999', '9638527410');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (26, 'Olivia Moore', 'olivia.moore@example.com', 'omoore@example.com', '555-000-1111', '2583691470');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (27, 'Michael Taylor', 'michael.taylor@example.com', 'mtaylor@example.com', '555-222-3333', '1472583690');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (28, 'Sophia Johnson', 'sophia.johnson@example.com', 'sjohnson@example.com', '555-444-5555', '3691472580');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (29, 'Daniel Brown', 'daniel.brown@example.com', 'dbrown@example.com', '555-666-7777', '7896541230');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (30, 'Isabella Anderson', 'isabella.anderson@example.com', 'ianderson@example.com', '555-888-9999', '9638527410');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (31, 'Alexander Wilson', 'alexander.wilson@example.com', 'awilson@example.com', '555-000-1111', '2583691470');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (32, 'Ava Garcia', 'ava.garcia@example.com', 'agarcia@example.com', '555-222-3333', '1472583690');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (33, 'Ethan Taylor', 'ethan.taylor@example.com', 'etaylor@example.com', '555-444-5555', '3691472580');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (34, 'Mia Moore', 'mia.moore@example.com', 'mmoore@example.com', '555-666-7777', '7896541230');
INSERT INTO TABLE_A (ID, NOMBRE, Email_1, Email_2, Telefono, Cedula) VALUES (35, 'Noah Johnson', 'noah.johnson@example.com', 'njohnson@example.com', '555-888-9999', '9638527410');
COMMIT;