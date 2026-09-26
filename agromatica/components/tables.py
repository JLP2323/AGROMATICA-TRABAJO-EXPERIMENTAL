"""
components/tables.py
--------------------
Componente de tabla detallada con paginación y exportación CSV.
Recibe DataFrames limpios y gestiona la presentación en la UI.
No ejecuta consultas ni aplica transformaciones de negocio.
"""
from __future__ import annotations

import io
from typing import Optional

import pandas as pd
import streamlit as st


def render_data_table(
    df: pd.DataFrame,
    title: str = "📋 Detalle de Registros",
    page_size: int = 20,
    key_prefix: str = "table",
    highlight_col: Optional[str] = None,
) -> None:
    """
    Renderiza una tabla paginada con encabezado, conteo de registros
    y opciones de exportación a CSV.

    Args:
        df: DataFrame con los datos a mostrar.
        title: Título descriptivo del bloque de tabla.
        page_size: Número de filas por página.
        key_prefix: Prefijo único para los widgets de Streamlit.
        highlight_col: Columna numérica a resaltar con color de fondo.
    """
    st.subheader(title)

    if df.empty:
        st.info(
            "🌿 No hay registros que coincidan con los filtros seleccionados. "
            "Prueba ampliando el rango de fechas o seleccionando más cultivos.",
            icon="ℹ️",
        )
        return

    total = len(df)
    total_pages = max(1, (total + page_size - 1) // page_size)

    # Controles de paginación y exportación en la misma fila
    ctrl_left, ctrl_center, ctrl_right = st.columns([2, 3, 2])

    with ctrl_left:
        st.caption(f"**{total:,}** registros encontrados · Página {1}/{total_pages}")

    with ctrl_center:
        page = st.number_input(
            "Página",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1,
            key=f"{key_prefix}_page",
            label_visibility="collapsed",
        )

    with ctrl_right:
        csv_bytes = _to_csv_bytes(df)
        st.download_button(
            label="⬇️ Exportar CSV",
            data=csv_bytes,
            file_name="agromatica_datos.csv",
            mime="text/csv",
            key=f"{key_prefix}_download",
            use_container_width=True,
        )

    # Slice de la página actual
    start = (page - 1) * page_size
    end = min(start + page_size, total)
    page_df = df.iloc[start:end]

    # Estilo de la tabla
    styled = _apply_table_style(page_df, highlight_col)

    st.dataframe(
        styled,
        use_container_width=True,
        height=min(40 + len(page_df) * 36, 600),
        hide_index=True,
    )

    st.caption(
        f"Mostrando filas {start + 1}–{end} de {total:,} · "
        "Haz clic en los encabezados de columna para ordenar."
    )


def render_stats_summary(df: pd.DataFrame, numeric_cols: Optional[list[str]] = None) -> None:
    """
    Renderiza un resumen estadístico compacto (media, mediana, std, min, max)
    para las columnas numéricas seleccionadas del DataFrame.

    Args:
        df: DataFrame fuente.
        numeric_cols: Lista de columnas numéricas a incluir (None = todas).
    """
    if df.empty:
        return

    cols = numeric_cols or df.select_dtypes("number").columns.tolist()
    if not cols:
        return

    stats = df[cols].describe().T[["mean", "50%", "std", "min", "max"]]
    stats.columns = ["Media", "Mediana", "Desv. Est.", "Mínimo", "Máximo"]
    stats = stats.round(2)

    st.dataframe(
        stats,
        use_container_width=True,
        hide_index=False,
    )


# ──────────────────────────────────────────────────────────
# Helpers internos
# ──────────────────────────────────────────────────────────

def _to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convierte un DataFrame a bytes CSV con encoding UTF-8 BOM (Excel compatible)."""
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding="utf-8-sig")
    return buffer.getvalue().encode("utf-8-sig")


def _apply_table_style(
    df: pd.DataFrame,
    highlight_col: Optional[str] = None,
) -> "pd.io.formats.style.Styler":
    """
    Aplica estilos CSS a la tabla:
    - Fondo intercalado en filas.
    - Degradado de color en la columna resaltada.
    """
    base_styles = [
        {"selector": "thead th", "props": [
            ("background-color", "#1E2D3D"),
            ("color", "#E2E8F0"),
            ("font-weight", "600"),
            ("border-bottom", "2px solid #2D9B6F"),
        ]},
        {"selector": "tbody tr:nth-child(even)", "props": [
            ("background-color", "#253347"),
        ]},
        {"selector": "tbody tr:hover", "props": [
            ("background-color", "#2D9B6F22"),
        ]},
        {"selector": "td", "props": [
            ("color", "#CBD5E1"),
            ("font-size", "13px"),
            ("padding", "6px 12px"),
        ]},
    ]

    styler = df.style.set_table_styles(base_styles)

    if highlight_col and highlight_col in df.columns:
        styler = styler.background_gradient(
            subset=[highlight_col],
            cmap="Greens",
            low=0.1,
            high=0.9,
        )

    return styler
