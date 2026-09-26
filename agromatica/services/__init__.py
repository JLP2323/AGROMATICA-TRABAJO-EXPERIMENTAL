"""agromatica/services/__init__.py"""
from .agro_analytics import (
    KPIMetrics,
    calcular_correlacion_pearson,
    clasificar_rendimiento,
    compute_kpis,
    describe_df,
    get_cultivos_cached,
    get_df_calidad,
    get_df_humedad_rendimiento,
    get_df_insumos,
    get_df_lotes_detalle,
    get_df_produccion_anual,
    get_df_rendimiento,
    get_fincas_cached,
    get_rango_fechas_cached,
)

__all__ = [
    "KPIMetrics",
    "calcular_correlacion_pearson",
    "clasificar_rendimiento",
    "compute_kpis",
    "describe_df",
    "get_cultivos_cached",
    "get_df_calidad",
    "get_df_humedad_rendimiento",
    "get_df_insumos",
    "get_df_lotes_detalle",
    "get_df_produccion_anual",
    "get_df_rendimiento",
    "get_fincas_cached",
    "get_rango_fechas_cached",
]
