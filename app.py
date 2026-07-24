import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title="Gestión NPS · Claro",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ESTILOS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Work+Sans:wght@300;400;500;600&family=Barlow+Condensed:wght@600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Work Sans', sans-serif;
}

/* fondo general */
.stApp { background-color: #07070F; }
section[data-testid="stSidebar"] { background-color: #0C0C18; border-right: 1px solid #1C1C2C; }

/* ocultar elementos de Streamlit */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 1rem 1rem 1rem !important; }

/* header */
.nps-header {
    background: #0A0A16;
    border-bottom: 3px solid #C8102E;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    margin: 0 -1rem 1.2rem -1rem;
}
.logo-box {
    background: #C8102E;
    padding: 6px 16px;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: white;
    letter-spacing: 1px;
}
.header-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: white;
    letter-spacing: 1px;
}
.header-sub {
    font-size: 11px;
    color: #6A6A85;
    margin-top: 2px;
}

/* KPI cards */
.kpi-grid { display: flex; gap: 8px; margin-bottom: 14px; }
.kpi-card {
    flex: 1;
    background: #0D0D1A;
    border: 1px solid #1C1C2C;
    border-top: 3px solid;
    border-left: 3px solid;
    padding: 12px 14px 10px;
    position: relative;
}
.kpi-value {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 38px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 4px;
}
.kpi-label {
    font-size: 10px;
    color: #6A6A85;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.kpi-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    position: absolute;
    bottom: 8px; right: 8px;
}

/* panel cards */
.panel {
    background: #0D0D1A;
    border: 1px solid #1C1C2C;
    border-top: 3px solid #C8102E;
    border-left: 3px solid #C8102E;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.panel-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: white;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.panel-sub {
    font-size: 10px;
    color: #353545;
    margin-bottom: 10px;
}

/* sidebar labels */
.sidebar-section {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #C8102E;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 8px 0 4px;
    border-bottom: 1px solid #1C1C2C;
    margin-bottom: 8px;
}

/* tabla de detalle */
.detail-table { width: 100%; font-size: 11px; border-collapse: collapse; }
.detail-table th {
    background: #111120; color: #6A6A85;
    padding: 6px 10px; text-align: left;
    font-weight: 500; font-size: 10px;
    text-transform: uppercase; letter-spacing: 0.06em;
    border-bottom: 1px solid #1C1C2C;
}
.detail-table td {
    padding: 7px 10px; color: #C8C8D8;
    border-bottom: 1px solid #111120;
    font-size: 11px; line-height: 1.4;
}
.detail-table tr:hover td { background: #111120; }
.badge {
    display: inline-block; border-radius: 3px;
    padding: 2px 7px; font-size: 10px; font-weight: 500;
}
.badge-green  { background: #021312; color: #0F9B8E; }
.badge-red    { background: #180508; color: #C83050; }
.badge-amber  { background: #180F03; color: #BA7517; }
.badge-blue   { background: #0C1420; color: #378ADD; }
.badge-purple { background: #0C0A1C; color: #7F77DD; }
.badge-gray   { background: #111120; color: #6A6A85; }

/* footer */
.nps-footer {
    background: #090914;
    border-top: 2px solid #C8102E;
    padding: 8px 20px;
    font-size: 9px;
    color: #2E2E40;
    display: flex;
    justify-content: space-between;
    margin: 1rem -1rem 0;
}
</style>
""", unsafe_allow_html=True)


# ── CARGA DE DATOS ────────────────────────────────────────────────────────────
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/10Gkvo98fO-aLa5FKLdDNR9Iv0OLm3r6POejykHdkGkM/export?format=csv&gid=1940977728"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(GOOGLE_SHEET_URL)

    # ── Renombrar ANTES de hacer strip para evitar colisiones ────────────────
    # Col 0 sin cabecera = Fecha de gestión NPS
    # Col 2 sin cabecera = Asignación (Atendida / Gestión)
    # Col 1 con encoding roto ("Asignaci?n ") = Soporte/Agente NPS
    rename_map = {}
    for col in df.columns:
        stripped = col.strip()
        if stripped == "Unnamed: 0":
            rename_map[col] = "Fecha"
        elif stripped == "Unnamed: 2":
            rename_map[col] = "Asignación"
        elif stripped.startswith("Asignaci"):
            rename_map[col] = "Soporte"
    if rename_map:
        df = df.rename(columns=rename_map)

    # Strip espacios en el resto de columnas
    df.columns = [c.strip() if c not in ["Fecha", "Asignación", "Soporte"] else c
                  for c in df.columns]

    # Fallbacks si la hoja no tiene las columnas sin nombre
    if "Fecha" not in df.columns and "Fecha_Actividad" in df.columns:
        df = df.rename(columns={"Fecha_Actividad": "Fecha"})
    if "Soporte" not in df.columns and "Tecnico" in df.columns:
        df = df.rename(columns={"Tecnico": "Soporte"})

    # Limpiar espacios en valores de texto
    for col in ["Contactado", "Asignación", "Soporte", "Tipo_Red", "Zona"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Parsear fecha (formato DD/MM/YYYY desde Google Sheets)
    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")
    df["Dia"] = df["Fecha"].dt.day
    return df

df_raw = load_data()


# ── SIDEBAR FILTROS ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-section">Filtros</div>', unsafe_allow_html=True)

    meses = ["Todos"] + sorted(df_raw["Mes_Actual"].dropna().unique().tolist())
    mes = st.selectbox("Mes", meses, index=meses.index("May") if "May" in meses else 0)

    soportes = ["Todos"] + sorted(df_raw["Soporte"].dropna().unique().tolist())
    soporte = st.selectbox("Soporte / Agente", soportes)

    semanas_disp = sorted(df_raw["Semana_Actual"].dropna().unique().tolist())
    semanas_sel = st.multiselect(
        "Semanas", semanas_disp,
        default=[s for s in semanas_disp if s >= 18]
    )

    asignacion_opts = ["Todas"] + df_raw["Asignación"].dropna().unique().tolist()
    asignacion = st.selectbox("Asignación", asignacion_opts)

    st.markdown('<div class="sidebar-section" style="margin-top:12px">Detalle</div>',
                unsafe_allow_html=True)
    tipo_red = st.multiselect(
        "Tipo de red",
        df_raw["Tipo_Red"].dropna().unique().tolist(),
        default=df_raw["Tipo_Red"].dropna().unique().tolist()
    )
    zonas = st.multiselect(
        "Zona",
        df_raw["Zona"].dropna().unique().tolist(),
        default=df_raw["Zona"].dropna().unique().tolist()
    )

    st.markdown("---")
    st.markdown(
        '<p style="font-size:10px;color:#353545;text-align:center">'
        'Los datos se actualizan automáticamente<br>al reemplazar el archivo Excel</p>',
        unsafe_allow_html=True
    )
    if st.button("🔄  Recargar datos"):
        st.cache_data.clear()
        st.rerun()


# ── APLICAR FILTROS ───────────────────────────────────────────────────────────
df = df_raw.copy()
if mes != "Todos":
    df = df[df["Mes_Actual"] == mes]
if soporte != "Todos":
    df = df[df["Soporte"] == soporte]
if semanas_sel:
    df = df[df["Semana_Actual"].isin(semanas_sel)]
if asignacion != "Todas":
    df = df[df["Asignación"] == asignacion]
if tipo_red:
    df = df[df["Tipo_Red"].isin(tipo_red)]
if zonas:
    df = df[df["Zona"].isin(zonas)]


# ── MÉTRICAS BASE ─────────────────────────────────────────────────────────────
total       = len(df)
contactados = len(df[df["Contactado"] == "Contactado"])
no_contact  = len(df[df["Contactado"] == "No Contactado"])
intento3    = len(df[df["Contactado"] == "Intento 3"])
pct_efect   = round(contactados / total * 100, 1) if total > 0 else 0


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="nps-header">
  <div class="logo-box">Claro</div>
  <div>
    <div class="header-title">GESTIÓN NPS</div>
    <div class="header-sub">PANEL DE CONTROL · MAYO 2026 · {total} casos filtrados</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card" style="border-color:#C8102E">
    <div class="kpi-value" style="color:#C8102E">{total}</div>
    <div class="kpi-label">Total asignados</div>
    <div class="kpi-dot" style="background:#C8102E"></div>
  </div>
  <div class="kpi-card" style="border-color:#0F9B8E">
    <div class="kpi-value" style="color:#0F9B8E">{contactados}</div>
    <div class="kpi-label">Contactados</div>
    <div class="kpi-dot" style="background:#0F9B8E"></div>
  </div>
  <div class="kpi-card" style="border-color:#C83050">
    <div class="kpi-value" style="color:#C83050">{no_contact}</div>
    <div class="kpi-label">No contactados</div>
    <div class="kpi-dot" style="background:#C83050"></div>
  </div>
  <div class="kpi-card" style="border-color:#7F77DD">
    <div class="kpi-value" style="color:#7F77DD">{pct_efect}%</div>
    <div class="kpi-label">% Efectividad</div>
    <div class="kpi-dot" style="background:#7F77DD"></div>
  </div>
  <div class="kpi-card" style="border-color:#BA7517">
    <div class="kpi-value" style="color:#BA7517">{intento3}</div>
    <div class="kpi-label">Intento 3 / Gestión</div>
    <div class="kpi-dot" style="background:#BA7517"></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── COLORES ───────────────────────────────────────────────────────────────────
COLORS = {
    "Contactado":    "#0F9B8E",
    "No Contactado": "#C83050",
    "Intento 3":     "#BA7517",
}
AREA_COLORS = {
    "Tecnico":               "#0F9B8E",
    "Cliente":               "#7F77DD",
    "Soporte Tecnico":       "#BA7517",
    "Comercial":             "#C83050",
    "Redes":                 "#378ADD",
    "No se Puede determinar":"#4A4A5A",
    "Sistema":               "#888780",
    "Tecnico / Comercial":   "#D85A30",
}
CHART_BG    = "#0D0D1A"
GRID_COLOR  = "#1C1C2C"
TEXT_COLOR  = "#8A8A9A"
FONT_FAMILY = "Work Sans"

def chart_layout(fig, title="", height=260):
    fig.update_layout(
        title=dict(text=title, font=dict(size=12, color="white",
                   family="Barlow Condensed"), x=0, xref="paper") if title else None,
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY, size=11),
        margin=dict(l=8, r=8, t=30 if title else 8, b=8),
        height=height,
        legend=dict(
            bgcolor="#0D0D1A", bordercolor="#1C1C2C", borderwidth=1,
            font=dict(size=10), orientation="h",
            yanchor="bottom", y=-0.25, xanchor="left", x=0
        ),
        xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                   tickfont=dict(size=10)),
        yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
                   tickfont=dict(size=10)),
    )
    return fig


# ── FILA 1: semanal + árbol causas + diario ───────────────────────────────────
col1, col2, col3 = st.columns([1.1, 1.6, 1.3])

with col1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Registro semanal</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Semanas seleccionadas</div>', unsafe_allow_html=True)

    if not df.empty and semanas_sel:
        pivot = df.groupby(["Semana_Actual","Contactado"]).size().unstack(fill_value=0)
        for c in ["Contactado","No Contactado","Intento 3"]:
            if c not in pivot.columns:
                pivot[c] = 0
        pivot["Total"] = pivot.sum(axis=1)
        pivot = pivot.reset_index().sort_values("Semana_Actual")

        fig_sem = go.Figure()
        for cat in ["Contactado","No Contactado","Intento 3"]:
            if cat in pivot.columns:
                fig_sem.add_trace(go.Bar(
                    name=cat, x=pivot["Semana_Actual"].astype(str),
                    y=pivot[cat], marker_color=COLORS.get(cat,"#888"),
                    text=pivot[cat], textposition="inside",
                    textfont=dict(size=10, color="white")
                ))
        fig_sem.update_layout(barmode="stack")
        chart_layout(fig_sem, height=250)
        fig_sem.update_xaxes(title_text="Semana")
        st.plotly_chart(fig_sem, use_container_width=True, config={"displayModeBar": False})

        # tabla resumen
        table_df = pivot[["Semana_Actual","Contactado","No Contactado","Intento 3","Total"]].copy()
        table_df.columns = ["Sem","Contact.","No Cont.","Int.3","Total"]
        st.dataframe(
            table_df.set_index("Sem"),
            use_container_width=True,
            height=120
        )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Árbol de causas — contactados</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Distribución por área y etapas</div>', unsafe_allow_html=True)

    df_cont = df[df["Contactado"] == "Contactado"].copy()

    tab1, tab2 = st.tabs(["Por área", "Por etapa 1→2→3"])

    with tab1:
        if not df_cont.empty and "Area" in df_cont.columns:
            area_counts = (
                df_cont["Area"].fillna("Sin área")
                .value_counts().reset_index()
            )
            area_counts.columns = ["Area","Casos"]
            area_counts["Pct"] = (area_counts["Casos"]/area_counts["Casos"].sum()*100).round(1)
            area_counts["Color"] = area_counts["Area"].map(AREA_COLORS).fillna("#888")

            fig_area = go.Figure(go.Bar(
                x=area_counts["Casos"],
                y=area_counts["Area"],
                orientation="h",
                marker_color=area_counts["Color"].tolist(),
                text=area_counts.apply(lambda r: f"{r['Casos']}  {r['Pct']}%", axis=1),
                textposition="outside",
                textfont=dict(size=10, color=TEXT_COLOR),
            ))
            chart_layout(fig_area, height=270)
            fig_area.update_yaxes(autorange="reversed")
            fig_area.update_layout(showlegend=False, margin=dict(l=8,r=80,t=8,b=8))
            st.plotly_chart(fig_area, use_container_width=True,
                            config={"displayModeBar": False})

    with tab2:
        if not df_cont.empty and "Etapa1" in df_cont.columns:
            etapa_data = (
                df_cont.groupby(["Etapa1","Etapa2","Etapa3"])
                .size().reset_index(name="Casos")
                .dropna(subset=["Etapa1"])
                .sort_values("Casos", ascending=False)
                .head(20)
            )
            if not etapa_data.empty:
                fig_sun = px.sunburst(
                    etapa_data,
                    path=["Etapa1","Etapa2","Etapa3"],
                    values="Casos",
                    color="Etapa1",
                    color_discrete_sequence=px.colors.qualitative.Dark24,
                )
                fig_sun.update_traces(textfont_size=10)
                fig_sun.update_layout(
                    paper_bgcolor=CHART_BG,
                    plot_bgcolor=CHART_BG,
                    font=dict(color=TEXT_COLOR),
                    margin=dict(l=0,r=0,t=0,b=0),
                    height=280,
                )
                st.plotly_chart(fig_sun, use_container_width=True,
                                config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">% Contactado por día</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Atendidas · tendencia diaria</div>', unsafe_allow_html=True)

    df_atend = df[df["Asignación"] == "Atendida"].copy()
    if not df_atend.empty and "Dia" in df_atend.columns:
        dia_g = df_atend.groupby(["Dia","Contactado"]).size().unstack(fill_value=0)
        for c in ["Contactado","No Contactado"]:
            if c not in dia_g.columns: dia_g[c] = 0
        dia_g["Total"] = dia_g["Contactado"] + dia_g["No Contactado"]
        dia_g["Pct_C"]  = (dia_g["Contactado"]    / dia_g["Total"] * 100).round(1)
        dia_g["Pct_NC"] = (dia_g["No Contactado"]  / dia_g["Total"] * 100).round(1)
        dia_g = dia_g.reset_index().sort_values("Dia")

        fig_dia = go.Figure()
        fig_dia.add_trace(go.Scatter(
            x=dia_g["Dia"], y=dia_g["Pct_C"],
            name="% Contactado", mode="lines+markers",
            line=dict(color="#0F9B8E", width=2),
            marker=dict(size=6, color="#0F9B8E"),
            fill="tozeroy", fillcolor="rgba(15,155,142,0.08)",
        ))
        fig_dia.add_trace(go.Scatter(
            x=dia_g["Dia"], y=dia_g["Pct_NC"],
            name="% No contactado", mode="lines+markers",
            line=dict(color="#C83050", width=2, dash="dot"),
            marker=dict(size=5, color="#C83050"),
        ))
        fig_dia.add_hline(y=50, line_dash="dash",
                          line_color="#353545", line_width=1,
                          annotation_text="50%",
                          annotation_font=dict(color="#353545", size=9))
        chart_layout(fig_dia, height=270)
        fig_dia.update_xaxes(title_text="Día del mes", dtick=1)
        fig_dia.update_yaxes(title_text="%", range=[0,105])
        st.plotly_chart(fig_dia, use_container_width=True,
                        config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ── FILA 2: agentes + cumplimiento + detalle registros ────────────────────────
col4, col5, col6 = st.columns([1.1, 1.3, 1.6])

with col4:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Efectividad por agente</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">% contactado sobre asignados</div>', unsafe_allow_html=True)

    if not df.empty:
        ag = df.groupby("Soporte").apply(
            lambda x: pd.Series({
                "Total":       len(x),
                "Contactados": (x["Contactado"]=="Contactado").sum(),
                "Pct":         round((x["Contactado"]=="Contactado").sum()/len(x)*100, 1)
            })
        ).reset_index().sort_values("Pct", ascending=True)

        fig_ag = go.Figure()
        for _, row in ag.iterrows():
            col_bar = "#0F9B8E" if row["Pct"] >= 50 else "#C83050"
            fig_ag.add_trace(go.Bar(
                x=[row["Pct"]],
                y=[row["Soporte"]],
                orientation="h",
                marker_color=col_bar,
                text=f"{row['Pct']}%  ({int(row['Contactados'])}/{int(row['Total'])})",
                textposition="outside",
                textfont=dict(size=10, color=TEXT_COLOR),
                showlegend=False,
            ))
        fig_ag.add_vline(x=50, line_dash="dash",
                         line_color="#353545", line_width=1,
                         annotation_text="meta 50%",
                         annotation_font=dict(color="#353545", size=9),
                         annotation_position="top")
        chart_layout(fig_ag, height=200)
        fig_ag.update_xaxes(range=[0,115], title_text="%")
        fig_ag.update_layout(margin=dict(l=8,r=80,t=8,b=8))
        st.plotly_chart(fig_ag, use_container_width=True,
                        config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col5:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Cumplimiento de visita</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Resultado del agendamiento técnico</div>', unsafe_allow_html=True)

    df_cumpl = df[df["cumplimiento_fecha_inicial_agendamiento"].notna()].copy()
    if not df_cumpl.empty:
        cumpl_map = {
            "Sí se cumplió, el Técnico llego el día y la hora acordadas":
                "Cumplió · día y hora",
            "Sí se cumplió, llego el día acordado pero en un horario diferente":
                "Cumplió · horario diferente",
            "No se cumplió, se tuvo que reagendar":
                "No cumplió · reagendado",
            "No se cumplió y no se ha reagendado":
                "No cumplió · sin reagendar",
        }
        df_cumpl["Resultado"] = df_cumpl[
            "cumplimiento_fecha_inicial_agendamiento"
        ].map(cumpl_map).fillna("Otro")

        cumpl_g = df_cumpl["Resultado"].value_counts().reset_index()
        cumpl_g.columns = ["Resultado","Casos"]

        CUMPL_COLORS = {
            "Cumplió · día y hora":        "#0F9B8E",
            "Cumplió · horario diferente": "#BA7517",
            "No cumplió · reagendado":     "#C83050",
            "No cumplió · sin reagendar":  "#7F3040",
        }
        fig_cumpl = go.Figure(go.Pie(
            labels=cumpl_g["Resultado"],
            values=cumpl_g["Casos"],
            hole=0.55,
            marker_colors=[CUMPL_COLORS.get(r,"#888") for r in cumpl_g["Resultado"]],
            textfont=dict(size=10),
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>%{value} casos · %{percent}<extra></extra>",
        ))
        fig_cumpl.add_annotation(
            text=f"<b>{len(df_cumpl)}</b><br><span style='font-size:9px'>casos</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="white", family="Barlow Condensed"),
        )
        fig_cumpl.update_layout(
            paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(l=0,r=0,t=0,b=0), height=200,
            legend=dict(
                bgcolor=CHART_BG, bordercolor="#1C1C2C", borderwidth=1,
                font=dict(size=9), orientation="v",
                x=1.0, y=0.5,
            ),
            showlegend=True,
        )
        st.plotly_chart(fig_cumpl, use_container_width=True,
                        config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Asignación por semana · detalle</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Asignación Diaria · Recuento de actividades</div>',
                unsafe_allow_html=True)

    if not df.empty:
        asig_sem = (
            df.groupby(["Semana_Actual","Asignación"])
            .size().unstack(fill_value=0).reset_index()
        )
        fig_asig = go.Figure()
        for col_name in [c for c in ["Atendida","Gestión"] if c in asig_sem.columns]:
            fig_asig.add_trace(go.Bar(
                x=asig_sem["Semana_Actual"].astype(str),
                y=asig_sem[col_name],
                name=col_name,
                marker_color="#0F9B8E" if col_name=="Atendida" else "#BA7517",
                text=asig_sem[col_name],
                textposition="inside",
                textfont=dict(size=10, color="white"),
            ))
        chart_layout(fig_asig, height=200)
        fig_asig.update_layout(barmode="group")
        fig_asig.update_xaxes(title_text="Semana")
        st.plotly_chart(fig_asig, use_container_width=True,
                        config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ── TABLA DETALLE COMPLETO ────────────────────────────────────────────────────
st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-title">Detalle de registros</div>', unsafe_allow_html=True)
st.markdown('<div class="panel-sub">Todos los casos según filtros aplicados — click en columna para ordenar</div>',
            unsafe_allow_html=True)

BADGE_MAP = {
    "Contactado":    "badge-green",
    "No Contactado": "badge-red",
    "Intento 3":     "badge-amber",
    "Atendida":      "badge-blue",
    "Gestión":       "badge-amber",
}

cols_show = [
    "Fecha","Soporte","Asignación","Contactado","nombre_cliente",
    "Zona","Tipo_Red","Area","Etapa1","Semana_Actual",
    "Observacion contacto telefonico cliente."
]
cols_show = [c for c in cols_show if c in df.columns]

df_show = df[cols_show].copy()
df_show["Fecha"] = df_show["Fecha"].dt.strftime("%d/%m/%Y")
df_show["Observacion contacto telefonico cliente."] = (
    df_show["Observacion contacto telefonico cliente."]
    .fillna("").astype(str).str[:80] + "..."
)
df_show = df_show.fillna("—")
df_show.columns = [
    c.replace("Observacion contacto telefonico cliente.", "Observación")
     .replace("nombre_cliente", "Cliente")
     .replace("Semana_Actual", "Sem.")
    for c in df_show.columns
]

st.dataframe(
    df_show,
    use_container_width=True,
    height=280,
    column_config={
        "Fecha":      st.column_config.TextColumn("Fecha", width=80),
        "Soporte":    st.column_config.TextColumn("Soporte", width=110),
        "Asignación": st.column_config.TextColumn("Asig.", width=70),
        "Contactado": st.column_config.TextColumn("Estado", width=100),
        "Cliente":    st.column_config.TextColumn("Cliente", width=160),
        "Zona":       st.column_config.TextColumn("Zona", width=90),
        "Tipo_Red":   st.column_config.TextColumn("Red", width=55),
        "Area":       st.column_config.TextColumn("Área", width=110),
        "Etapa1":     st.column_config.TextColumn("Etapa 1", width=130),
        "Sem.":       st.column_config.NumberColumn("Sem.", width=45),
        "Observación":st.column_config.TextColumn("Observación", width=240),
    },
    hide_index=True,
)

descarga = df[cols_show].copy()
descarga["Fecha"] = descarga["Fecha"].dt.strftime("%d/%m/%Y")
csv = descarga.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇  Exportar CSV filtrado",
    csv,
    "nps_filtrado.csv",
    "text/csv",
)
st.markdown('</div>', unsafe_allow_html=True)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nps-footer">
  <span>Fuente: BBDD-NPS · Gestión NPS Mayo 2026 · Datos actualizados automáticamente</span>
  <span>Claro Colombia · Panel de Control</span>
</div>
""", unsafe_allow_html=True)
