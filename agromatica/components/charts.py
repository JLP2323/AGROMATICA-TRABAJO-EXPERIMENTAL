"""
components/charts.py
--------------------
Funciones puras que reciben DataFrames limpios y retornan figuras Plotly.
NUNCA ejecutan queries, no llaman a la BD, no importan streamlit.
Principio de responsabilidad única: solo construcción visual.

Paleta de identidad agronómica:
  - Verde esmeralda:  #2D9B6F
  - Verde bosque:     #1A6B47
  - Ámbar acento:     #F59E0B
  - Azul analítico:   #3B82F6
  - Slate neutro:     #64748B
  - Fondo oscuro:     #0F1923
  - Superficie:       #1E2D3D
"""
from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Paleta de colores agronómica ──────────────────────────
PALETTE = {
    "primary":    "#10b981",
    "secondary":  "#059669",
    "accent":     "#f59e0b",
    "info":       "#6366f1",
    "slate":      "#64748b",
    "bg":         "#0f172a",
    "surface":    "#1e293b",
    "surface2":   "#1e293b",
    "text":       "#f8fafc",
    "text_muted": "#94a3b8",
    "success":    "#10b981",
    "warning":    "#ef4444",
}

QUALITATIVE_PALETTE = [
    "#10b981", "#f59e0b", "#6366f1", "#8b5cf6",
    "#ec4899", "#14b8a6", "#f97316", "#0ea5e9",
]

CATEGORY_COLORS = {
    "Alto":  "#22C55E",
    "Medio": "#F59E0B",
    "Bajo":  "#EF4444",
}


def _base_layout(title: str) -> dict:
    """Retorna el layout base con tema oscuro y tipografía consistente."""
    return dict(
        title=dict(
            text=title,
            font=dict(size=16, color=PALETTE["text"], family="Inter, sans-serif"),
            x=0.02,
            xanchor="left",
        ),
        paper_bgcolor=PALETTE["surface"],
        plot_bgcolor=PALETTE["surface2"],
        font=dict(color=PALETTE["text_muted"], size=12, family="Inter, sans-serif"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=PALETTE["surface2"],
            borderwidth=1,
            font=dict(color=PALETTE["text"]),
        ),
        margin=dict(l=40, r=20, t=40, b=40),
        hovermode="x unified",
        height=340,
        hoverlabel=dict(
            bgcolor=PALETTE["surface"],
            bordercolor=PALETTE["primary"],
            font=dict(color=PALETTE["text"], size=12),
        ),
    )


def _style_axes(fig: go.Figure, xgrid: bool = True, ygrid: bool = True) -> go.Figure:
    """Aplica estilos de ejes coherentes con el tema oscuro."""
    axis_style = dict(
        gridcolor=f"{PALETTE['slate']}33",
        zerolinecolor=f"{PALETTE['slate']}55",
        linecolor=PALETTE["surface2"],
        tickfont=dict(color=PALETTE["text_muted"]),
        title_font=dict(color=PALETTE["text_muted"]),
        showgrid=True,
    )
    fig.update_xaxes(**{**axis_style, "showgrid": xgrid})
    fig.update_yaxes(**{**axis_style, "showgrid": ygrid})
    return fig


# ──────────────────────────────────────────────────────────
# Gráfico 1: Rendimiento por cultivo (barras horizontales)
# ──────────────────────────────────────────────────────────

def chart_rendimiento_por_cultivo(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de barras horizontales mostrando el rendimiento promedio
    (kg/ha) por tipo de cultivo, coloreado por categoría de desempeño.

    Args:
        df: DataFrame con columnas [cultivo, rendimiento_promedio, categoria, pct_max]

    Returns:
        Figura Plotly lista para st.plotly_chart()
    """
    if df.empty:
        return _empty_figure("Sin datos de rendimiento para los filtros seleccionados")

    df = df.sort_values("rendimiento_promedio", ascending=True)
    color_map = {k: v for k, v in CATEGORY_COLORS.items() if k in df["categoria"].unique()}

    fig = px.bar(
        df,
        x="rendimiento_promedio",
        y="cultivo",
        color="categoria",
        color_discrete_map=color_map,
        orientation="h",
        text="rendimiento_promedio",
        custom_data=["total_cosechas", "produccion_total_kg", "pct_max"],
    )

    fig.update_traces(
        texttemplate="%{x:,.0f} kg/ha",
        textposition="outside",
        textfont=dict(color=PALETTE["text"], size=11),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Rendimiento: %{x:,.0f} kg/ha<br>"
            "% del máximo: %{customdata[2]:.1f}%<br>"
            "Cosechas: %{customdata[0]:,}<br>"
            "Producción total: %{customdata[1]:,.0f} kg"
            "<extra></extra>"
        ),
        marker=dict(line=dict(width=0)),
    )

    fig.update_layout(
        **_base_layout("🌾 Rendimiento Promedio por Cultivo"),
        xaxis_title="Rendimiento (kg/ha)",
        yaxis_title=None,
        showlegend=True,
        legend_title_text="Desempeño",
        bargap=0.3,
    )
    return _style_axes(fig, ygrid=False)


# ──────────────────────────────────────────────────────────
# Gráfico 2: Producción anual (área + línea)
# ──────────────────────────────────────────────────────────

def chart_produccion_anual(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de área + línea que muestra la evolución de la producción
    anual (kg) con anotación del crecimiento YoY.

    Args:
        df: DataFrame con columnas [anio, produccion_total_kg, total_cosechas, crecimiento_yoy]
    """
    if df.empty:
        return _empty_figure("Sin datos de producción anual")

    fig = go.Figure()

    # Área de fondo
    fig.add_trace(go.Scatter(
        x=df["anio"],
        y=df["produccion_total_kg"],
        fill="tozeroy",
        fillcolor=f"{PALETTE['primary']}22",
        line=dict(color=PALETTE["primary"], width=2.5),
        mode="lines+markers+text",
        marker=dict(
            size=9,
            color=PALETTE["accent"],
            line=dict(color=PALETTE["primary"], width=2),
        ),
        text=df["crecimiento_yoy"].apply(
            lambda v: f"{v:+.1f}%" if pd.notna(v) else ""
        ),
        textposition="top center",
        textfont=dict(color=PALETTE["accent"], size=10),
        customdata=df[["total_cosechas", "crecimiento_yoy"]].values,
        hovertemplate=(
            "<b>Año %{x}</b><br>"
            "Producción: %{y:,.0f} kg<br>"
            "Cosechas: %{customdata[0]:,}<br>"
            "Crecimiento: %{customdata[1]:+.1f}%"
            "<extra></extra>"
        ),
        name="Producción (kg)",
    ))

    fig.update_layout(
        **_base_layout("📈 Evolución de Producción Anual"),
        xaxis_title="Año",
        yaxis_title="Producción Total (kg)",
        xaxis=dict(tickmode="linear", dtick=1),
        showlegend=False,
    )
    return _style_axes(fig)


# ──────────────────────────────────────────────────────────
# Gráfico 3: Scatter - Humedad vs Rendimiento
# ──────────────────────────────────────────────────────────

def chart_humedad_vs_rendimiento(
    df: pd.DataFrame,
    correlacion: float = 0.0,
) -> go.Figure:
    """
    Scatter plot de correlación entre humedad del suelo (%) y
    rendimiento (kg/ha), con línea de tendencia y coloreado por cultivo.

    Args:
        df: DataFrame con columnas [cultivo, humedad, rendimiento_kg_ha, finca, calidad]
        correlacion: coeficiente de Pearson pre-calculado
    """
    if df.empty:
        return _empty_figure("Sin datos de correlación ambiental")

    fig = px.scatter(
        df,
        x="humedad",
        y="rendimiento_kg_ha",
        color="cultivo",
        color_discrete_sequence=QUALITATIVE_PALETTE,
        symbol="calidad",
        size_max=14,
        trendline="ols",
        trendline_color_override=PALETTE["accent"],
        custom_data=["finca", "calidad"],
    )

    fig.update_traces(
        marker=dict(size=10, opacity=0.82, line=dict(width=1, color=PALETTE["surface"])),
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Humedad: %{x:.1f}%<br>"
            "Rendimiento: %{y:,.0f} kg/ha<br>"
            "Finca: %{customdata[0]}<br>"
            "Calidad: %{customdata[1]}"
            "<extra></extra>"
        ),
        selector=dict(mode="markers"),
    )

    # Anotación de correlación
    signo = "+" if correlacion >= 0 else ""
    color_corr = PALETTE["success"] if abs(correlacion) > 0.5 else PALETTE["warning"]
    fig.add_annotation(
        x=0.02, y=0.97,
        xref="paper", yref="paper",
        text=f"ρ Pearson: {signo}{correlacion:.3f}",
        showarrow=False,
        bgcolor=f"{color_corr}22",
        bordercolor=color_corr,
        borderwidth=1,
        borderpad=6,
        font=dict(color=color_corr, size=12),
    )

    fig.update_layout(
        **_base_layout("💧 Correlación: Humedad del Suelo vs Rendimiento"),
        xaxis_title="Humedad del Suelo (%)",
        yaxis_title="Rendimiento (kg/ha)",
        legend_title_text="Cultivo",
    )
    return _style_axes(fig)


# ──────────────────────────────────────────────────────────
# Gráfico 4: Distribución de calidad (donut)
# ──────────────────────────────────────────────────────────

def chart_distribucion_calidad(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de donut que muestra la distribución porcentual de
    calidad de cosecha agregada.

    Args:
        df: DataFrame con columnas [cultivo, calidad, cantidad]
    """
    if df.empty:
        return _empty_figure("Sin datos de distribución de calidad")

    # Agregar por calidad (sin distinción de cultivo para el donut global)
    agg = df.groupby("calidad", as_index=False)["cantidad"].sum()

    fig = go.Figure(go.Pie(
        labels=agg["calidad"],
        values=agg["cantidad"],
        hole=0.55,
        marker=dict(
            colors=QUALITATIVE_PALETTE[: len(agg)],
            line=dict(color=PALETTE["surface"], width=2),
        ),
        hovertemplate="<b>%{label}</b><br>Cosechas: %{value:,}<br>%{percent}<extra></extra>",
        textfont=dict(color=PALETTE["text"], size=12),
        textinfo="label+percent",
    ))

    fig.add_annotation(
        text="Calidad<br>Cosecha",
        x=0.5, y=0.5,
        font=dict(size=13, color=PALETTE["text_muted"]),
        showarrow=False,
    )

    fig.update_layout(
        **_base_layout("🏅 Distribución de Calidad de Cosecha"),
        showlegend=True,
    )
    return fig


# ──────────────────────────────────────────────────────────
# Gráfico 5: Heatmap calidad por cultivo (stacked bar)
# ──────────────────────────────────────────────────────────

def chart_calidad_por_cultivo(df: pd.DataFrame) -> go.Figure:
    """
    Barras apiladas normalizadas (100%) que comparan la distribución
    de calidad dentro de cada tipo de cultivo.

    Args:
        df: DataFrame con columnas [cultivo, calidad, cantidad]
    """
    if df.empty:
        return _empty_figure("Sin datos de calidad por cultivo")

    pivot = df.pivot_table(
        index="cultivo", columns="calidad", values="cantidad", aggfunc="sum", fill_value=0
    )
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig = go.Figure()
    for i, calidad in enumerate(pivot_pct.columns):
        fig.add_trace(go.Bar(
            name=str(calidad),
            x=pivot_pct.index.tolist(),
            y=pivot_pct[calidad].round(1).tolist(),
            marker_color=QUALITATIVE_PALETTE[i % len(QUALITATIVE_PALETTE)],
            hovertemplate=f"<b>%{{x}}</b><br>{calidad}: %{{y:.1f}}%<extra></extra>",
        ))

    fig.update_layout(
        **_base_layout("📊 Calidad por Cultivo (%)"),
        barmode="stack",
        xaxis_title="Cultivo",
        yaxis_title="Porcentaje (%)",
        yaxis=dict(range=[0, 100], ticksuffix="%"),
    )
    return _style_axes(fig, xgrid=False)


# ──────────────────────────────────────────────────────────
# Gráfico 6: Insumos por cultivo (barras agrupadas)
# ──────────────────────────────────────────────────────────

def chart_insumos_por_categoria(df: pd.DataFrame) -> go.Figure:
    """
    Barras agrupadas que muestran el total de insumos aplicados
    por categoría (Fertilizante, Pesticida, Semilla) en cada cultivo.

    Args:
        df: DataFrame con columnas [cultivo, categoria_insumo, total_aplicado]
    """
    if df.empty:
        return _empty_figure("Sin datos de insumos agrícolas")

    pivot = df.pivot_table(
        index="cultivo",
        columns="categoria_insumo",
        values="total_aplicado",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    fig = go.Figure()
    categorias = [c for c in pivot.columns if c != "cultivo"]

    for i, cat in enumerate(categorias):
        fig.add_trace(go.Bar(
            name=str(cat),
            x=pivot["cultivo"].tolist(),
            y=pivot[cat].round(2).tolist(),
            marker_color=QUALITATIVE_PALETTE[i % len(QUALITATIVE_PALETTE)],
            hovertemplate=f"<b>%{{x}}</b><br>{cat}: %{{y:,.2f}}<extra></extra>",
        ))

    fig.update_layout(
        **_base_layout("🧪 Insumos Aplicados por Cultivo y Categoría"),
        barmode="group",
        xaxis_title="Cultivo",
        yaxis_title="Total Aplicado",
        legend_title_text="Categoría",
    )
    return _style_axes(fig, xgrid=False)


# ──────────────────────────────────────────────────────────
# Helper: figura de estado vacío
# ──────────────────────────────────────────────────────────

def _empty_figure(message: str) -> go.Figure:
    """
    Retorna una figura Plotly estilizada para estados vacíos.
    Muestra un mensaje amigable centrado en el área del gráfico.
    """
    fig = go.Figure()
    fig.add_annotation(
        x=0.5, y=0.5,
        xref="paper", yref="paper",
        text=f"<b>🌿 {message}</b>",
        showarrow=False,
        font=dict(size=14, color=PALETTE["text_muted"]),
        bgcolor=f"{PALETTE['surface2']}88",
        bordercolor=PALETTE["slate"],
        borderwidth=1,
        borderpad=14,
    )
    fig.update_layout(
        paper_bgcolor=PALETTE["surface"],
        plot_bgcolor=PALETTE["surface2"],
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=320,
    )
    return fig
