"""
app.py — Orquestador Principal del Dashboard Agromatica
========================================================
Responsabilidad ÚNICA: ensamblar los componentes visuales,
gestionar el estado de la UI y coordinar el flujo de datos
entre el sidebar (filtros) y las secciones del dashboard.

NO contiene lógica de negocio ni consultas SQL.

Ejecutar:
    streamlit run app.py
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import streamlit as st

# ── Asegurar que el paquete 'agromatica' sea importable ──
# (necesario cuando se ejecuta desde el directorio raíz del proyecto)
sys.path.insert(0, str(Path(__file__).parent))

# ── Importaciones de la aplicación ───────────────────────
from agromatica.components.charts import (
    chart_calidad_por_cultivo,
    chart_distribucion_calidad,
    chart_humedad_vs_rendimiento,
    chart_insumos_por_categoria,
    chart_produccion_anual,
    chart_rendimiento_por_cultivo,
)
from agromatica.components.kpi_cards import render_kpi_cards
from agromatica.components.tables import render_data_table, render_stats_summary
from agromatica.database import FiltrosAgricolas, check_connection
from agromatica.services import (
    calcular_correlacion_pearson,
    compute_kpis,
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

# ─────────────────────────────────────────────────────────
# 0. CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Agromatica · Dashboard Analítico",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "**Agromatica Analytics Dashboard** v1.0 · Sistema de gestión inteligente de cultivos.",
    },
)

# ─────────────────────────────────────────────────────────
# 1. INYECCIÓN DE ESTILOS CSS GLOBALES
# ─────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    /* ── Google Font: Inter ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Variables de diseño ── */
    :root {
        --bg:        #0f172a;
        --surface:   #1e293b;
        --surface2:  #1e293b;
        --primary:   #10b981;
        --accent:    #f59e0b;
        --info:      #6366f1;
        --text:      #f8fafc;
        --text-muted:#94a3b8;
        --border:    #334155;
        --radius:    12px;
    }

    /* ── Fondo general ── */
    .stApp { background-color: var(--bg); font-family: 'Inter', sans-serif; }
    section[data-testid="stSidebar"] { background-color: var(--surface); border-right: 1px solid var(--border); }

    /* ── Encabezados ── */
    h1, h2, h3 { color: var(--text) !important; font-family: 'Inter', sans-serif; }
    h1 { font-size: 1.9rem !important; font-weight: 700; }
    h2 { font-size: 1.3rem !important; font-weight: 600; }
    h3 { font-size: 1.05rem !important; font-weight: 500; }

    /* ── Tarjetas de métricas KPI ── */
    [data-testid="metric-container"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 20px 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
        border-color: var(--primary);
    }
    [data-testid="metric-container"] label {
        color: var(--text-muted) !important; font-size: 0.78rem !important;
        text-transform: uppercase; letter-spacing: 0.06em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--text) !important; font-size: 1.8rem !important; font-weight: 700;
        white-space: nowrap !important;
        overflow: visible !important;
    }
    [data-testid="stMetricValue"] > div {
        white-space: nowrap !important;
        overflow: visible !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
    }

    /* ── Expander ── */
    details {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 4px;
    }
    details summary { color: var(--text) !important; font-weight: 600; }

    /* ── Divider ── */
    hr { border-color: var(--border) !important; margin: 1.5rem 0; }

    /* ── Sidebar widgets ── */
    .stSelectbox label, .stMultiSelect label, .stDateInput label,
    .stSlider label, .stCheckbox label { color: var(--text-muted) !important; font-size: 0.8rem; }

    /* ── Botón de descarga ── */
    .stDownloadButton button {
        background: linear-gradient(135deg, var(--primary), #1A6B47);
        color: white; border: none; border-radius: 6px;
        font-weight: 600; transition: all 0.2s ease;
    }
    .stDownloadButton button:hover {
        background: linear-gradient(135deg, #1A6B47, var(--primary));
        box-shadow: 0 4px 12px rgba(45,155,111,0.4);
    }

    /* ── Info/Warning banners ── */
    [data-testid="stAlert"] { border-radius: var(--radius); }

    /* ── DataFrames ── */
    [data-testid="stDataFrame"] { border-radius: var(--radius); overflow: hidden; }

    /* ── Plotly charts container ── */
    [data-testid="stPlotlyChart"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }

    /* ── Sección divisoria con badge ── */
    .section-badge {
        display: inline-flex; align-items: center; gap: 8px;
        background: linear-gradient(135deg, var(--primary)22, var(--primary)11);
        border: 1px solid var(--primary)55;
        border-radius: 20px; padding: 4px 14px;
        color: var(--primary); font-weight: 600; font-size: 0.82rem;
        text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;
    }

    /* ── Logo header ── */
    .app-header {
        display: flex; align-items: center; gap: 16px;
        padding: 12px 0 20px; border-bottom: 1px solid var(--border);
        margin-bottom: 24px;
    }
    .app-title { font-size: 2rem; font-weight: 800; color: var(--text); letter-spacing: -0.02em; }
    .app-subtitle { color: var(--text-muted); font-size: 0.88rem; margin-top: 2px; }
    .brand-pill {
        background: linear-gradient(135deg, var(--primary), #1A6B47);
        color: white; padding: 6px 14px; border-radius: 20px;
        font-weight: 700; font-size: 0.8rem; letter-spacing: 0.04em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────
# 2. SIDEBAR — CONTROLES GLOBALES Y ESTADO DE CONEXIÓN
# ─────────────────────────────────────────────────────────

def _render_sidebar() -> FiltrosAgricolas:
    """
    Renderiza el sidebar con todos los controles de filtrado y
    retorna un objeto FiltrosAgricolas con los valores seleccionados.
    """
    with st.sidebar:
        # Logo / branding
        st.markdown(
            '<div style="text-align:center;padding:10px 0 24px;">'
            '<div style="font-size:2.5rem;">🌿</div>'
            '<div style="font-size:1.1rem;font-weight:700;color:#E2E8F0;margin-top:4px;">AGROMATICA</div>'
            '<div style="font-size:0.72rem;color:#64748B;letter-spacing:0.08em;">ANALYTICS DASHBOARD</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        # ── Estado de conexión ──
        st.markdown("##### 🔌 Estado de Conexión")
        if "conn_status" not in st.session_state:
            st.session_state.conn_status = None

        if st.button("Verificar conexión", use_container_width=True, key="btn_check_conn"):
            with st.spinner("Verificando..."):
                ok, msg = check_connection()
                st.session_state.conn_status = (ok, msg)

        if st.session_state.conn_status:
            ok, msg = st.session_state.conn_status
            if ok:
                st.success(msg, icon="✅")
            else:
                st.error(msg, icon="❌")

        st.divider()

        # ── Filtros agrícolas ──
        st.markdown("##### 🔍 Filtros de Análisis")

        # Cultivos
        try:
            cultivos_disponibles = get_cultivos_cached()
        except Exception:
            cultivos_disponibles = []

        cultivos_sel: list[str] = st.multiselect(
            "🌾 Cultivo(s)",
            options=cultivos_disponibles,
            default=[],
            placeholder="Todos los cultivos",
            key="filter_cultivos",
        )

        # Fincas
        try:
            fincas_disponibles = get_fincas_cached()
        except Exception:
            fincas_disponibles = []

        fincas_sel: list[str] = st.multiselect(
            "🏡 Finca(s)",
            options=fincas_disponibles,
            default=[],
            placeholder="Todas las fincas",
            key="filter_fincas",
        )

        # Rango de fechas
        try:
            fecha_min_db, fecha_max_db = get_rango_fechas_cached()
        except Exception:
            fecha_min_db, fecha_max_db = None, None

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fecha_inicio = st.date_input(
                "📅 Desde",
                value=fecha_min_db or date(2020, 1, 1),
                key="filter_fecha_inicio",
            )
        with col_f2:
            fecha_fin = st.date_input(
                "📅 Hasta",
                value=fecha_max_db or date.today(),
                key="filter_fecha_fin",
            )

        # Estado del lote
        estado_sel = st.selectbox(
            "📌 Estado del lote",
            options=["Todos", "activo", "cosechado", "en_preparacion", "abandonado"],
            key="filter_estado",
        )

        st.divider()

        # Botón de limpieza
        if st.button("🔄 Limpiar filtros", use_container_width=True, key="btn_clear"):
            for key in ["filter_cultivos", "filter_fincas", "filter_estado"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        # Info de caché
        st.caption("⚡ Los datos se actualizan automáticamente cada 10 minutos.")

    return FiltrosAgricolas(
        cultivos=cultivos_sel,
        fincas=fincas_sel,
        fecha_inicio=fecha_inicio if isinstance(fecha_inicio, date) else None,
        fecha_fin=fecha_fin if isinstance(fecha_fin, date) else None,
        estado_lote=None if estado_sel == "Todos" else estado_sel,
    )


# ─────────────────────────────────────────────────────────
# 3. HEADER PRINCIPAL
# ─────────────────────────────────────────────────────────

def _render_header() -> None:
    st.markdown(
        """
        <div class="app-header">
            <div>
                <div class="app-title">🌿 Agromatica</div>
                <div class="app-subtitle">Sistema Inteligente de Gestión y Análisis de Cultivos</div>
            </div>
            <div style="margin-left:auto;">
                <span class="brand-pill">Dashboard Analítico</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────
# 4. NIVEL 1 — KPI Cards
# ─────────────────────────────────────────────────────────

def _render_kpis(filtros: FiltrosAgricolas) -> None:
    st.markdown(
        '<div class="section-badge">📊 Métricas Clave</div>',
        unsafe_allow_html=True,
    )
    with st.spinner("Calculando métricas..."):
        try:
            metrics = compute_kpis(filtros)
            render_kpi_cards(metrics)
        except Exception as exc:
            st.error(
                f"⚠️ No se pudieron cargar las métricas. "
                f"Verifica la conexión a la base de datos.\n\n`{exc}`"
            )


# ─────────────────────────────────────────────────────────
# 5. NIVEL 2 — Visualizaciones analíticas
# ─────────────────────────────────────────────────────────

def _render_charts(filtros: FiltrosAgricolas) -> None:
    st.divider()
    st.markdown(
        '<div class="section-badge">📈 Análisis Visual</div>',
        unsafe_allow_html=True,
    )

    # ── Fila 1: Rendimiento | Producción anual ──
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        with st.spinner("Cargando rendimiento..."):
            try:
                df_rend = get_df_rendimiento(filtros)
                fig = chart_rendimiento_por_cultivo(df_rend)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            except Exception as exc:
                st.warning(f"No se pudo cargar el gráfico de rendimiento: {exc}")

    with col2:
        with st.spinner("Cargando producción anual..."):
            try:
                df_prod = get_df_produccion_anual(filtros)
                fig = chart_produccion_anual(df_prod)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            except Exception as exc:
                st.warning(f"No se pudo cargar el gráfico de producción: {exc}")

    # ── Fila 2: Correlación humedad | Distribución calidad ──
    col3, col4 = st.columns([3, 2], gap="medium")

    with col3:
        with st.spinner("Calculando correlación ambiental..."):
            try:
                df_hum = get_df_humedad_rendimiento(filtros)
                correlacion = calcular_correlacion_pearson(df_hum)
                fig = chart_humedad_vs_rendimiento(df_hum, correlacion)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            except Exception as exc:
                st.warning(f"No se pudo cargar el scatter de correlación: {exc}")

    with col4:
        with st.spinner("Cargando distribución de calidad..."):
            try:
                df_cal = get_df_calidad(filtros)
                fig = chart_distribucion_calidad(df_cal)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            except Exception as exc:
                st.warning(f"No se pudo cargar el gráfico de calidad: {exc}")

    # ── Fila 3: Calidad por cultivo | Insumos por categoría ──
    col5, col6 = st.columns(2, gap="medium")

    with col5:
        with st.spinner("Cargando calidad por cultivo..."):
            try:
                df_cal_cult = get_df_calidad(filtros)
                fig = chart_calidad_por_cultivo(df_cal_cult)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            except Exception as exc:
                st.warning(f"No se pudo cargar el gráfico de calidad por cultivo: {exc}")

    with col6:
        with st.spinner("Cargando insumos agrícolas..."):
            try:
                df_insumos = get_df_insumos(filtros)
                fig = chart_insumos_por_categoria(df_insumos)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            except Exception as exc:
                st.warning(f"No se pudo cargar el gráfico de insumos: {exc}")


# ─────────────────────────────────────────────────────────
# 6. NIVEL 3 — Detalle y Acción (Expander)
# ─────────────────────────────────────────────────────────

def _render_detail_table(filtros: FiltrosAgricolas) -> None:
    st.divider()
    st.markdown(
        '<div class="section-badge">🗂️ Datos Detallados</div>',
        unsafe_allow_html=True,
    )

    with st.expander("📋 Ver tabla completa de lotes y cosechas", expanded=False):
        with st.spinner("Cargando registros detallados..."):
            try:
                df_lotes = get_df_lotes_detalle(filtros)
                render_data_table(
                    df_lotes,
                    title="Lotes de Cultivo y Cosechas",
                    page_size=25,
                    key_prefix="lotes",
                    highlight_col="Rendimiento (kg/ha)",
                )
            except Exception as exc:
                st.error(f"Error cargando detalle: {exc}")

    with st.expander("📊 Estadísticas descriptivas", expanded=False):
        with st.spinner("Calculando estadísticas..."):
            try:
                df_rend = get_df_rendimiento(filtros)
                if not df_rend.empty:
                    st.markdown("**Resumen de Rendimiento por Cultivo:**")
                    render_stats_summary(
                        df_rend,
                        numeric_cols=["rendimiento_promedio", "produccion_total_kg"],
                    )
            except Exception as exc:
                st.warning(f"No se pudieron calcular estadísticas: {exc}")


# ─────────────────────────────────────────────────────────
# 7. FOOTER
# ─────────────────────────────────────────────────────────

def _render_footer() -> None:
    st.divider()
    st.markdown(
        """
        <div style="text-align:center;padding:16px 0;color:#475569;font-size:0.78rem;">
            <span>🌿 <strong style="color:#2D9B6F;">Agromatica Analytics</strong> v1.0</span>
            &nbsp;·&nbsp;
            <span>Sistema Inteligente de Gestión de Cultivos</span>
            &nbsp;·&nbsp;
            <span>Datos actualizados automáticamente cada 10 min</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────
# 8. PUNTO DE ENTRADA PRINCIPAL
# ─────────────────────────────────────────────────────────

def main() -> None:
    """Función principal del dashboard. Orquesta todos los componentes."""
    # Sidebar (retorna los filtros activos)
    filtros = _render_sidebar()

    # Contenido principal
    _render_header()
    _render_kpis(filtros)
    _render_charts(filtros)
    _render_detail_table(filtros)
    _render_footer()


if __name__ == "__main__":
    main()
