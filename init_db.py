import psycopg2
import os

DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "agrobio_db"
DB_USER = "postgres"
DB_PASSWORD = "Julissa2318"

sql_schema = """
-- Fincas
CREATE TABLE IF NOT EXISTS finca (
    id_finca            SERIAL PRIMARY KEY,
    nombre              VARCHAR(200),
    extension_hectareas DECIMAL(10, 2),
    tipo_suelo          VARCHAR(100)
);

-- Lotes de cultivo
CREATE TABLE IF NOT EXISTS lote_cultivo (
    numero_lote              SERIAL PRIMARY KEY,
    tipo_cultivo             VARCHAR(100),
    fecha_siembra            DATE,
    fecha_estimada_cosecha   DATE,
    estado_actual            VARCHAR(50),
    id_finca                 INTEGER REFERENCES finca(id_finca)
);

-- Cosechas
CREATE TABLE IF NOT EXISTS cosecha (
    id_cosecha   SERIAL PRIMARY KEY,
    fecha        DATE,
    cantidad_kg  DECIMAL(12, 2),
    calidad      VARCHAR(50),
    id_lote      INTEGER REFERENCES lote_cultivo(numero_lote)
);

-- Monitoreo ambiental (sensores)
CREATE TABLE IF NOT EXISTS monitoreo_climatico (
    id          SERIAL PRIMARY KEY,
    temperatura DECIMAL(5, 2),
    humedad     DECIMAL(5, 2),
    ph_suelo    DECIMAL(4, 2),
    id_lote     INTEGER REFERENCES lote_cultivo(numero_lote)
);

-- Insumos agricolas
CREATE TABLE IF NOT EXISTS insumo_agricola (
    codigo           VARCHAR(50) PRIMARY KEY,
    nombre           VARCHAR(200),
    categoria        VARCHAR(100),
    unidad_medida    VARCHAR(30),
    stock_disponible DECIMAL(12, 2)
);

-- Aplicacion de insumos
CREATE TABLE IF NOT EXISTS aplicacion_insumo (
    id_aplicacion      SERIAL PRIMARY KEY,
    fecha_aplicacion   DATE,
    cantidad_utilizada DECIMAL(10, 2),
    id_lote            INTEGER REFERENCES lote_cultivo(numero_lote),
    id_insumo          VARCHAR(50) REFERENCES insumo_agricola(codigo)
);
"""

sql_seed_data = """
INSERT INTO finca (nombre, extension_hectareas, tipo_suelo) VALUES 
('Finca El Sol', 150.5, 'Arcilloso'),
('Hacienda La Esperanza', 200.0, 'Arenoso') ON CONFLICT DO NOTHING;

INSERT INTO lote_cultivo (tipo_cultivo, fecha_siembra, fecha_estimada_cosecha, estado_actual, id_finca) VALUES 
('Maíz', '2023-01-15', '2023-06-15', 'Cosechado', 1),
('Soya', '2023-02-10', '2023-07-10', 'Cosechado', 1),
('Trigo', '2023-03-05', '2023-08-05', 'Activo', 2),
('Arroz', '2023-04-20', '2023-09-20', 'Activo', 2) ON CONFLICT DO NOTHING;

INSERT INTO cosecha (fecha, cantidad_kg, calidad, id_lote) VALUES 
('2023-06-20', 45000.5, 'Alta', 1),
('2023-07-15', 38000.0, 'Media', 2) ON CONFLICT DO NOTHING;

INSERT INTO monitoreo_climatico (temperatura, humedad, ph_suelo, id_lote) VALUES 
(25.5, 60.0, 6.5, 1),
(26.0, 58.5, 6.4, 1),
(24.0, 65.0, 6.8, 2),
(22.5, 70.0, 6.2, 3),
(28.0, 55.0, 6.1, 4) ON CONFLICT DO NOTHING;

INSERT INTO insumo_agricola (codigo, nombre, categoria, unidad_medida, stock_disponible) VALUES 
('FERT-001', 'Urea', 'Fertilizante', 'kg', 5000.0),
('PEST-001', 'Glifosato', 'Pesticida', 'litros', 1000.0),
('SEM-001', 'Semilla Maíz Híbrido', 'Semilla', 'kg', 2000.0) ON CONFLICT DO NOTHING;

INSERT INTO aplicacion_insumo (fecha_aplicacion, cantidad_utilizada, id_lote, id_insumo) VALUES 
('2023-02-01', 500.0, 1, 'FERT-001'),
('2023-03-15', 50.0, 1, 'PEST-001'),
('2023-01-15', 200.0, 1, 'SEM-001') ON CONFLICT DO NOTHING;
"""

try:
    print("Conectando a la base de datos...")
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Creando tablas...")
    cursor.execute(sql_schema)
    print("Tablas creadas exitosamente.")
    
    print("Insertando datos de prueba...")
    cursor.execute(sql_seed_data)
    print("Datos insertados exitosamente.")
    
    cursor.close()
    conn.close()
    print("Configuración completada.")
except Exception as e:
    print(f"Error: {e}")
