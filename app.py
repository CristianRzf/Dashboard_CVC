import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Dashboard Estratégico CVC", layout="wide", page_icon="")

st.title("Dashboard Estratégico de TI – CVC")
st.caption("Corporación Autónoma Regional del Valle del Cauca | 2026-2029")

# ── Carga de datos ────────────────────────────────────────────
@st.cache_data
def cargar(ruta, nombre):
    if not os.path.exists(ruta):
        st.warning(f"No se encontró: {ruta}")
        return None
    try:
        return pd.read_excel(ruta)
    except Exception as e:
        st.warning(f"Error al cargar {nombre}: {e}")
        return None

kpis      = cargar("datos/kpis_bsc.xlsx",       "KPIs")
proyectos = cargar("datos/proyectos_peti.xlsx",  "Proyectos")
calor     = cargar("datos/matriz_calor.xlsx",    "Mapa de Calor")
madurez   = cargar("datos/madurez_digital.xlsx", "Madurez Digital")

if kpis is None or proyectos is None:
    st.error("Faltan archivos esenciales (KPIs o Proyectos).")
    st.stop()

# ── Conversión de tipos ───────────────────────────────────────
COLS_NUM = ["Año", "Valor", "Target", "Puntaje", "Puntuación", "Presupuesto"]
for df in [kpis, proyectos, madurez, calor]:
    if df is not None:
        for col in df.columns:
            if any(k in col for k in COLS_NUM):
                df[col] = pd.to_numeric(df[col], errors="coerce")

# ── Helper: caja de análisis ──────────────────────────────────
def caja_analisis(texto):
    st.markdown(
        f"""
        <div style="background:#1e3a5f;border-left:4px solid #3498db;
                    border-radius:6px;padding:16px 20px;margin-top:8px;margin-bottom:24px">
            <span style="color:#aed6f1;font-size:13px;font-weight:600"> ANÁLISIS</span>
            <p style="color:#ecf0f1;font-size:14px;margin-top:8px;margin-bottom:0;line-height:1.7">{texto}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Clasificación de KPIs por unidad ─────────────────────────
KPIS_PORCENTAJE = {
    "Ejecucion eficiente presupuesto TI",
    "Gobierno del dato y analitica avanzada",
    "Competencias digitales del personal CVC",
    "Satisfaccion usuarios internos TI",
    "Gobierno de TI formal alineado al MRAE",
    "Portafolio PETI",
    "mision",
    "Seguridad digital - SGSI ISO 27001",
}
KPIS_HORAS   = {"Reduccion tiempo resolucion incidentes"}
KPIS_PUNTAJE = {"Modernizacion arquitectura - ERP nube"}
# El resto (vision, fuentes financiacion, sostenimiento) son conteos (#)

def fmt_valor(kpi, valor):
    if pd.isna(valor):
        return "—"
    if kpi in KPIS_PORCENTAJE:
        return f"{valor:.0f} %"
    if kpi in KPIS_HORAS:
        return f"{valor:.0f} h"
    if kpi in KPIS_PUNTAJE:
        return f"{valor:.0f} pts"
    return f"{valor:.0f}"

def cumple_meta(kpi, valor, target):
    if pd.isna(valor) or pd.isna(target):
        return False
    if kpi in KPIS_HORAS:
        return valor <= target   # menor = mejor
    return valor >= target

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.header("Filtros")
años = sorted(kpis["Año"].dropna().unique())
año_sel = st.sidebar.selectbox("Año", años)

oeti_opts = ["Todos"] + sorted(proyectos["OETI"].dropna().unique())
oeti_sel  = st.sidebar.selectbox("OETI", oeti_opts)
proy_fil  = proyectos if oeti_sel == "Todos"else proyectos[proyectos["OETI"] == oeti_sel]

st.sidebar.markdown("---")
st.sidebar.subheader("Riesgos")
st.sidebar.markdown("- JD Edwards sin soporte\n- Sin BCP/DRP\n- MSPI nivel inicial")
st.sidebar.subheader("Recomendaciones")
st.sidebar.markdown("1. Migrar JD Edwards\n2. DRP en nube\n3. Ciberseguridad\n4. Capacitación\n5. Priorizar P-05, P-09, P-10")

# ── Filtro del año ────────────────────────────────────────────
kpis_año = kpis[kpis["Año"] == año_sel].copy()

# ════════════════════════════════════════════════════════════════
#  SECCIÓN BSC
# ════════════════════════════════════════════════════════════════

# ── Métricas rápidas ──────────────────────────────────────────
def get_kv(nombre):
    row = kpis_año[kpis_año["KPI"] == nombre]
    if row.empty:
        return None, None
    return row["Valor"].values[0], row["Target"].values[0]

v_ejec, t_ejec   = get_kv("Ejecucion eficiente presupuesto TI")
v_sat,  t_sat    = get_kv("Satisfaccion usuarios internos TI")
v_inc,  t_inc    = get_kv("Reduccion tiempo resolucion incidentes")
v_gov,  t_gov    = get_kv("Gobierno de TI formal alineado al MRAE")
v_seg,  t_seg    = get_kv("Seguridad digital - SGSI ISO 27001")
v_comp, t_comp   = get_kv("Competencias digitales del personal CVC")

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.metric("Ejec. Presupuesto",
              f"{v_ejec:.0f} %"if v_ejec is not None else "—",
              f"Meta {t_ejec:.0f} %"if t_ejec is not None else "")
with c2:
    st.metric("Satisfacción usuarios",
              f"{v_sat:.0f} %"if v_sat is not None else "—",
              f"Meta {t_sat:.0f} %"if t_sat is not None else "")
with c3:
    st.metric("⏱ Resolución incidentes",
              f"{v_inc:.0f} h"if v_inc is not None else "—",
              f"Meta {t_inc:.0f} h"if t_inc is not None else "",
              delta_color="inverse")
with c4:
    st.metric("Gobierno TI",
              f"{v_gov:.0f} %"if v_gov is not None else "—",
              f"Meta {t_gov:.0f} %"if t_gov is not None else "")
with c5:
    st.metric("Seguridad SGSI",
              f"{v_seg:.0f} %"if v_seg is not None else "—",
              f"Meta {t_seg:.0f} %"if t_seg is not None else "")
with c6:
    st.metric("Competencias digitales",
              f"{v_comp:.0f} %"if v_comp is not None else "—",
              f"Meta {t_comp:.0f} %"if t_comp is not None else "")

# ── Preparar datos de visualización BSC ──────────────────────
kpis_viz = kpis_año.copy()
kpis_viz["Cumple"]    = kpis_viz.apply(lambda r: cumple_meta(r["KPI"], r["Valor"], r["Target"]), axis=1)
kpis_viz["Semaforo"]  = kpis_viz["Cumple"].apply(lambda c: ""if c else "")
kpis_viz["ValorFmt"]  = kpis_viz.apply(lambda r: fmt_valor(r["KPI"], r["Valor"]),  axis=1)
kpis_viz["TargetFmt"] = kpis_viz.apply(lambda r: fmt_valor(r["KPI"], r["Target"]), axis=1)

# % alcanzado vs meta (normalizado; horas invertidas)
kpis_viz["pct_vs_meta"] = kpis_viz.apply(
    lambda r: (r["Target"] / r["Valor"] * 100)
              if (r["KPI"] in KPIS_HORAS and r["Valor"] > 0)
              else ((r["Valor"] / r["Target"] * 100) if r["Target"] and r["Target"] != 0 else 0),
    axis=1
).clip(upper=150)

ORDEN_PERSPECTIVAS = [
    "Mision/Vision", "Objetivo estrategico", "Financiera",
    "Cliente", "Procesos Internos", "Aprendizaje y conocimiento",
]
COLORES_PERSPECTIVA = {
    "Financiera":                 "#2ecc71",
    "Cliente":                    "#3498db",
    "Procesos Internos":          "#e67e22",
    "Aprendizaje y conocimiento": "#9b59b6",
    "Objetivo estrategico":       "#e74c3c",
    "Mision/Vision":              "#1abc9c",
}

kpis_viz["Perspectiva"] = pd.Categorical(
    kpis_viz["Perspectiva"], categories=ORDEN_PERSPECTIVAS, ordered=True
)
kpis_viz = kpis_viz.sort_values("Perspectiva")

# ── Gráfico de barras BSC ─────────────────────────────────────
st.subheader("Balanced Scorecard")

fig_bsc = px.bar(
    kpis_viz,
    x="pct_vs_meta",
    y="KPI",
    color="Perspectiva",
    orientation="h",
    color_discrete_map=COLORES_PERSPECTIVA,
    text=kpis_viz.apply(
        lambda r: f"{r['ValorFmt']} / Meta: {r['TargetFmt']}  {r['Semaforo']}", axis=1
    ),
    labels={"pct_vs_meta": "% alcanzado vs meta", "KPI": ""},
    height=560,
    title=f"Desempeño BSC — {int(año_sel)}",
)
fig_bsc.add_vline(x=100, line_dash="dash", line_color="white",
                  annotation_text="Meta 100 %", annotation_font_color="white")
fig_bsc.update_traces(textposition="outside", cliponaxis=False)
fig_bsc.update_layout(
    plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
    font_color="white", legend_title_text="Perspectiva",
    xaxis=dict(range=[0, 165], gridcolor="#1e3a5f"),
    yaxis=dict(autorange="reversed"),
    margin=dict(l=10, r=30, t=50, b=30),
)
st.plotly_chart(fig_bsc, use_container_width=True)

# ── Análisis BSC ──────────────────────────────────────────────
kpis_validos = kpis_viz.dropna(subset=["Valor", "Target"])
if not kpis_validos.empty:
    total_kpis = len(kpis_validos)
    kpis_ok    = kpis_validos["Cumple"].sum()
    kpis_nok   = total_kpis - kpis_ok
    pct_cumpl  = kpis_ok / total_kpis * 100

    rezagados = kpis_validos[~kpis_validos["Cumple"]].sort_values("pct_vs_meta")
    peor_kpi  = rezagados.iloc[0] if not rezagados.empty else None

    persp_nok = (
        kpis_validos[~kpis_validos["Cumple"]]
        .groupby("Perspectiva", observed=True).size().idxmax()
        if kpis_nok > 0 else "ninguna"
    )

    txt_peor = (
        f"El KPI más rezagado es <b>{peor_kpi['KPI']}</b> "
        f"({peor_kpi['ValorFmt']} vs meta {peor_kpi['TargetFmt']}, "
        f"alcanzando solo el <b>{peor_kpi['pct_vs_meta']:.0f}%</b> de su objetivo). "
        if peor_kpi is not None else ""
    )

    caja_analisis(
        f"Para el año <b>{int(año_sel)}</b>, el BSC registra <b>{int(kpis_ok)} de {total_kpis}</b> "
        f"indicadores en cumplimiento (<b>{pct_cumpl:.0f}%</b> de logro global). "
        f"{txt_peor}"
        f"La perspectiva con mayor número de incumplimientos es <b>{persp_nok}</b>, "
        f"requiriendo revisión inmediata del plan de acción asociado. "
        f"Se recomienda priorizar los indicadores rezagados en el comité de seguimiento "
        f"del próximo trimestre."
    )

# ── Tabla semafórica ──────────────────────────────────────────
st.subheader("Estado por perspectiva")
tabla_display = kpis_viz[["Perspectiva", "KPI", "Unidad", "Semaforo", "ValorFmt", "TargetFmt"]].rename(columns={
    "Semaforo":  "Estado",
    "ValorFmt":  "Valor real",
    "TargetFmt": "Meta",
})
st.dataframe(
    tabla_display,
    use_container_width=True,
    hide_index=True,
    column_config={"Estado": st.column_config.TextColumn("Estado", width="small")},
)

# ── Evolución 2026–2029 ───────────────────────────────────────
st.subheader("Evolución 2026–2029 — KPIs clave")

KPIS_TENDENCIA = [
    "Satisfaccion usuarios internos TI",
    "Ejecucion eficiente presupuesto TI",
    "Gobierno del dato y analitica avanzada",
    "Competencias digitales del personal CVC",
    "Reduccion tiempo resolucion incidentes",
]
kpis_tend = kpis[kpis["KPI"].isin(KPIS_TENDENCIA)].copy()
tend_pct  = kpis_tend[~kpis_tend["KPI"].isin(KPIS_HORAS)]
tend_hrs  = kpis_tend[kpis_tend["KPI"].isin(KPIS_HORAS)]

tab1, tab2 = st.tabs(["Indicadores (%)", "Tiempo resolución (horas)"])

with tab1:
    fig_pct = px.line(
        tend_pct, x="Año", y="Valor", color="KPI", markers=True,
        labels={"Valor": "% alcanzado"},
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    for kpi_name, grp in tend_pct.groupby("KPI"):
        fig_pct.add_scatter(
            x=grp["Año"], y=grp["Target"], mode="lines",
            line=dict(dash="dot", width=1), showlegend=False,
            opacity=0.5, name=f"Meta {kpi_name}",
        )
    fig_pct.update_layout(
        plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
        font_color="white",
        xaxis=dict(dtick=1, gridcolor="#1e3a5f"),
        yaxis=dict(gridcolor="#1e3a5f"),
    )
    st.plotly_chart(fig_pct, use_container_width=True)

with tab2:
    if not tend_hrs.empty:
        fig_hrs = px.line(
            tend_hrs, x="Año", y="Valor", color="KPI", markers=True,
            labels={"Valor": "Horas"},
            color_discrete_sequence=["#e74c3c"],
        )
        fig_hrs.add_scatter(
            x=tend_hrs["Año"], y=tend_hrs["Target"], mode="lines",
            line=dict(dash="dot", color="#aaaaaa", width=1),
            name="Meta horas", showlegend=True,
        )
        fig_hrs.update_layout(
            plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
            font_color="white",
            xaxis=dict(dtick=1, gridcolor="#1e3a5f"),
            yaxis=dict(gridcolor="#1e3a5f", title="Horas (menor = mejor)"),
        )
        st.plotly_chart(fig_hrs, use_container_width=True)

if not kpis_tend.empty:
    resumen = []
    for kpi, grp in kpis_tend.groupby("KPI"):
        grp = grp.sort_values("Año")
        if len(grp) >= 2:
            inicio, fin = grp.iloc[0]["Valor"], grp.iloc[-1]["Valor"]
            if kpi in KPIS_HORAS:
                tend = "mejora (↓)"if fin < inicio else "deterioro (↑)"
                etiq = f"{inicio:.0f} h → {fin:.0f} h"
            else:
                tend = "creciente ↑"if fin > inicio else "decreciente ↓"
                etiq = f"{inicio:.0f}% → {fin:.0f}%"
            resumen.append(f"<b>{kpi}</b>: {tend} ({etiq})")
    caja_analisis(
        "Tendencias proyectadas 2026–2029: "
        + "&nbsp;|&nbsp; ".join(resumen)
        + ". Se recomienda monitorear trimestralmente los indicadores con tendencia "
          "decreciente o de deterioro, y ajustar los planes de acción antes del cierre "
          "de cada vigencia."
    )

# ── Radar BSC ─────────────────────────────────────────────────
st.subheader("Radar de cumplimiento BSC")

radar_data = (
    kpis_viz.groupby("Perspectiva", observed=True)["pct_vs_meta"]
    .mean()
    .reset_index()
    .rename(columns={"pct_vs_meta": "Cumplimiento_pct"})
)

fig_radar = go.Figure()
r_vals  = radar_data["Cumplimiento_pct"].tolist()
theta   = radar_data["Perspectiva"].tolist()
fig_radar.add_trace(go.Scatterpolar(
    r=r_vals + [r_vals[0]], theta=theta + [theta[0]],
    fill="toself", fillcolor="rgba(52,152,219,0.3)",
    line=dict(color="#3498db", width=2),
    name=f"Año {int(año_sel)}",
))
fig_radar.add_trace(go.Scatterpolar(
    r=[100] * (len(radar_data) + 1), theta=theta + [theta[0]],
    mode="lines", line=dict(color="white", dash="dot", width=1),
    name="Meta 100%",
))
fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 150], gridcolor="#1e3a5f",
                        tickfont=dict(color="white"), ticksuffix="%"),
        angularaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="white")),
        bgcolor="#0d1b2a",
    ),
    paper_bgcolor="#0d1b2a", font_color="white",
    legend=dict(orientation="h", yanchor="bottom", y=-0.15),
    height=480,
)
st.plotly_chart(fig_radar, use_container_width=True)

persp_lideres = radar_data.nlargest(2,  "Cumplimiento_pct")["Perspectiva"].tolist()
persp_rezag   = radar_data.nsmallest(2, "Cumplimiento_pct")["Perspectiva"].tolist()
caja_analisis(
    f"El radar BSC para <b>{int(año_sel)}</b> muestra que las perspectivas con mayor "
    f"cumplimiento son <b>{'</b> y <b>'.join(persp_lideres)}</b>. "
    f"Las perspectivas más alejadas de la meta son "
    f"<b>{'</b> y <b>'.join(persp_rezag)}</b>. "
    f"Una forma de radar equilibrada hacia el exterior indica madurez estratégica integral; "
    f"los vacíos actuales señalan las áreas de inversión prioritaria para el siguiente ciclo."
)

# ════════════════════════════════════════════════════════════════
#  SECCIÓN PORTAFOLIO PETI (sin cambios)
# ════════════════════════════════════════════════════════════════
st.subheader("Portafolio PETI")
proy_fil = proy_fil.copy()
# Inicio = 1 enero del año; Fin = 31 diciembre del año (garantiza barra visible aunque Inicio==Fin)
proy_fil["Inicio_dt"] = pd.to_datetime(proy_fil["Inicio"].astype(int).astype(str) + "-01-01")
proy_fil["Fin_dt"]    = pd.to_datetime(proy_fil["Fin"].astype(int).astype(str)    + "-12-31")
proy_fil["Label"]     = proy_fil["ID"] + "– "+ proy_fil["Nombre"].str.slice(0, 45)

COLORES_PRIORIDAD = {"Alta": "#e74c3c", "Media": "#e67e22", "Baja": "#3498db"}

fig_gantt = px.timeline(
    proy_fil,
    x_start="Inicio_dt", x_end="Fin_dt",
    y="Label", color="Prioridad",
    color_discrete_map=COLORES_PRIORIDAD,
    hover_data={"Presupuesto_MCOP": True, "OETI": True, "Estado": True, "Label": False},
    labels={"Label": ""},
    height=520,
)
fig_gantt.update_yaxes(autorange="reversed", tickfont=dict(size=12))
fig_gantt.update_xaxes(
    dtick="M12", tickformat="%Y",
    range=["2025-07-01", "2030-01-01"],
    gridcolor="#1e3a5f",
)
fig_gantt.update_layout(
    plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
    font_color="white", legend_title_text="Prioridad",
    margin=dict(l=10, r=20, t=20, b=20),
)
st.plotly_chart(fig_gantt, use_container_width=True)

with st.expander("Detalle proyectos"):
    st.dataframe(
        proy_fil[["ID", "Nombre", "OETI", "Presupuesto_MCOP", "Inicio", "Fin", "Prioridad", "Estado"]],
        use_container_width=True, hide_index=True,
    )

if not proy_fil.empty:
    total_proy  = len(proy_fil)
    alta        = len(proy_fil[proy_fil["Prioridad"].str.lower() == "alta"])  if "Prioridad"in proy_fil.columns else 0
    media       = len(proy_fil[proy_fil["Prioridad"].str.lower() == "media"]) if "Prioridad"in proy_fil.columns else 0
    baja        = len(proy_fil[proy_fil["Prioridad"].str.lower() == "baja"])  if "Prioridad"in proy_fil.columns else 0
    presupuesto = proy_fil["Presupuesto_MCOP"].sum() if "Presupuesto_MCOP"in proy_fil.columns else 0
    filtro_txt  = f"(filtrado por OETI: {oeti_sel})"if oeti_sel != "Todos"else ""
    caja_analisis(
        f"El portafolio{filtro_txt} contiene <b>{total_proy} proyectos</b>: "
        f"<b>{alta} de alta</b>, <b>{media} de media</b> y <b>{baja} de baja</b> prioridad. "
        f"La inversión total estimada es <b>{presupuesto:,.0f} MCOP</b>. "
        f"Se recomienda garantizar la ejecución de los proyectos de alta prioridad en los primeros dos años "
        f"para consolidar la base tecnológica antes de escalar las iniciativas de menor prioridad."
    )

# ════════════════════════════════════════════════════════════════
#  SECCIÓN MAPA DE CALOR (sin cambios)
# ════════════════════════════════════════════════════════════════
if calor is not None:
    st.subheader("Mapa de Calor – Priorización Digital")

    calor["Puntuación"] = pd.to_numeric(calor["Puntuación"], errors="coerce")
    calor_grp = calor.groupby(["Área", "Proceso"])["Puntuación"].max().reset_index()

    orden_filas = [
        "la Empresa", "Infraestructura de la Comunidad",
        "Construcción del Gestión del Tecnológico", "Desarrollo",
        "Aprovisionamientos", "Logística Interna", "Operaciones",
        "Marketing y Ventas", "Servicios Postventa",
    ]
    orden_cols = [
        "Modernización arquitectura ERP nube",
        "N° procesos misionales con IA/IoT",
        "Seguridad digital SGSI ISO 27001",
        "Sostenimiento activos GeoCVC",
    ]

    pivot_orig = calor_grp.pivot(index="Área", columns="Proceso", values="Puntuación")
    pivot_orig = pivot_orig.reindex(index=orden_filas).reindex(columns=orden_cols)

    pivot = pivot_orig.copy()
    nombres_cortos = {
        "Modernización arquitectura ERP nube": "Modernización<br>ERP nube",
        "N° procesos misionales con IA/IoT":   "Procesos<br>IA/IoT",
        "Seguridad digital SGSI ISO 27001":    "Seguridad<br>SGSI ISO 27001",
        "Sostenimiento activos GeoCVC":        "Sostenimiento<br>GeoCVC",
    }
    pivot.columns = [nombres_cortos.get(c, c) for c in pivot.columns]

    fig_heat = px.imshow(
        pivot, text_auto=True, color_continuous_scale="RdYlGn",
        aspect="auto", zmin=0, zmax=9,
        labels={"x": "", "y": "", "color": "Puntuación"},
    )
    fig_heat.update_xaxes(tickangle=0, tickfont=dict(size=13), side="top")
    fig_heat.update_yaxes(tickfont=dict(size=12))
    fig_heat.update_layout(height=480, margin=dict(l=280, r=40, t=120, b=20))
    st.plotly_chart(fig_heat, use_container_width=True)

    areas_criticas = pivot_orig[pivot_orig.min(axis=1) == 0].index.tolist()
    areas_fuertes  = pivot_orig[pivot_orig.min(axis=1) >= 7].index.tolist()
    col_max        = pivot_orig.mean().idxmax()
    col_min        = pivot_orig.mean().idxmin()
    txt_criticas   = ", ".join(f"<b>{a}</b>"for a in areas_criticas) if areas_criticas else "<b>ninguna</b>"
    txt_fuertes    = ", ".join(f"<b>{a}</b>"for a in areas_fuertes)  if areas_fuertes  else "<b>ninguna</b>"
    caja_analisis(
        f"La iniciativa con mayor impacto transversal es <b>{col_max}</b> (promedio más alto entre todas las áreas). "
        f"La iniciativa con menor cobertura es <b>{col_min}</b>, indicando oportunidad de expansión. "
        f"Áreas con puntuación 0 en alguna iniciativa (vacíos críticos): {txt_criticas}. "
        f"Áreas con alta priorización en todas las iniciativas (≥7): {txt_fuertes}. "
        f"Se recomienda enfocar inversiones en las áreas críticas para evitar vacíos digitales "
        f"que comprometan la continuidad operacional de la CVC."
    )

# ════════════════════════════════════════════════════════════════
#  SECCIÓN MADUREZ DIGITAL (sin cambios)
# ════════════════════════════════════════════════════════════════
if madurez is not None:
    st.subheader("Madurez Digital")
    madurez["Puntaje"] = pd.to_numeric(madurez["Puntaje"], errors="coerce")
    mad_clean = madurez.dropna(subset=["Puntaje"])

    fig_mad = px.bar(mad_clean, x="Pregunta_ID", y="Puntaje", color="Dimensión",
                     labels={"Puntaje": "Puntuación (1-3)", "Pregunta_ID": "Pregunta"})
    fig_mad.add_hline(y=1.5, line_dash="dash", line_color="red",   annotation_text="Umbral bajo")
    fig_mad.add_hline(y=2.5, line_dash="dash", line_color="green", annotation_text="Umbral alto")
    st.plotly_chart(fig_mad, use_container_width=True)

    if not mad_clean.empty:
        promedio_global = mad_clean["Puntaje"].mean()
        bajo_umbral     = mad_clean[mad_clean["Puntaje"] <= 1.5]
        sobre_umbral    = mad_clean[mad_clean["Puntaje"] >= 2.5]
        nivel           = "inicial"if promedio_global < 1.8 else "en desarrollo"if promedio_global < 2.4 else "avanzado"

        if "Dimensión"in mad_clean.columns:
            dim_prom   = mad_clean.groupby("Dimensión")["Puntaje"].mean()
            dim_fuerte = dim_prom.idxmax()
            dim_debil  = dim_prom.idxmin()
            detalle    = (
                f"Por dimensión, <b>{dim_fuerte}</b> es la más madura (promedio {dim_prom.max():.2f}) "
                f"y <b>{dim_debil}</b> requiere mayor atención (promedio {dim_prom.min():.2f}). "
            )
        else:
            detalle = ""

        caja_analisis(
            f"El nivel de madurez digital global es <b>{promedio_global:.2f}/3.0</b>, clasificado como <b>{nivel}</b>. "
            f"{detalle}"
            f"<b>{len(bajo_umbral)} preguntas</b> están en zona crítica (≤1.5) y "
            f"<b>{len(sobre_umbral)} preguntas</b> superan el umbral alto (≥2.5). "
            f"Se recomienda priorizar acciones de mejora en las dimensiones débiles "
            f"antes de avanzar hacia tecnologías de cuarta revolución industrial."
        )