<div align="center">

# Agromatica Analytics Dashboard

**Sistema Inteligente de Gestion y Analisis de Cultivos Agricolas**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-7.1-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)

*Dashboard web interactivo para el monitoreo de rendimiento de cultivos, analisis de cosechas y correlaciones ambientales en tiempo real.*

</div>

---

## Tabla de Contenidos

- [Descripcion general](#descripcion-general)
- [Caracteristicas](#caracteristicas)
- [Arquitectura del proyecto](#arquitectura-del-proyecto)
- [Requisitos previos](#requisitos-previos)
- [Instalacion](#instalacion)
- [Configuracion](#configuracion)
- [Ejecucion](#ejecucion)
- [Estructura de la base de datos](#estructura-de-la-base-de-datos)
- [Diagrama UML](#diagrama-uml-del-sistema)
- [Stack tecnologico](#stack-tecnologico)
- [Contribucion](#contribucion)

---

## Descripcion general

**Agromatica Analytics Dashboard** es una aplicacion web construida con **Streamlit** y **Plotly** que transforma datos agronomicos almacenados en PostgreSQL en visualizaciones interactivas y metricas clave de negocio.

El proyecto evoluciono desde scripts basicos de terminal (`conexion.py`, `graficos.py`) hacia una **arquitectura modular en capas** siguiendo principios de **Clean Architecture** y **SOLID**, separando estrictamente:

- La capa de acceso a datos (SQL puro)
- La capa de logica de negocio (calculos agronomicos)
- La capa de presentacion (componentes Streamlit/Plotly)

---

## Caracteristicas

### Dashboard interactivo
- **5 KPI Cards** con metricas de impacto inmediato (rendimiento, humedad, hectareas, produccion, registros)
- **6 graficos Plotly** con tooltips enriquecidos, zoom y leyendas ordenadas
- **Tabla paginada** con 25 registros por pagina y exportacion a **CSV** con un clic

### Filtrado global en tiempo real
- Filtro por **tipo de cultivo** (multiselect)
- Filtro por **finca/parcela** (multiselect)
- Filtro por **rango de fechas** (date picker)
- Filtro por **estado del lote** (activo, cosechado, en preparacion)

### Rendimiento
- **Cache multicapa** con `@st.cache_data(ttl=600)` — respuestas instantaneas en cambios de filtros
- **Pool de conexiones** SQLAlchemy con reconexion automatica (`pool_pre_ping=True`)
- **Empty states** amigables cuando los filtros no devuelven datos

### Seguridad
- Credenciales externalizadas a `.env` (git-ignorado)
- Consultas 100% **parametrizadas** — sin riesgo de SQL Injection
- Context manager con **rollback automatico** ante excepciones

---

## Arquitectura del proyecto

```
AGROMATICA TRABAJO EXPERIMENTAL/
|
|-- app.py                          <- Punto de entrada (streamlit run app.py)
|-- .env                            <- Credenciales (git-ignorado)
|-- .env.example                    <- Plantilla de entorno
|-- .streamlit/
|   `-- config.toml                 <- Tema visual de Streamlit
|-- requirements.txt                <- Dependencias
|
`-- agromatica/                     <- Paquete principal
    |
    |-- config/
    |   `-- settings.py             <- Variables de entorno con Pydantic
    |
    |-- database/
    |   |-- connection.py           <- Pool + Context Manager + rollback
    |   `-- queries.py              <- SQL puro parametrizado (DataFrames)
    |
    |-- services/
    |   `-- agro_analytics.py       <- Logica de negocio + cache
    |
    `-- components/
        |-- kpi_cards.py            <- Tarjetas de metricas
        |-- charts.py               <- Figuras Plotly (6 tipos)
        `-- tables.py               <- Tabla paginada + CSV
```

### Flujo de datos

```
PostgreSQL
    |
    v
database/connection.py     <- Pool SQLAlchemy + context manager
    |
    v
database/queries.py        <- SQL parametrizado -> DataFrame
    |
    v
services/agro_analytics.py <- Transformaciones + @st.cache_data
    |
    v
components/                <- charts.py | kpi_cards.py | tables.py
    |
    v
app.py                     <- Orquestador UI (Streamlit)
```

---

## Graficos disponibles

| # | Tipo | Descripcion |
|---|------|-------------|
| 1 | Barras horizontales | Rendimiento promedio por cultivo (kg/ha) |
| 2 | Area + linea | Produccion anual con % de crecimiento YoY |
| 3 | Scatter + trendline OLS | Correlacion humedad vs rendimiento |
| 4 | Donut | Distribucion de calidad de cosecha |
| 5 | Barras apiladas 100% | Calidad por cultivo (%) |
| 6 | Barras agrupadas | Insumos agricolas por categoria y cultivo |

---

## Requisitos previos

- **Python** 3.10 o superior
- **PostgreSQL** 13+ (corriendo en `localhost:5433`)
- Base de datos `agrobio_db` creada con el esquema del sistema

---

## Instalacion

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd "AGROMATICA TRABAJO EXPERIMENTAL"
```

### 2. Crear y activar el entorno virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar en Windows
.venv\Scripts\activate

# Activar en macOS/Linux
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Configuracion

Copia la plantilla de entorno y edita con tus credenciales:

```bash
copy .env.example .env
```

Contenido del archivo `.env`:

```env
# Conexion PostgreSQL
DB_HOST=localhost
DB_PORT=5433
DB_NAME=agrobio_db
DB_USER=postgres
DB_PASSWORD=tu_contrasena_aqui

# Pool de conexiones (valores recomendados)
DB_POOL_SIZE=5
DB_POOL_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800

# Aplicacion
APP_ENV=development
APP_CACHE_TTL=600
```

> **Importante:** El archivo `.env` esta en `.gitignore`. Nunca lo subas a control de versiones.

---

## Ejecucion

```bash
# Con el entorno virtual activado, desde la raiz del proyecto:
streamlit run app.py
```

La aplicacion abrira automaticamente en tu navegador en:

```
http://localhost:8501
```

Una vez en el dashboard, haz clic en **"Verificar conexion"** en el sidebar para confirmar que la base de datos esta accesible.

---

## Estructura de la base de datos

El dashboard espera las siguientes tablas en PostgreSQL:

```sql
-- Fincas
CREATE TABLE finca (
    id_finca            SERIAL PRIMARY KEY,
    nombre              VARCHAR(200),
    extension_hectareas DECIMAL(10, 2),
    tipo_suelo          VARCHAR(100)
);

-- Lotes de cultivo
CREATE TABLE lote_cultivo (
    numero_lote              SERIAL PRIMARY KEY,
    tipo_cultivo             VARCHAR(100),
    fecha_siembra            DATE,
    fecha_estimada_cosecha   DATE,
    estado_actual            VARCHAR(50),
    id_finca                 INTEGER REFERENCES finca(id_finca)
);

-- Cosechas
CREATE TABLE cosecha (
    id_cosecha   SERIAL PRIMARY KEY,
    fecha        DATE,
    cantidad_kg  DECIMAL(12, 2),
    calidad      VARCHAR(50),
    id_lote      INTEGER REFERENCES lote_cultivo(numero_lote)
);

-- Monitoreo ambiental (sensores)
CREATE TABLE monitoreo_climatico (
    id          SERIAL PRIMARY KEY,
    temperatura DECIMAL(5, 2),
    humedad     DECIMAL(5, 2),
    ph_suelo    DECIMAL(4, 2),
    id_lote     INTEGER REFERENCES lote_cultivo(numero_lote)
);

-- Insumos agricolas
CREATE TABLE insumo_agricola (
    codigo           VARCHAR(50) PRIMARY KEY,
    nombre           VARCHAR(200),
    categoria        VARCHAR(100),
    unidad_medida    VARCHAR(30),
    stock_disponible DECIMAL(12, 2)
);

-- Aplicacion de insumos
CREATE TABLE aplicacion_insumo (
    id_aplicacion      SERIAL PRIMARY KEY,
    fecha_aplicacion   DATE,
    cantidad_utilizada DECIMAL(10, 2),
    id_lote            INTEGER REFERENCES lote_cultivo(numero_lote),
    id_insumo          VARCHAR(50) REFERENCES insumo_agricola(codigo)
);
```

---

## Diagrama UML del sistema

El archivo `consultas.py` genera el diagrama UML con **Graphviz** que modela las 16 entidades del sistema:

```
CooperativaAgricola --administra 1..*--> Finca
                                          |
                                   posee 1|    contiene 1..*
                                          v          |
                                    UbicacionGPS  LoteCultivo --genera 0..*--> Cosecha
                                                      |
                                              registra 0..*
                                                      |
                                              AplicacionInsumo --utiliza--> InsumoAgricola
                                                                                   ^
                                                                  Semilla  Fertilizante  Pesticida

Modulos adicionales:
  Usuarios: Usuario + Rol
  Monitoreo: Sensor + MonitoreoClimatico + Alerta
  Produccion: PlanSiembra + SeguimientoCultivo + RendimientoCultivo
  Inventario: Inventario + MovimientoInventario + Proveedor
```

Para regenerar el diagrama (requiere Graphviz instalado):

```bash
python consultas.py
```

---

## Stack tecnologico

| Categoria | Tecnologia | Version | Rol |
|-----------|-----------|---------|-----|
| **UI** | Streamlit | 1.64+ | Framework web del dashboard |
| **Graficos** | Plotly | 7.1+ | Visualizaciones interactivas |
| **Estadistica** | Statsmodels | 0.14+ | Lineas de tendencia (OLS) |
| **Base de datos** | PostgreSQL | 13+ | Almacenamiento de datos agricolas |
| **Conector BD** | psycopg2-binary | 2.9+ | Driver PostgreSQL para Python |
| **ORM / Pool** | SQLAlchemy | 2.0+ | Pool de conexiones |
| **Datos** | Pandas | 2.2+ | Manipulacion de DataFrames |
| **Computo** | NumPy | 1.26+ | Operaciones numericas |
| **Configuracion** | Pydantic Settings | 2.x | Validacion de variables de entorno |
| **Entorno** | python-dotenv | 1.0+ | Carga de archivos `.env` |

---

## Principios de diseno aplicados

- **Single Responsibility**: cada modulo tiene una sola razon para cambiar
- **Open/Closed**: agregar nuevos graficos no requiere modificar `app.py`
- **Dependency Inversion**: `app.py` depende de abstracciones, no de SQL
- **DRY**: filtros definidos una vez en `FiltrosAgricolas`, usados en todas las queries
- **Cache inteligente**: `@st.cache_data(ttl=600)` evita re-consultas innecesarias

---

## Contribucion

1. Haz fork del repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Para agregar un **nuevo grafico**: modifica solo `agromatica/components/charts.py`
4. Para agregar una **nueva consulta**: modifica solo `agromatica/database/queries.py`
5. Para agregar una **nueva metrica**: modifica solo `agromatica/services/agro_analytics.py`
6. Haz commit: `git commit -m "feat: agrega grafico de temperatura vs rendimiento"`
7. Abre un Pull Request

---

## Autora

**Julissa** — Proyecto Experimental de Agromatica
Arquitectura: Python · Streamlit · Plotly · PostgreSQL

---

<div align="center">
Hecho con dedicacion y pasion por la agronomia inteligente
</div>
