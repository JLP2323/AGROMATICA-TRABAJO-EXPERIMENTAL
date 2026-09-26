"""agromatica/components/__init__.py"""
from .charts import (
    chart_calidad_por_cultivo,
    chart_distribucion_calidad,
    chart_humedad_vs_rendimiento,
    chart_insumos_por_categoria,
    chart_produccion_anual,
    chart_rendimiento_por_cultivo,
)
from .kpi_cards import render_kpi_cards, render_kpi_mini_banner
from .tables import render_data_table, render_stats_summary

__all__ = [
    "chart_calidad_por_cultivo",
    "chart_distribucion_calidad",
    "chart_humedad_vs_rendimiento",
    "chart_insumos_por_categoria",
    "chart_produccion_anual",
    "chart_rendimiento_por_cultivo",
    "render_kpi_cards",
    "render_kpi_mini_banner",
    "render_data_table",
    "render_stats_summary",
]
