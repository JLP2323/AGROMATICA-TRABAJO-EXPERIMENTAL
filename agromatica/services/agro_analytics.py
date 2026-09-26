"""
services/agro_analytics.py
--------------------------
Capa de negocio: cálculos agronómicos, transformaciones, enriquecimiento
y filtros que operan sobre DataFrames limpios provenientes de queries.py.

Esta capa NO toca la base de datos directamente ni renderiza UI.
Orquesta la lógica de dominio agrícola y expone funciones cacheadas
para uso en el dashboard.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

from agromatica.config import get_settings
from agromatica.database.queries import (
    FiltrosAgricolas,
    get_cultivos_disponibles,
    get_distribucion_calidad,
    get_fincas_disponibles,
    get_humedad_vs_rendimiento,
    get_insumos_por_cultivo,
    get_lotes_detalle,
    get_produccion_por_anio,
    get_rango_fechas,
    get_rendimiento_por_cultivo,
    get_resumen_kpis,
)

logger = logging.getLogger(__name__)
_TTL = get_settings().app.cache_ttl


# ──────────────────────────────────────────────────────────
# Modelos de datos de dominio
# ──────────────────────────────────────────────────────────

@dataclass
class KPIMetrics:
    """Métricas clave del dashboard agronómico."""

    rendimiento_promedio: float
    """Rendimiento medio en kg/ha."""

    humedad_media: float
    """Humedad media del suelo (%)."""

    total_hectareas: float
    """Total de hectáreas evaluadas."""

    total_registros: int
    """Número de cosechas registradas."""

    total_produccion_kg: float
    """Producción total en kilogramos."""

    delta_rendimiento: Optional[float] = None
    """Variación del rendimiento respecto al período anterior (%)."""

    delta_humedad: Optional[float] = None
    """Variación de la humedad respecto al período anterior (%)."""


# ──────────────────────────────────────────────────────────
# Funciones cacheadas de catálogo
# ──────────────────────────────────────────────────────────

@st.cache_data(ttl=_TTL, show_spinner=False)
def get_cultivos_cached() -> list[str]:
    """Retorna lista de cultivos disponibles (cacheada)."""
    return get_cultivos_disponibles()


@st.cache_data(ttl=_TTL, show_spinner=False)
def get_fincas_cached() -> list[str]:
    """Retorna lista de fincas disponibles (cacheada)."""
    return get_fincas_disponibles()


@st.cache_data(ttl=_TTL, show_spinner=False)
def get_rango_fechas_cached() -> tuple[Optional[object], Optional[object]]:
    """Retorna rango de fechas mínimo y máximo (cacheada)."""
    return get_rango_fechas()


# ──────────────────────────────────────────────────────────
# Funciones de negocio cacheadas
# ──────────────────────────────────────────────────────────

@st.cache_data(ttl=_TTL, show_spinner=False)
def compute_kpis(filtros: FiltrosAgricolas) -> KPIMetrics:
    """
    Calcula y retorna las métricas clave (KPIs) del dashboard
    a partir de los filtros seleccionados.

    Los valores nulos se reemplazan con 0.0 para evitar errores de render.
    """
    df = get_resumen_kpis(filtros)

    if df.empty:
        return KPIMetrics(
            rendimiento_promedio=0.0,
            humedad_media=0.0,
            total_hectareas=0.0,
            total_registros=0,
            total_produccion_kg=0.0,
        )

    row = df.iloc[0]
    return KPIMetrics(
        rendimiento_promedio=float(row.get("rendimiento_promedio") or 0.0),
        humedad_media=float(row.get("humedad_media") or 0.0),
        total_hectareas=float(row.get("total_hectareas") or 0.0),
        total_registros=int(row.get("total_registros") or 0),
        total_produccion_kg=float(row.get("total_produccion_kg") or 0.0),
    )


@st.cache_data(ttl=_TTL, show_spinner=False)
def get_df_rendimiento(filtros: FiltrosAgricolas) -> pd.DataFrame:
    """
    Retorna DataFrame de rendimiento por cultivo, enriquecido con
    la columna 'color_categoria' para mapeo visual en gráficos.
    """
    df = get_rendimiento_por_cultivo(filtros)
    if df.empty:
        return df

    # Enriquecer: clasificar rendimiento relativo
    max_rend = df["rendimiento_promedio"].max()
    df["pct_max"] = (df["rendimiento_promedio"] / max_rend * 100).round(1)
    df["categoria"] = pd.cut(
        df["rendimiento_promedio"],
        bins=[-np.inf, max_rend * 0.33, max_rend * 0.66, np.inf],
        labels=["Bajo", "Medio", "Alto"],
    ).astype(str)
    return df


@st.cache_data(ttl=_TTL, show_spinner=False)
def get_df_produccion_anual(filtros: FiltrosAgricolas) -> pd.DataFrame:
    """Retorna DataFrame de producción anual con crecimiento YoY (%)."""
    df = get_produccion_por_anio(filtros)
    if df.empty:
        return df

    df = df.sort_values("anio").reset_index(drop=True)
    df["crecimiento_yoy"] = df["produccion_total_kg"].pct_change() * 100
    df["crecimiento_yoy"] = df["crecimiento_yoy"].round(1)
    return df


@st.cache_data(ttl=_TTL, show_spinner=False)
def get_df_humedad_rendimiento(filtros: FiltrosAgricolas) -> pd.DataFrame:
    """
    Retorna DataFrame para correlación humedad vs rendimiento.
    Elimina filas con valores nulos en las columnas críticas.
    """
    df = get_humedad_vs_rendimiento(filtros)
    if df.empty:
        return df

    df = df.dropna(subset=["humedad", "rendimiento_kg_ha"])
    df["rendimiento_kg_ha"] = df["rendimiento_kg_ha"].astype(float)
    df["humedad"] = df["humedad"].astype(float)
    return df


@st.cache_data(ttl=_TTL, show_spinner=False)
def get_df_calidad(filtros: FiltrosAgricolas) -> pd.DataFrame:
    """Retorna DataFrame de distribución de calidad por cultivo."""
    return get_distribucion_calidad(filtros)


@st.cache_data(ttl=_TTL, show_spinner=False)
def get_df_lotes_detalle(filtros: FiltrosAgricolas) -> pd.DataFrame:
    """
    Retorna DataFrame del detalle de lotes con columnas formateadas
    para presentación en tabla.
    """
    df = get_lotes_detalle(filtros)
    if df.empty:
        return df

    # Formatear fechas para legibilidad
    for col in ("fecha_siembra", "fecha_estimada_cosecha"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%d/%m/%Y")

    # Renombrar columnas para la UI
    column_map = {
        "finca": "Finca",
        "lote": "Lote",
        "cultivo": "Cultivo",
        "fecha_siembra": "Siembra",
        "fecha_estimada_cosecha": "Cosecha Est.",
        "estado": "Estado",
        "total_cosecha_kg": "Producción (kg)",
        "rendimiento_kg_ha": "Rendimiento (kg/ha)",
        "calidad_predominante": "Calidad",
    }
    df = df.rename(columns=column_map)
    return df


@st.cache_data(ttl=_TTL, show_spinner=False)
def get_df_insumos(filtros: FiltrosAgricolas) -> pd.DataFrame:
    """Retorna DataFrame de insumos por cultivo."""
    return get_insumos_por_cultivo(filtros)


# ──────────────────────────────────────────────────────────
# Utilidades de análisis agronómico
# ──────────────────────────────────────────────────────────

def calcular_correlacion_pearson(df: pd.DataFrame) -> float:
    """
    Calcula el coeficiente de correlación de Pearson entre
    humedad y rendimiento_kg_ha en el DataFrame dado.

    Returns:
        Valor entre -1 y 1, o 0.0 si no hay suficientes datos.
    """
    if df.empty or len(df) < 3:
        return 0.0
    try:
        corr = df["humedad"].corr(df["rendimiento_kg_ha"])
        return round(float(corr), 3) if not np.isnan(corr) else 0.0
    except Exception:  # noqa: BLE001
        return 0.0


def clasificar_rendimiento(valor_kg_ha: float) -> str:
    """
    Clasifica un valor de rendimiento según estándares agronómicos
    típicos para pequeñas y medianas fincas latinoamericanas.
    """
    if valor_kg_ha >= 6000:
        return "🟢 Excelente"
    if valor_kg_ha >= 4000:
        return "🟡 Bueno"
    if valor_kg_ha >= 2000:
        return "🟠 Regular"
    return "🔴 Bajo"


def describe_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna estadísticas descriptivas del DataFrame con
    columnas numéricas formateadas para display en UI.
    """
    if df.empty:
        return pd.DataFrame()
    return df.describe().round(2)
