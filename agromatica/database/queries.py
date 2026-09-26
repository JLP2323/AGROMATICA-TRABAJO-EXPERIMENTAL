"""
database/queries.py
-------------------
Consultas SQL puras, parametrizadas y desacopladas de toda lógica visual.
Cada función retorna un DataFrame de pandas o tuplas crudas, NUNCA
realiza formateos para UI ni lógica de negocio compleja.

Todas las consultas aceptan filtros opcionales vía parámetros tipados
y usan el engine SQLAlchemy para aprovechar el pool de conexiones.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

import pandas as pd
from sqlalchemy import text

from agromatica.database.connection import get_sqlalchemy_engine

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────
# Modelo de filtros (desacoplado de UI y negocio)
# ──────────────────────────────────────────────────────────

@dataclass
class FiltrosAgricolas:
    """Parámetros de filtrado para las consultas del dashboard agrícola."""

    cultivos: list[str] = field(default_factory=list)
    """Lista de tipos de cultivo a incluir (vacío = todos)."""

    fincas: list[str] = field(default_factory=list)
    """Lista de nombres de finca a incluir (vacío = todas)."""

    fecha_inicio: Optional[date] = None
    """Fecha mínima de siembra o cosecha (inclusive)."""

    fecha_fin: Optional[date] = None
    """Fecha máxima de siembra o cosecha (inclusive)."""

    estado_lote: Optional[str] = None
    """Estado del lote: 'activo', 'cosechado', 'en_preparacion', etc."""


# ──────────────────────────────────────────────────────────
# Helpers internos
# ──────────────────────────────────────────────────────────

def _execute_query(sql: str, params: Optional[dict] = None) -> pd.DataFrame:
    """
    Ejecuta una consulta SQL y retorna el resultado como DataFrame.
    Centraliza el manejo de errores y logging de queries.
    """
    engine = get_sqlalchemy_engine()
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn, params=params or {})
        logger.debug("Query ejecutada. Filas retornadas: %d", len(df))
        return df
    except Exception as exc:
        logger.error("Error ejecutando query: %s | SQL: %.200s", exc, sql)
        raise


def _build_where_clauses(
    filtros: FiltrosAgricolas,
    cultivo_col: str = "lc.tipo_cultivo",
    finca_col: str = "f.nombre",
    fecha_col: str = "lc.fecha_siembra",
    estado_col: str = "lc.estado_actual",
) -> tuple[list[str], dict]:
    """
    Genera dinámicamente las cláusulas WHERE y el dict de parámetros
    a partir de un objeto FiltrosAgricolas.
    """
    clauses: list[str] = []
    params: dict = {}

    if filtros.cultivos:
        clauses.append(f"{cultivo_col} = ANY(:cultivos)")
        params["cultivos"] = filtros.cultivos

    if filtros.fincas:
        clauses.append(f"{finca_col} = ANY(:fincas)")
        params["fincas"] = filtros.fincas

    if filtros.fecha_inicio:
        clauses.append(f"{fecha_col} >= :fecha_inicio")
        params["fecha_inicio"] = filtros.fecha_inicio

    if filtros.fecha_fin:
        clauses.append(f"{fecha_col} <= :fecha_fin")
        params["fecha_fin"] = filtros.fecha_fin

    if filtros.estado_lote:
        clauses.append(f"{estado_col} = :estado_lote")
        params["estado_lote"] = filtros.estado_lote

    return clauses, params


# ──────────────────────────────────────────────────────────
# Consultas de catálogo (para poblar selectores de UI)
# ──────────────────────────────────────────────────────────

def get_cultivos_disponibles() -> list[str]:
    """Retorna la lista de tipos de cultivo únicos registrados."""
    sql = """
        SELECT DISTINCT tipo_cultivo
        FROM lote_cultivo
        WHERE tipo_cultivo IS NOT NULL
        ORDER BY tipo_cultivo
    """
    df = _execute_query(sql)
    return df["tipo_cultivo"].tolist() if not df.empty else []


def get_fincas_disponibles() -> list[str]:
    """Retorna la lista de nombres de finca únicos registrados."""
    sql = """
        SELECT DISTINCT nombre
        FROM finca
        WHERE nombre IS NOT NULL
        ORDER BY nombre
    """
    df = _execute_query(sql)
    return df["nombre"].tolist() if not df.empty else []


def get_rango_fechas() -> tuple[Optional[date], Optional[date]]:
    """
    Retorna el rango mínimo y máximo de fechas de siembra disponibles.
    Útil para inicializar los date_input del sidebar.
    """
    sql = """
        SELECT
            MIN(fecha_siembra)::date AS fecha_min,
            MAX(fecha_siembra)::date AS fecha_max
        FROM lote_cultivo
        WHERE fecha_siembra IS NOT NULL
    """
    df = _execute_query(sql)
    if df.empty or df.iloc[0]["fecha_min"] is None:
        return None, None
    row = df.iloc[0]
    return row["fecha_min"], row["fecha_max"]


# ──────────────────────────────────────────────────────────
# Consultas analíticas principales
# ──────────────────────────────────────────────────────────

def get_resumen_kpis(filtros: FiltrosAgricolas) -> pd.DataFrame:
    """
    Retorna métricas agregadas globales para las KPI cards:
    - rendimiento_promedio: promedio de kg/ha
    - humedad_media: promedio de humedad del suelo (%)
    - total_hectareas: suma de hectáreas evaluadas
    - total_registros: cantidad de cosechas registradas
    - total_produccion_kg: suma total de kilogramos cosechados
    """
    clauses, params = _build_where_clauses(filtros)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    sql = f"""
        SELECT
            ROUND(AVG(c.cantidad_kg / NULLIF(f.extension_hectareas, 0))::numeric, 2)
                AS rendimiento_promedio,
            ROUND(AVG(mc.humedad)::numeric, 1)
                AS humedad_media,
            ROUND(SUM(DISTINCT f.extension_hectareas)::numeric, 2)
                AS total_hectareas,
            COUNT(c.id_cosecha)
                AS total_registros,
            ROUND(SUM(c.cantidad_kg)::numeric, 0)
                AS total_produccion_kg
        FROM lote_cultivo lc
        JOIN finca f ON f.id_finca = lc.id_finca
        LEFT JOIN cosecha c ON c.id_lote = lc.numero_lote
        LEFT JOIN monitoreo_climatico mc ON mc.id_lote = lc.numero_lote
        {where}
    """
    return _execute_query(sql, params)


def get_rendimiento_por_cultivo(filtros: FiltrosAgricolas) -> pd.DataFrame:
    """
    Retorna el rendimiento promedio (kg/ha) agrupado por tipo de cultivo.

    Columnas: cultivo, rendimiento_promedio, total_cosechas, produccion_total_kg
    """
    clauses, params = _build_where_clauses(filtros)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    sql = f"""
        SELECT
            lc.tipo_cultivo AS cultivo,
            ROUND(AVG(c.cantidad_kg / NULLIF(f.extension_hectareas, 0))::numeric, 2)
                AS rendimiento_promedio,
            COUNT(c.id_cosecha) AS total_cosechas,
            ROUND(SUM(c.cantidad_kg)::numeric, 0) AS produccion_total_kg
        FROM lote_cultivo lc
        JOIN finca f ON f.id_finca = lc.id_finca
        LEFT JOIN cosecha c ON c.id_lote = lc.numero_lote
        {where}
        GROUP BY lc.tipo_cultivo
        HAVING COUNT(c.id_cosecha) > 0
        ORDER BY rendimiento_promedio DESC
    """
    return _execute_query(sql, params)


def get_produccion_por_anio(filtros: FiltrosAgricolas) -> pd.DataFrame:
    """
    Retorna la producción total (kg) agrupada por año de cosecha.

    Columnas: anio, produccion_total_kg, total_cosechas
    """
    clauses, params = _build_where_clauses(
        filtros, fecha_col="c.fecha"
    )
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    sql = f"""
        SELECT
            EXTRACT(YEAR FROM c.fecha)::int AS anio,
            ROUND(SUM(c.cantidad_kg)::numeric, 0) AS produccion_total_kg,
            COUNT(c.id_cosecha) AS total_cosechas
        FROM cosecha c
        JOIN lote_cultivo lc ON lc.numero_lote = c.id_lote
        JOIN finca f ON f.id_finca = lc.id_finca
        {where}
        GROUP BY anio
        ORDER BY anio
    """
    return _execute_query(sql, params)


def get_humedad_vs_rendimiento(filtros: FiltrosAgricolas) -> pd.DataFrame:
    """
    Retorna datos para el scatter plot de correlación humedad vs. rendimiento.

    Columnas: cultivo, humedad, rendimiento_kg_ha, finca
    """
    clauses, params = _build_where_clauses(filtros)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    sql = f"""
        SELECT
            lc.tipo_cultivo AS cultivo,
            mc.humedad,
            ROUND((c.cantidad_kg / NULLIF(f.extension_hectareas, 0))::numeric, 2)
                AS rendimiento_kg_ha,
            f.nombre AS finca,
            c.calidad
        FROM lote_cultivo lc
        JOIN finca f ON f.id_finca = lc.id_finca
        JOIN cosecha c ON c.id_lote = lc.numero_lote
        JOIN monitoreo_climatico mc ON mc.id_lote = lc.numero_lote
        {where}
        ORDER BY lc.tipo_cultivo
    """
    return _execute_query(sql, params)


def get_distribucion_calidad(filtros: FiltrosAgricolas) -> pd.DataFrame:
    """
    Retorna la distribución de calidad de cosechas por cultivo.

    Columnas: cultivo, calidad, cantidad
    """
    clauses, params = _build_where_clauses(filtros)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    sql = f"""
        SELECT
            lc.tipo_cultivo AS cultivo,
            c.calidad,
            COUNT(*) AS cantidad
        FROM cosecha c
        JOIN lote_cultivo lc ON lc.numero_lote = c.id_lote
        JOIN finca f ON f.id_finca = lc.id_finca
        {where}
        GROUP BY lc.tipo_cultivo, c.calidad
        ORDER BY lc.tipo_cultivo, cantidad DESC
    """
    return _execute_query(sql, params)


def get_lotes_detalle(filtros: FiltrosAgricolas) -> pd.DataFrame:
    """
    Retorna el detalle completo de lotes para la tabla paginada de la UI.

    Columnas: finca, lote, cultivo, fecha_siembra, fecha_cosecha_est,
              estado, total_cosecha_kg, rendimiento_kg_ha, calidad
    """
    clauses, params = _build_where_clauses(filtros)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    sql = f"""
        SELECT
            f.nombre AS finca,
            lc.numero_lote AS lote,
            lc.tipo_cultivo AS cultivo,
            lc.fecha_siembra,
            lc.fecha_estimada_cosecha,
            lc.estado_actual AS estado,
            ROUND(SUM(c.cantidad_kg)::numeric, 0) AS total_cosecha_kg,
            ROUND(AVG(c.cantidad_kg / NULLIF(f.extension_hectareas, 0))::numeric, 2)
                AS rendimiento_kg_ha,
            MODE() WITHIN GROUP (ORDER BY c.calidad) AS calidad_predominante
        FROM lote_cultivo lc
        JOIN finca f ON f.id_finca = lc.id_finca
        LEFT JOIN cosecha c ON c.id_lote = lc.numero_lote
        {where}
        GROUP BY f.nombre, lc.numero_lote, lc.tipo_cultivo,
                 lc.fecha_siembra, lc.fecha_estimada_cosecha, lc.estado_actual
        ORDER BY f.nombre, lc.numero_lote
    """
    return _execute_query(sql, params)


def get_insumos_por_cultivo(filtros: FiltrosAgricolas) -> pd.DataFrame:
    """
    Retorna el total de insumos aplicados agrupado por cultivo y categoría.

    Columnas: cultivo, categoria_insumo, nombre_insumo, total_aplicado, unidad
    """
    clauses, params = _build_where_clauses(filtros)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    sql = f"""
        SELECT
            lc.tipo_cultivo AS cultivo,
            ia.categoria AS categoria_insumo,
            ia.nombre AS nombre_insumo,
            ROUND(SUM(ai.cantidad_utilizada)::numeric, 2) AS total_aplicado,
            ia.unidad_medida AS unidad
        FROM lote_cultivo lc
        JOIN finca f ON f.id_finca = lc.id_finca
        JOIN aplicacion_insumo ai ON ai.id_lote = lc.numero_lote
        JOIN insumo_agricola ia ON ia.codigo = ai.id_insumo
        {where}
        GROUP BY lc.tipo_cultivo, ia.categoria, ia.nombre, ia.unidad_medida
        ORDER BY cultivo, total_aplicado DESC
    """
    return _execute_query(sql, params)
