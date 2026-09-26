"""
components/kpi_cards.py
-----------------------
Componente de renderizado de tarjetas KPI para el dashboard.
Recibe datos ya calculados y únicamente construye la UI de Streamlit.
No ejecuta queries ni lógica de negocio.
"""
from __future__ import annotations

import streamlit as st

from agromatica.services.agro_analytics import KPIMetrics, clasificar_rendimiento


def render_kpi_cards(metrics: KPIMetrics) -> None:
    """
    Renderiza la fila principal de tarjetas KPI en el dashboard.

    Diseño: 5 columnas con métricas de impacto inmediato.
    Usa st.metric con delta para mostrar tendencias.
    """
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        clasificacion = clasificar_rendimiento(metrics.rendimiento_promedio)
        st.metric(
            label="🌾 Rendimiento Prom.",
            value=f"{metrics.rendimiento_promedio:,.1f} kg/ha",
            delta=(
                f"{metrics.delta_rendimiento:+.1f}%"
                if metrics.delta_rendimiento is not None
                else None
            ),
            help=(
                f"Rendimiento promedio por hectárea · "
                f"Clasificación: {clasificacion}"
            ),
        )

    with col2:
        delta_hum_str = (
            f"{metrics.delta_humedad:+.1f}%"
            if metrics.delta_humedad is not None
            else None
        )
        st.metric(
            label="💧 Humedad Media",
            value=f"{metrics.humedad_media:.1f}%",
            delta=delta_hum_str,
            delta_color="inverse",
            help="Humedad media del suelo registrada por sensores",
        )

    with col3:
        st.metric(
            label="🗺️ Total Hectáreas",
            value=f"{metrics.total_hectareas:,.1f} ha",
            help="Suma de hectáreas evaluadas con los filtros actuales",
        )

    with col4:
        st.metric(
            label="📦 Producción Total",
            value=f"{metrics.total_produccion_kg:,.0f} kg",
            help="Kilogramos cosechados en el período seleccionado",
        )

    with col5:
        st.metric(
            label="📋 Registros",
            value=f"{metrics.total_registros:,}",
            help="Número de cosechas registradas en el sistema",
        )


def render_kpi_mini_banner(metrics: KPIMetrics) -> None:
    """
    Versión compacta en banner para uso en secciones secundarias.
    Muestra 3 métricas clave en una sola fila.
    """
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Rendimiento", f"{metrics.rendimiento_promedio:.1f} kg/ha")
    with c2:
        st.metric("Humedad", f"{metrics.humedad_media:.1f}%")
    with c3:
        st.metric("Hectáreas", f"{metrics.total_hectareas:.1f} ha")
