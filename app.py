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
            <span style="color:#aed6f1;font-size:13px;font-weight:600">ANÁLISIS</span>
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
        return valor <= target
    return valor >= target

# ── Navegacion por pestanas principales ─────────────────────────────────────
tab_ti, tab_datos, tab_ia = st.tabs([
    "Gobierno de TI",
    "Gobierno de Datos — DAMA-DMBOK2",
    "Gobierno de IA"
])

with tab_ti:
    # ── Sidebar ───────────────────────────────────────────────────
    st.sidebar.header("Filtros")
    años = sorted(kpis["Año"].dropna().unique())
    año_sel = st.sidebar.selectbox("Año", años)
    
    oeti_opts = ["Todos"] + sorted(proyectos["OETI"].dropna().unique())
    oeti_sel  = st.sidebar.selectbox("OETI", oeti_opts)
    proy_fil  = proyectos if oeti_sel == "Todos" else proyectos[proyectos["OETI"] == oeti_sel]
    
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
                  f"{v_ejec:.0f} %" if v_ejec is not None else "—",
                  f"Meta {t_ejec:.0f} %" if t_ejec is not None else "")
    with c2:
        st.metric("Satisfacción usuarios",
                  f"{v_sat:.0f} %" if v_sat is not None else "—",
                  f"Meta {t_sat:.0f} %" if t_sat is not None else "")
    with c3:
        st.metric("Resolución incidentes",
                  f"{v_inc:.0f} h" if v_inc is not None else "—",
                  f"Meta {t_inc:.0f} h" if t_inc is not None else "",
                  delta_color="inverse")
    with c4:
        st.metric("Gobierno TI",
                  f"{v_gov:.0f} %" if v_gov is not None else "—",
                  f"Meta {t_gov:.0f} %" if t_gov is not None else "")
    with c5:
        st.metric("Seguridad SGSI",
                  f"{v_seg:.0f} %" if v_seg is not None else "—",
                  f"Meta {t_seg:.0f} %" if t_seg is not None else "")
    with c6:
        st.metric("Competencias digitales",
                  f"{v_comp:.0f} %" if v_comp is not None else "—",
                  f"Meta {t_comp:.0f} %" if t_comp is not None else "")
    
    # ── Preparar datos BSC ────────────────────────────────────────
    kpis_viz = kpis_año.copy()
    kpis_viz["Cumple"]    = kpis_viz.apply(lambda r: cumple_meta(r["KPI"], r["Valor"], r["Target"]), axis=1)
    kpis_viz["Semaforo"]  = kpis_viz["Cumple"].apply(lambda c: "OK" if c else "NOK")
    kpis_viz["ValorFmt"]  = kpis_viz.apply(lambda r: fmt_valor(r["KPI"], r["Valor"]),  axis=1)
    kpis_viz["TargetFmt"] = kpis_viz.apply(lambda r: fmt_valor(r["KPI"], r["Target"]), axis=1)
    
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
    
    st.subheader("Balanced Scorecard")
    
    fig_bsc = px.bar(
        kpis_viz,
        x="pct_vs_meta", y="KPI", color="Perspectiva", orientation="h",
        color_discrete_map=COLORES_PERSPECTIVA,
        text=kpis_viz.apply(lambda r: f"{r['ValorFmt']} / Meta: {r['TargetFmt']}  [{r['Semaforo']}]", axis=1),
        labels={"pct_vs_meta": "% alcanzado vs meta", "KPI": ""},
        height=560, title=f"Desempeño BSC — {int(año_sel)}",
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
    
    kpis_validos = kpis_viz.dropna(subset=["Valor", "Target"])
    if not kpis_validos.empty:
        total_kpis = len(kpis_validos)
        kpis_ok    = kpis_validos["Cumple"].sum()
        kpis_nok   = total_kpis - kpis_ok
        pct_cumpl  = kpis_ok / total_kpis * 100
        rezagados  = kpis_validos[~kpis_validos["Cumple"]].sort_values("pct_vs_meta")
        peor_kpi   = rezagados.iloc[0] if not rezagados.empty else None
        persp_nok  = (
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
            f"requiriendo revisión inmediata del plan de acción asociado."
        )
    
    st.subheader("Estado por perspectiva")
    tabla_display = kpis_viz[["Perspectiva", "KPI", "Unidad", "Semaforo", "ValorFmt", "TargetFmt"]].rename(columns={
        "Semaforo": "Estado", "ValorFmt": "Valor real", "TargetFmt": "Meta",
    })
    st.dataframe(tabla_display, use_container_width=True, hide_index=True,
                 column_config={"Estado": st.column_config.TextColumn("Estado", width="small")})
    
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
        fig_pct = px.line(tend_pct, x="Año", y="Valor", color="KPI", markers=True,
                          labels={"Valor": "% alcanzado"},
                          color_discrete_sequence=px.colors.qualitative.Vivid)
        for kpi_name, grp in tend_pct.groupby("KPI"):
            fig_pct.add_scatter(x=grp["Año"], y=grp["Target"], mode="lines",
                                line=dict(dash="dot", width=1), showlegend=False, opacity=0.5)
        fig_pct.update_layout(plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a", font_color="white",
                              xaxis=dict(dtick=1, gridcolor="#1e3a5f"), yaxis=dict(gridcolor="#1e3a5f"))
        st.plotly_chart(fig_pct, use_container_width=True)
    with tab2:
        if not tend_hrs.empty:
            fig_hrs = px.line(tend_hrs, x="Año", y="Valor", color="KPI", markers=True,
                              labels={"Valor": "Horas"}, color_discrete_sequence=["#e74c3c"])
            fig_hrs.add_scatter(x=tend_hrs["Año"], y=tend_hrs["Target"], mode="lines",
                                line=dict(dash="dot", color="#aaaaaa", width=1), name="Meta horas")
            fig_hrs.update_layout(plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a", font_color="white",
                                  xaxis=dict(dtick=1, gridcolor="#1e3a5f"),
                                  yaxis=dict(gridcolor="#1e3a5f", title="Horas (menor = mejor)"))
            st.plotly_chart(fig_hrs, use_container_width=True)
    
    if not kpis_tend.empty:
        resumen = []
        for kpi, grp in kpis_tend.groupby("KPI"):
            grp = grp.sort_values("Año")
            if len(grp) >= 2:
                inicio, fin = grp.iloc[0]["Valor"], grp.iloc[-1]["Valor"]
                if kpi in KPIS_HORAS:
                    tend = "mejora" if fin < inicio else "deterioro"
                    etiq = f"{inicio:.0f} h → {fin:.0f} h"
                else:
                    tend = "creciente" if fin > inicio else "decreciente"
                    etiq = f"{inicio:.0f}% → {fin:.0f}%"
                resumen.append(f"<b>{kpi}</b>: {tend} ({etiq})")
        caja_analisis("Tendencias 2026–2029: " + " | ".join(resumen) +
                      ". Monitorear trimestralmente los indicadores con tendencia decreciente.")
    
    st.subheader("Radar de cumplimiento BSC")
    radar_data = (kpis_viz.groupby("Perspectiva", observed=True)["pct_vs_meta"]
                  .mean().reset_index().rename(columns={"pct_vs_meta": "Cumplimiento_pct"}))
    fig_radar = go.Figure()
    r_vals = radar_data["Cumplimiento_pct"].tolist()
    theta  = radar_data["Perspectiva"].tolist()
    fig_radar.add_trace(go.Scatterpolar(
        r=r_vals + [r_vals[0]], theta=theta + [theta[0]],
        fill="toself", fillcolor="rgba(52,152,219,0.3)",
        line=dict(color="#3498db", width=2), name=f"Año {int(año_sel)}"))
    fig_radar.add_trace(go.Scatterpolar(
        r=[100] * (len(radar_data) + 1), theta=theta + [theta[0]],
        mode="lines", line=dict(color="white", dash="dot", width=1), name="Meta 100%"))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 150], gridcolor="#1e3a5f",
                                   tickfont=dict(color="white"), ticksuffix="%"),
                   angularaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="white")),
                   bgcolor="#0d1b2a"),
        paper_bgcolor="#0d1b2a", font_color="white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.15), height=480)
    st.plotly_chart(fig_radar, use_container_width=True)
    persp_lideres = radar_data.nlargest(2,  "Cumplimiento_pct")["Perspectiva"].tolist()
    persp_rezag   = radar_data.nsmallest(2, "Cumplimiento_pct")["Perspectiva"].tolist()
    caja_analisis(
        f"Perspectivas con mayor cumplimiento: <b>{'</b> y <b>'.join(persp_lideres)}</b>. "
        f"Perspectivas más alejadas de la meta: <b>{'</b> y <b>'.join(persp_rezag)}</b>. "
        f"Los vacíos en el radar señalan las áreas de inversión prioritaria para el siguiente ciclo."
    )
    
    # ════════════════════════════════════════════════════════════════
    #  SECCIÓN PORTAFOLIO PETI
    # ════════════════════════════════════════════════════════════════
    st.subheader("Portafolio PETI")
    proy_fil = proy_fil.copy()
    proy_fil["Inicio_dt"] = pd.to_datetime(proy_fil["Inicio"].astype(int).astype(str) + "-01-01")
    proy_fil["Fin_dt"]    = pd.to_datetime(proy_fil["Fin"].astype(int).astype(str)    + "-12-31")
    proy_fil["Label"]     = proy_fil["ID"] + " – " + proy_fil["Nombre"].str.slice(0, 45)
    
    COLORES_PRIORIDAD = {"Alta": "#e74c3c", "Media": "#e67e22", "Baja": "#3498db"}
    fig_gantt = px.timeline(
        proy_fil, x_start="Inicio_dt", x_end="Fin_dt", y="Label", color="Prioridad",
        color_discrete_map=COLORES_PRIORIDAD,
        hover_data={"Presupuesto_MCOP": True, "OETI": True, "Estado": True, "Label": False},
        labels={"Label": ""}, height=520)
    fig_gantt.update_yaxes(autorange="reversed", tickfont=dict(size=12))
    fig_gantt.update_xaxes(dtick="M12", tickformat="%Y",
                           range=["2025-07-01", "2030-01-01"], gridcolor="#1e3a5f")
    fig_gantt.update_layout(plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
                            font_color="white", legend_title_text="Prioridad",
                            margin=dict(l=10, r=20, t=20, b=20))
    st.plotly_chart(fig_gantt, use_container_width=True)
    
    with st.expander("Detalle proyectos"):
        st.dataframe(proy_fil[["ID", "Nombre", "OETI", "Presupuesto_MCOP", "Inicio", "Fin", "Prioridad", "Estado"]],
                     use_container_width=True, hide_index=True)
    
    if not proy_fil.empty:
        total_proy  = len(proy_fil)
        alta        = len(proy_fil[proy_fil["Prioridad"].str.lower() == "alta"])  if "Prioridad" in proy_fil.columns else 0
        media       = len(proy_fil[proy_fil["Prioridad"].str.lower() == "media"]) if "Prioridad" in proy_fil.columns else 0
        baja        = len(proy_fil[proy_fil["Prioridad"].str.lower() == "baja"])  if "Prioridad" in proy_fil.columns else 0
        presupuesto = proy_fil["Presupuesto_MCOP"].sum() if "Presupuesto_MCOP" in proy_fil.columns else 0
        filtro_txt  = f" (filtrado por OETI: {oeti_sel})" if oeti_sel != "Todos" else ""
        caja_analisis(
            f"El portafolio{filtro_txt} contiene <b>{total_proy} proyectos</b>: "
            f"<b>{alta} de alta</b>, <b>{media} de media</b> y <b>{baja} de baja</b> prioridad. "
            f"La inversión total estimada es <b>{presupuesto:,.0f} MCOP</b>. "
            f"Se recomienda garantizar la ejecución de los proyectos de alta prioridad en los primeros dos años."
        )
    
    # ════════════════════════════════════════════════════════════════
    #  SECCIÓN MAPA DE CALOR
    # ════════════════════════════════════════════════════════════════
    if calor is not None:
        st.subheader("Mapa de Calor – Priorización Digital")
        calor["Puntuación"] = pd.to_numeric(calor["Puntuación"], errors="coerce")
        calor_grp = calor.groupby(["Área", "Proceso"])["Puntuación"].max().reset_index()
        orden_filas = ["la Empresa", "Infraestructura de la Comunidad",
                       "Construcción del Gestión del Tecnológico", "Desarrollo",
                       "Aprovisionamientos", "Logística Interna", "Operaciones",
                       "Marketing y Ventas", "Servicios Postventa"]
        orden_cols  = ["Modernización arquitectura ERP nube", "N° procesos misionales con IA/IoT",
                       "Seguridad digital SGSI ISO 27001", "Sostenimiento activos GeoCVC"]
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
        fig_heat = px.imshow(pivot, text_auto=True, color_continuous_scale="RdYlGn",
                             aspect="auto", zmin=0, zmax=9,
                             labels={"x": "", "y": "", "color": "Puntuación"})
        fig_heat.update_xaxes(tickangle=0, tickfont=dict(size=13), side="top")
        fig_heat.update_yaxes(tickfont=dict(size=12))
        fig_heat.update_layout(height=480, margin=dict(l=280, r=40, t=120, b=20))
        st.plotly_chart(fig_heat, use_container_width=True)
        areas_criticas = pivot_orig[pivot_orig.min(axis=1) == 0].index.tolist()
        areas_fuertes  = pivot_orig[pivot_orig.min(axis=1) >= 7].index.tolist()
        col_max = pivot_orig.mean().idxmax()
        col_min = pivot_orig.mean().idxmin()
        txt_criticas = ", ".join(f"<b>{a}</b>" for a in areas_criticas) if areas_criticas else "<b>ninguna</b>"
        txt_fuertes  = ", ".join(f"<b>{a}</b>" for a in areas_fuertes)  if areas_fuertes  else "<b>ninguna</b>"
        caja_analisis(
            f"Iniciativa con mayor impacto transversal: <b>{col_max}</b>. "
            f"Iniciativa con menor cobertura: <b>{col_min}</b>. "
            f"Areas con vacios criticos (puntuacion 0): {txt_criticas}. "
            f"Areas con alta priorización en todas las iniciativas (>=7): {txt_fuertes}."
        )
    
    # ════════════════════════════════════════════════════════════════
    #  SECCIÓN MADUREZ DIGITAL
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
            nivel = "inicial" if promedio_global < 1.8 else "en desarrollo" if promedio_global < 2.4 else "avanzado"
            if "Dimensión" in mad_clean.columns:
                dim_prom   = mad_clean.groupby("Dimensión")["Puntaje"].mean()
                dim_fuerte = dim_prom.idxmax()
                dim_debil  = dim_prom.idxmin()
                detalle = (f"Por dimensión, <b>{dim_fuerte}</b> es la más madura ({dim_prom.max():.2f}) "
                           f"y <b>{dim_debil}</b> requiere mayor atención ({dim_prom.min():.2f}). ")
            else:
                detalle = ""
            caja_analisis(
                f"Nivel de madurez digital global: <b>{promedio_global:.2f}/3.0</b> — <b>{nivel}</b>. "
                f"{detalle}"
                f"<b>{len(bajo_umbral)} preguntas</b> en zona critica (<=1.5) y "
                f"<b>{len(sobre_umbral)} preguntas</b> sobre umbral alto (>=2.5)."
            )
    
    # ════════════════════════════════════════════════════════════════
    #  SECCIÓN COBIT 2019
    #  Management Awareness Diagnostic (40 procesos) +
    #  Diagnóstico Control TI (niveles 0-5 para 37 procesos)
    # ════════════════════════════════════════════════════════════════
    st.subheader("COBIT 2019 – Management Awareness & Diagnóstico de Control")
    
    # ── Datos integrados de ambos archivos ───────────────────────
    # Columnas: Subdominio, Código, Nombre (EN), Importancia(1-5), Performance(1-5),
    #           Auditado(Y/N), Formalidad(Y/N), Responsable,
    #           NivelCapacidad(0-5 o None), Observacion
    cobit_raw = [
        ("Evaluate, Direct and Monitor", "EDM01", "Ensured Governance Framework Setting and Maintenance", 5, 3, "N", "N", "Jefe OTI, Direccion General",          1, "Sin marco formal de gobierno TI ni comites definidos."),
        ("Evaluate, Direct and Monitor", "EDM02", "Ensured Benefits Delivery",                            5, 3, "N", "N", "Direccion General",                      1, "No se mide el valor publico generado por TI. Sin evaluacion post-implementacion."),
        ("Evaluate, Direct and Monitor", "EDM03", "Ensured Risk Optimization",                            5, 4, "N", "N", "Jefe OTI, Direccion General",          0, "Riesgos criticos sin mitigar. Sin BCP/DRP probado. Gestion reactiva."),
        ("Evaluate, Direct and Monitor", "EDM04", "Ensured Resource Optimization",                        4, 3, "N", "N", "Jefe OTI, Financiera",                 2, "Presupuesto definido y ejecutado. Sin optimizacion de recursos adicional."),
        ("Evaluate, Direct and Monitor", "EDM05", "Ensured Stakeholder Engagement",                       4, 3, "N", "N", "Direccion General",                      1, "Sin informes periodicos de desempeño TI para la alta direccion."),
        ("Align, Plan and Organize",     "APO01", "Managed I&T Management Framework",                     5, 3, "N", "N", "Jefe OTI",                             1, "Sin marco formal (COBIT/ITIL/ISO). MRAE usado parcialmente."),
        ("Align, Plan and Organize",     "APO02", "Managed Strategy",                                     5, 2, "Y", "N", "Direccion General, Planeacion",          3, "PETI 2026-2029 y BSC documentados y alineados con la mision."),
        ("Align, Plan and Organize",     "APO03", "Managed Enterprise Architecture",                      4, 4, "N", "N", "Jefe OTI",                             1, "Sin arquitectura empresarial formalizada. Integraciones por archivos planos."),
        ("Align, Plan and Organize",     "APO04", "Managed Innovation",                                   4, 4, "N", "N", "Jefe OTI",                             1, "Sin proyectos IA/IoT en ejecucion. Solo intenciones en el PETI."),
        ("Align, Plan and Organize",     "APO05", "Managed Portfolio",                                    5, 2, "Y", "N", "Jefe OTI, Planeacion",                 3, "Portafolio de 12 proyectos PETI definido con inversion de $12.300M COP."),
        ("Align, Plan and Organize",     "APO06", "Managed Budget and Costs",                             5, 2, "Y", "Y", "Jefe OTI, Financiera",                 3, "Presupuesto auditado. Unico proceso con auditoria formal."),
        ("Align, Plan and Organize",     "APO07", "Managed Human Resources",                              4, 3, "N", "N", "Jefe OTI, Talento Humano",             2, "Planes de formacion existentes. Sin plan formal de retencion."),
        ("Align, Plan and Organize",     "APO08", "Managed Relationships",                                4, 3, "N", "N", "Jefe OTI",                             2, "Comunicacion con areas misionales sin programa formal."),
        ("Align, Plan and Organize",     "APO09", "Managed Service Agreements",                           4, 3, "Y", "N", "Jefe OTI",                             1, "Sin politicas formales. Dependencia critica de Oracle, ESRI, Arq."),
        ("Align, Plan and Organize",     "APO10", "Managed Vendors",                                      5, 4, "N", "N", "Jefe OTI",                             1, "Sin sistema de gestion de calidad TI formal."),
        ("Align, Plan and Organize",     "APO11", "Managed Quality",                                      4, 3, "N", "N", "Jefe OTI",                             0, "Riesgos identificados sin registro actualizado ni plan de mitigacion."),
        ("Align, Plan and Organize",     "APO12", "Managed Risk",                                         5, 4, "N", "N", "Jefe OTI, Direccion General",          1, "MSPI en nivel inicial. Sin SIEM, IAM ni backups inmutables."),
        ("Align, Plan and Organize",     "APO13", "Manage Security",                                      5, 4, "N", "N", "Jefe OTI",                             None, "No evaluado en diagnostico de control."),
        ("Align, Plan and Organize",     "APO14", "Managed Data",                                         5, 4, "N", "N", "Jefe OTI, Grupo SIA",                  None, "No evaluado en diagnostico de control."),
        ("Build, Acquire and Operate",   "BAI01", "Managed Programs",                                     4, 3, "Y", "N", "Jefe OTI",                             2, "PETI formalizado con cronogramas. Ejecucion presupuestal 2026 al 70%."),
        ("Build, Acquire and Operate",   "BAI02", "Managed Requirements Definition",                      4, 3, "N", "N", "Jefe OTI",                             2, "Requerimientos definidos por proyecto, sin proceso estandarizado."),
        ("Build, Acquire and Operate",   "BAI03", "Managed Solutions Identification and Build",           4, 3, "N", "N", "Jefe OTI",                             2, "Sin proceso estandarizado de evaluacion hacer vs comprar."),
        ("Build, Acquire and Operate",   "BAI04", "Managed Availability and Capacity",                    4, 3, "N", "N", "Jefe OTI",                             2, "Monitoreo de disponibilidad activo. Sin plan formal de capacidad."),
        ("Build, Acquire and Operate",   "BAI05", "Managed Organizational Change",                        4, 4, "N", "N", "Jefe OTI, Talento Humano",             1, "Baja apropiacion tecnologica. Sin programa formal de gestion del cambio."),
        ("Build, Acquire and Operate",   "BAI06", "Managed IT Changes",                                   4, 3, "N", "N", "Jefe OTI",                             2, "Cambios gestionados caso a caso. Sin proceso ITIL formal."),
        ("Build, Acquire and Operate",   "BAI07", "Managed IT Change Acceptance and Transitioning",       4, 3, "N", "N", "Jefe OTI",                             2, "Transiciones sin proceso de aceptacion estandarizado."),
        ("Build, Acquire and Operate",   "BAI08", "Managed Knowledge",                                    3, 4, "N", "N", "Jefe OTI",                             1, "Baja transferencia de conocimiento. Dependencia de personal clave."),
        ("Build, Acquire and Operate",   "BAI09", "Managed Assets",                                       4, 3, "Y", "N", "Jefe OTI",                             2, "Activos inventariados. Sin ciclo de vida formal."),
        ("Build, Acquire and Operate",   "BAI10", "Managed Configuration",                                3, 4, "N", "N", "Jefe OTI",                             1, "Sin gestion de configuracion centralizada."),
        ("Build, Acquire and Operate",   "BAI11", "Managed Projects",                                     5, 3, "Y", "N", "Jefe OTI",                             1, "Sin gestion formal de problemas ni analisis de causa raiz."),
        ("Deliver, Service and Support", "DSS01", "Managed Operations",                                   5, 3, "Y", "N", "Jefe OTI",                             2, "Operaciones gestionadas con monitoreo. Sin proceso formal documentado."),
        ("Deliver, Service and Support", "DSS02", "Managed Service Requests and Incidents",               5, 3, "Y", "N", "Jefe OTI",                             2, "Mesa de servicio tercerizada. Tiempo de resolucion 5.5 h."),
        ("Deliver, Service and Support", "DSS03", "Managed Problems",                                     4, 4, "N", "N", "Jefe OTI",                             1, "Sin gestion formal de problemas recurrentes."),
        ("Deliver, Service and Support", "DSS04", "Managed Continuity",                                   5, 5, "N", "N", "Jefe OTI, Direccion General",          0, "CRITICO: Sin BCP/DRP probado. Zona de alta amenaza sismica."),
        ("Deliver, Service and Support", "DSS05", "Managed Security Services",                            5, 4, "N", "N", "Jefe OTI",                             1, "MSPI inicial. Gestion de seguridad reactiva."),
        ("Deliver, Service and Support", "DSS06", "Managed Business Process Controls",                    4, 4, "N", "N", "Jefe OTI",                             1, "Sin controles automatizados. Integraciones por archivos planos."),
        ("Monitor, Evaluate and Assess", "MEA01", "Managed Performance and Conformance Monitoring",       5, 3, "Y", "N", "Jefe OTI, Planeacion",                 2, "BSC con indicadores definidos. Seguimiento no sistematico."),
        ("Monitor, Evaluate and Assess", "MEA02", "Managed System of Internal Control",                   4, 4, "N", "N", "Jefe OTI, Control Interno",            1, "Sin proceso formal de monitoreo normativo (Decreto 620, Ley 1581)."),
        ("Monitor, Evaluate and Assess", "MEA03", "Managed Compliance with External Requirements",        5, 3, "N", "N", "Jefe OTI",                             1, "Sin sistema de control interno para TI formalizado."),
        ("Monitor, Evaluate and Assess", "MEA04", "Managed Assurance",                                    4, 4, "N", "N", "Jefe OTI, Control Interno",            None, "No evaluado en diagnostico de control."),
    ]
    
    cobit_df = pd.DataFrame(cobit_raw, columns=[
        "Subdominio", "Proceso", "Nombre", "Importancia", "Performance",
        "Auditado", "Formalidad", "Responsable", "NivelCapacidad", "Observacion"
    ])
    cobit_df["Dominio"] = cobit_df["Proceso"].str[:3]
    cobit_df["Brecha"] = cobit_df["Importancia"] - cobit_df["Performance"]
    
    # ── Tabs principales ─────────────────────────────────────────
    tab_aware, tab_diag = st.tabs([
        "Management Awareness (Importancia vs Performance)",
        "Diagnostico de Control (Nivel de Capacidad 0-5)"
    ])
    
    # ════ TAB 1: Management Awareness ════════════════════════════
    with tab_aware:
    
        # Métricas resumen
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Importancia promedio",  f"{cobit_df['Importancia'].mean():.1f} / 5")
        a2.metric("Performance promedio",  f"{cobit_df['Performance'].mean():.1f} / 5")
        a3.metric("Brecha promedio (I-P)", f"{cobit_df['Brecha'].mean():.1f}")
        a4.metric("Procesos con brecha >= 2", str(len(cobit_df[cobit_df['Brecha'] >= 2])))
    
        # Gráfico scatter Importancia vs Performance
        fig_scatter = px.scatter(
            cobit_df,
            x="Performance", y="Importancia",
            color="Dominio", text="Proceso",
            hover_data={"Nombre": True, "Responsable": True, "Auditado": True, "Brecha": True},
            labels={"Performance": "Performance (1=bien, 5=mal)", "Importancia": "Importancia (1=baja, 5=alta)"},
            height=500,
            title="Importancia vs Performance — 40 procesos COBIT 2019",
            color_discrete_map={"EDM": "#1abc9c", "APO": "#3498db", "BAI": "#e67e22", "DSS": "#e74c3c", "MEA": "#9b59b6"},
        )
        # Cuadrantes
        fig_scatter.add_hline(y=3, line_dash="dot", line_color="#555")
        fig_scatter.add_vline(x=3, line_dash="dot", line_color="#555")
        # Zona critica: alta importancia + bajo performance (cuadrante sup-derecho)
        fig_scatter.add_shape(type="rect", x0=3, x1=5.2, y0=3, y1=5.2,
                              fillcolor="rgba(231,76,60,0.08)", line_width=0)
        fig_scatter.update_traces(textposition="top center", textfont_size=9)
        fig_scatter.update_layout(
            plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a", font_color="white",
            xaxis=dict(range=[0.5, 5.5], gridcolor="#1e3a5f"),
            yaxis=dict(range=[0.5, 5.5], gridcolor="#1e3a5f"),
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
        # Gráfico de brechas ordenado
        cobit_brecha = cobit_df.sort_values("Brecha", ascending=False)
        fig_brecha = px.bar(
            cobit_brecha, x="Proceso", y="Brecha", color="Dominio",
            text="Brecha",
            labels={"Brecha": "Brecha (Importancia - Performance)"},
            height=380,
            title="Brecha por proceso (mayor = más urgente)",
            color_discrete_map={"EDM": "#1abc9c", "APO": "#3498db", "BAI": "#e67e22", "DSS": "#e74c3c", "MEA": "#9b59b6"},
        )
        fig_brecha.add_hline(y=0, line_color="white", line_width=1)
        fig_brecha.update_traces(textposition="outside")
        fig_brecha.update_layout(
            plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a", font_color="white",
            xaxis=dict(tickangle=-45, gridcolor="#1e3a5f"),
            yaxis=dict(gridcolor="#1e3a5f"),
            margin=dict(l=10, r=10, t=50, b=80),
        )
        st.plotly_chart(fig_brecha, use_container_width=True)
    
        # Tabla completa
        with st.expander("Tabla detalle — 40 procesos"):
            st.dataframe(
                cobit_df[["Dominio", "Proceso", "Nombre", "Importancia", "Performance",
                           "Brecha", "Auditado", "Formalidad", "Responsable"]],
                use_container_width=True, hide_index=True,
            )
    
        # Análisis
        top_brecha  = cobit_brecha.head(5)["Proceso"].tolist()
        no_auditado = len(cobit_df[cobit_df["Auditado"] == "N"])
        no_formal   = len(cobit_df[cobit_df["Formalidad"] == "N"])
        zona_critica = cobit_df[(cobit_df["Importancia"] >= 4) & (cobit_df["Performance"] >= 4)]
        caja_analisis(
            f"De los <b>40 procesos COBIT 2019</b> evaluados, la brecha promedio importancia-performance es "
            f"<b>{cobit_df['Brecha'].mean():.1f}</b> puntos. "
            f"Los procesos con mayor urgencia de mejora son: <b>{', '.join(top_brecha)}</b>. "
            f"<b>{len(zona_critica)} procesos</b> caen en la zona critica (alta importancia + bajo performance). "
            f"Solo <b>{len(cobit_df[cobit_df['Auditado']=='Y'])} de 40</b> procesos han sido auditados y "
            f"<b>{len(cobit_df[cobit_df['Formalidad']=='Y'])} de 40</b> tienen formalidad documentada, "
            f"evidenciando una brecha significativa de gobernanza."
        )
    
    # ════ TAB 2: Diagnóstico de Control ══════════════════════════
    with tab_diag:
    
        cobit_nivel = cobit_df.dropna(subset=["NivelCapacidad"]).copy()
        cobit_nivel["NivelCapacidad"] = cobit_nivel["NivelCapacidad"].astype(int)
    
        nivel_prom = cobit_nivel["NivelCapacidad"].mean()
        criticos   = len(cobit_nivel[cobit_nivel["NivelCapacidad"] == 0])
        gestionado = len(cobit_nivel[cobit_nivel["NivelCapacidad"] >= 2])
        total_eval = len(cobit_nivel)
    
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Nivel promedio", f"{nivel_prom:.2f} / 5")
        d2.metric("Procesos nivel 0 (inexistente)", str(criticos))
        d3.metric("Procesos nivel >= 2 (gestionado)", str(gestionado))
        d4.metric("Procesos evaluados", f"{total_eval} / 40")
    
        # Barras nivel de capacidad
        fig_nivel = px.bar(
            cobit_nivel.sort_values(["Dominio", "Proceso"]),
            x="Proceso", y="NivelCapacidad", color="Dominio",
            text="NivelCapacidad",
            labels={"NivelCapacidad": "Nivel de Capacidad (0-5)", "Proceso": ""},
            height=420,
            title="Nivel de Capacidad COBIT 2019 por Proceso",
            color_discrete_map={"EDM": "#1abc9c", "APO": "#3498db", "BAI": "#e67e22", "DSS": "#e74c3c", "MEA": "#9b59b6"},
        )
        fig_nivel.add_hline(y=2, line_dash="dash", line_color="#f1c40f",
                            annotation_text="Minimo aceptable (2)", annotation_font_color="#f1c40f")
        fig_nivel.add_hline(y=nivel_prom, line_dash="dot", line_color="white",
                            annotation_text=f"Promedio {nivel_prom:.1f}", annotation_font_color="white")
        fig_nivel.update_traces(textposition="outside")
        fig_nivel.update_layout(
            plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a", font_color="white",
            xaxis=dict(tickangle=-45, gridcolor="#1e3a5f"),
            yaxis=dict(range=[0, 5.5], gridcolor="#1e3a5f"),
            margin=dict(l=10, r=10, t=50, b=80),
        )
        st.plotly_chart(fig_nivel, use_container_width=True)
    
        # Radar por dominio
        radar_cobit = cobit_nivel.groupby("Dominio")["NivelCapacidad"].mean().reset_index()
        fig_rc = go.Figure()
        rv = radar_cobit["NivelCapacidad"].tolist()
        th = radar_cobit["Dominio"].tolist()
        fig_rc.add_trace(go.Scatterpolar(
            r=rv + [rv[0]], theta=th + [th[0]],
            fill="toself", fillcolor="rgba(231,76,60,0.25)",
            line=dict(color="#e74c3c", width=2), name="Nivel actual"))
        fig_rc.add_trace(go.Scatterpolar(
            r=[3] * (len(radar_cobit) + 1), theta=th + [th[0]],
            mode="lines", line=dict(color="#2ecc71", dash="dot", width=1), name="Meta nivel 3"))
        fig_rc.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5], gridcolor="#1e3a5f", tickfont=dict(color="white")),
                angularaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="white")),
                bgcolor="#0d1b2a"),
            paper_bgcolor="#0d1b2a", font_color="white",
            legend=dict(orientation="h", yanchor="bottom", y=-0.15), height=420,
        )
        st.plotly_chart(fig_rc, use_container_width=True)
    
        # Tabla filtrable
        dom_sel = st.selectbox("Filtrar por dominio", ["Todos", "EDM", "APO", "BAI", "DSS", "MEA"])
        cobit_fil = cobit_nivel if dom_sel == "Todos" else cobit_nivel[cobit_nivel["Dominio"] == dom_sel]
        st.dataframe(
            cobit_fil[["Dominio", "Proceso", "Nombre", "NivelCapacidad", "Observacion"]].rename(
                columns={"NivelCapacidad": "Nivel (0-5)", "Observacion": "Observacion / Brecha"}),
            use_container_width=True, hide_index=True,
        )
    
        # Análisis
        proc_criticos  = cobit_nivel[cobit_nivel["NivelCapacidad"] == 0]["Proceso"].tolist()
        proc_avanzados = cobit_nivel[cobit_nivel["NivelCapacidad"] >= 3]["Proceso"].tolist()
        dom_debil  = cobit_nivel.groupby("Dominio")["NivelCapacidad"].mean().idxmin()
        dom_fuerte = cobit_nivel.groupby("Dominio")["NivelCapacidad"].mean().idxmax()
        caja_analisis(
            f"Sobre <b>{total_eval} procesos evaluados</b>, el nivel de capacidad promedio es "
            f"<b>{nivel_prom:.2f}/5</b>, muy por debajo del nivel minimo aceptable de 2. "
            f"<b>{criticos} procesos en nivel 0 (inexistente)</b>: <b>{', '.join(proc_criticos)}</b> — "
            f"riesgo critico de continuidad y seguridad que requiere accion inmediata. "
            f"Solo <b>{len(proc_avanzados)} procesos</b> alcanzan nivel 3 o superior: "
            f"<b>{', '.join(proc_avanzados)}</b>. "
            f"Dominio mas debil: <b>{dom_debil}</b>. Dominio mas avanzado: <b>{dom_fuerte}</b>. "
            f"Prioridad inmediata: formalizar BCP/DRP (DSS04), gestion de riesgos (APO11/EDM03) "
            f"y marco de gobierno TI (EDM01)."
        )
    
    # ════════════════════════════════════════════════════════════════
    #  SECCIÓN RESULTADOS AUTOMATIZACIÓN n8n — COBIT 2019
    #  Lee en tiempo real desde Google Sheets (hoja Resultados)
    # ════════════════════════════════════════════════════════════════
    st.subheader("Resultados del Flujo de Automatización — COBIT 2019")
    
    SHEET_ID_RESULTADOS = "1cUEJ_K7_qkZaReLPR-sKDZ8lS8WkiUuiX3aTtqfZkdE"
    URL_RESULTADOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID_RESULTADOS}/export?format=csv&sheet=Resultados"
    
    @st.cache_data(ttl=300)  # refresca cada 5 minutos
    def cargar_resultados(url):
        try:
            df = pd.read_csv(url)
            df["Fecha_Ejecucion"] = pd.to_datetime(df["Fecha_Ejecucion"], errors="coerce")
            for col in ["Total_Procesos","Nivel_Promedio","Procesos_Criticos","Procesos_Gestionados",
                        "Procesos_En_Riesgo","Semaforo_Rojo","Semaforo_Naranja","Semaforo_Amarillo","Semaforo_Verde"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            return df.sort_values("Fecha_Ejecucion", ascending=False).reset_index(drop=True)
        except Exception as e:
            return None
    
    res_df = cargar_resultados(URL_RESULTADOS)
    
    if res_df is None or res_df.empty:
        st.info("No hay ejecuciones registradas. Ejecuta el workflow en n8n para ver resultados aquí.")
    else:
        # ── Selector de ejecución ─────────────────────────────────
        opciones = [f"Ejecución {i+1} — {row['Periodo']}  ({row['Fecha_Ejecucion'].strftime('%Y-%m-%d %H:%M')})"
                    for i, row in res_df.iterrows()]
        sel_idx = st.selectbox("Seleccionar ejecución", range(len(opciones)), format_func=lambda i: opciones[i])
        ult = res_df.iloc[sel_idx]
    
        # ── Métricas clave ────────────────────────────────────────
        r1, r2, r3, r4, r5 = st.columns(5)
        r1.metric("Nivel promedio",      f"{ult['Nivel_Promedio']:.1f} / 5")
        r2.metric("Procesos criticos",   int(ult['Procesos_Criticos']),   delta=None)
        r3.metric("En riesgo",           int(ult['Procesos_En_Riesgo']))
        r4.metric("Gestionados (>=2)",   int(ult['Procesos_Gestionados']))
        r5.metric("Dominio mas debil",   ult['Dominio_Mas_Debil'])
    
        # ── Gráfico semáforo ──────────────────────────────────────
        col_left, col_right = st.columns([1, 2])
    
        with col_left:
            semaforo_df = pd.DataFrame({
                "Estado":   ["Critico (0)", "En riesgo (1)", "Gestionado (2)", "Avanzado (3+)"],
                "Cantidad": [int(ult["Semaforo_Rojo"]), int(ult["Semaforo_Naranja"]),
                             int(ult["Semaforo_Amarillo"]), int(ult["Semaforo_Verde"])],
                "Color":    ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71"]
            })
            fig_sem = px.bar(
                semaforo_df, x="Estado", y="Cantidad", color="Estado",
                color_discrete_map={row["Estado"]: row["Color"] for _, row in semaforo_df.iterrows()},
                text="Cantidad", height=320,
                title="Distribucion semaforo COBIT",
            )
            fig_sem.update_traces(textposition="outside", showlegend=False)
            fig_sem.update_layout(
                plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a", font_color="white",
                xaxis=dict(gridcolor="#1e3a5f"), yaxis=dict(gridcolor="#1e3a5f", range=[0, 30]),
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(fig_sem, use_container_width=True)
    
        with col_right:
            # Evolución del nivel promedio entre ejecuciones
            if len(res_df) > 1:
                fig_evo = px.line(
                    res_df.sort_values("Fecha_Ejecucion"),
                    x="Fecha_Ejecucion", y="Nivel_Promedio",
                    markers=True, text="Nivel_Promedio",
                    labels={"Nivel_Promedio": "Nivel promedio", "Fecha_Ejecucion": "Fecha"},
                    title="Evolucion del nivel promedio entre ejecuciones",
                    height=320,
                )
                fig_evo.add_hline(y=2, line_dash="dash", line_color="#f1c40f",
                                  annotation_text="Meta nivel 2", annotation_font_color="#f1c40f")
                fig_evo.update_traces(textposition="top center", textfont_size=11,
                                      line=dict(color="#3498db", width=2))
                fig_evo.update_layout(
                    plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a", font_color="white",
                    xaxis=dict(gridcolor="#1e3a5f"), yaxis=dict(gridcolor="#1e3a5f", range=[0, 5]),
                    margin=dict(l=10, r=10, t=40, b=10),
                )
                st.plotly_chart(fig_evo, use_container_width=True)
            else:
                st.info("Ejecuta el workflow más veces para ver la evolución temporal.")
    
        # ── Procesos urgentes ─────────────────────────────────────
        if pd.notna(ult.get("Procesos_Urgentes", None)):
            urgentes = [p.strip() for p in str(ult["Procesos_Urgentes"]).split(",")]
            cols_urg = st.columns(len(urgentes))
            for i, proc in enumerate(urgentes):
                cols_urg[i].markdown(
                    f'<div style="background:#e74c3c22;border:1px solid #e74c3c;border-radius:6px;'
                    f'padding:8px;text-align:center;color:#e74c3c;font-weight:bold;font-size:13px">'
                    f'{proc}</div>', unsafe_allow_html=True
                )
    
        # ── Análisis IA ───────────────────────────────────────────
        st.markdown("#### Analisis IA — Resumen ejecutivo")
        if pd.notna(ult.get("Analisis_IA", None)):
            analisis_limpio = str(ult["Analisis_IA"]).replace("**", "").strip()
            st.markdown(
                f'<div style="background:#1e3a5f;border-left:4px solid #2ecc71;border-radius:6px;'
                f'padding:16px 20px;margin-top:8px;margin-bottom:16px">'
                f'<span style="color:#aed6f1;font-size:13px;font-weight:600">IA — llama-3.3-70b (Groq)</span>'
                f'<p style="color:#ecf0f1;font-size:14px;margin-top:8px;margin-bottom:0;'
                f'line-height:1.8;white-space:pre-wrap">{analisis_limpio}</p></div>',
                unsafe_allow_html=True
            )
    
        # ── Recomendaciones IA ────────────────────────────────────
        st.markdown("#### Plan de accion e indicadores de seguimiento")
        if pd.notna(ult.get("Recomendaciones_IA", None)):
            rec_limpio = str(ult["Recomendaciones_IA"]).replace("**", "").strip()
            st.markdown(
                f'<div style="background:#1e2a3a;border-left:4px solid #e67e22;border-radius:6px;'
                f'padding:16px 20px;margin-top:8px;margin-bottom:24px">'
                f'<span style="color:#f39c12;font-size:13px;font-weight:600">PLAN DE ACCION</span>'
                f'<p style="color:#ecf0f1;font-size:14px;margin-top:8px;margin-bottom:0;'
                f'line-height:1.8;white-space:pre-wrap">{rec_limpio}</p></div>',
                unsafe_allow_html=True
            )
    
        # ── Historial de ejecuciones ──────────────────────────────
        with st.expander("Historial de ejecuciones"):
            st.dataframe(
                res_df[["Periodo", "Fecha_Ejecucion", "Nivel_Promedio", "Procesos_Criticos",
                        "Procesos_En_Riesgo", "Procesos_Gestionados",
                        "Dominio_Mas_Debil", "Dominio_Mas_Fuerte"]].rename(columns={
                    "Nivel_Promedio": "Nivel Prom.",
                    "Procesos_Criticos": "Criticos",
                    "Procesos_En_Riesgo": "En Riesgo",
                    "Procesos_Gestionados": "Gestionados",
                    "Dominio_Mas_Debil": "Dom. Debil",
                    "Dominio_Mas_Fuerte": "Dom. Fuerte",
                }),
                use_container_width=True, hide_index=True,
            )
    
        # Botón para forzar refresco
        if st.button("Actualizar datos desde n8n"):
            st.cache_data.clear()
            st.rerun()
    

with tab_datos:

    # ════════════════════════════════════════════════════════════════
    #  PESTAÑA 2 — GOBIERNO DE DATOS (DAMA-DMBOK2)
    # ════════════════════════════════════════════════════════════════

    # ── Métricas de madurez DAMA ─────────────────────────────────
    dama_areas = [
        ("Gobernanza de Datos",          1, 3),
        ("Arquitectura de Datos",         1, 3),
        ("Modelado de Datos",             1, 3),
        ("Almacenamiento y Operaciones",  2, 3),
        ("Seguridad de Datos",            1, 3),
        ("Integracion e Interoperabilidad",1,3),
        ("Gestion Documental",            2, 3),
        ("Datos Maestros y Referencia",   1, 3),
        ("Data Warehousing e IA",         1, 3),
        ("Metadatos",                     0, 3),
        ("Calidad de Datos",              1, 3),
    ]
    dama_df = pd.DataFrame(dama_areas, columns=["Area", "Actual", "Meta"])
    dama_df["Gap"] = dama_df["Meta"] - dama_df["Actual"]
    dama_df["pct"] = (dama_df["Actual"] / 5 * 100).round(1)

    mad_prom = dama_df["Actual"].mean()

    st.subheader("Gobierno de Datos — DAMA-DMBOK2")
    st.caption("Madurez de Gestión de Datos CVC | Baseline 2026 → Meta 2029")

    gd1, gd2, gd3, gd4 = st.columns(4)
    gd1.metric("Madurez promedio actual",  f"{mad_prom:.2f} / 5")
    gd2.metric("Areas en nivel 0",         str(len(dama_df[dama_df["Actual"]==0])))
    gd3.metric("Areas en nivel >= 2",      str(len(dama_df[dama_df["Actual"]>=2])))
    gd4.metric("Meta promedio 2029",       "3.0 / 5")

    # ── Radar de madurez DAMA ─────────────────────────────────────
    col_r, col_b = st.columns([1,1])

    with col_r:
        areas  = dama_df["Area"].tolist()
        actual = dama_df["Actual"].tolist()
        meta   = dama_df["Meta"].tolist()
        fig_dama_radar = go.Figure()
        fig_dama_radar.add_trace(go.Scatterpolar(
            r=actual + [actual[0]], theta=areas + [areas[0]],
            fill="toself", fillcolor="rgba(231,76,60,0.2)",
            line=dict(color="#e74c3c", width=2), name="Nivel actual 2026"))
        fig_dama_radar.add_trace(go.Scatterpolar(
            r=meta + [meta[0]], theta=areas + [areas[0]],
            fill="toself", fillcolor="rgba(46,204,113,0.1)",
            line=dict(color="#2ecc71", dash="dot", width=2), name="Meta 2029"))
        fig_dama_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0,5], gridcolor="#1e3a5f",
                                tickfont=dict(color="white")),
                angularaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="white", size=10)),
                bgcolor="#0d1b2a"),
            paper_bgcolor="#0d1b2a", font_color="white",
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            height=460, title="Madurez DAMA-DMBOK2 por Area")
        st.plotly_chart(fig_dama_radar, use_container_width=True)

    with col_b:
        fig_dama_bar = px.bar(
            dama_df.sort_values("Actual"),
            x="Actual", y="Area", orientation="h",
            color="Actual",
            color_continuous_scale=["#e74c3c","#e67e22","#f1c40f","#2ecc71","#3498db"],
            range_color=[0,5],
            text="Actual",
            labels={"Actual":"Nivel (0-5)", "Area":""},
            height=460,
            title="Nivel actual por area DAMA")
        fig_dama_bar.add_vline(x=3, line_dash="dash", line_color="#2ecc71",
                               annotation_text="Meta 2029", annotation_font_color="#2ecc71")
        fig_dama_bar.update_traces(textposition="outside")
        fig_dama_bar.update_layout(
            plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a", font_color="white",
            xaxis=dict(range=[0,5.5], gridcolor="#1e3a5f"),
            coloraxis_showscale=False,
            margin=dict(l=10,r=30,t=50,b=20))
        st.plotly_chart(fig_dama_bar, use_container_width=True)

    # ── KPIs de Gobernanza de Datos ───────────────────────────────
    st.subheader("KPIs del Programa de Gobernanza de Datos")

    kpis_gd = [
        ("Cobertura catalogo de datos",      0,  40, 70, 95,  "%"),
        ("Indice de calidad de datos",        0,   0, 80, 90,  "%"),
        ("Data Owners asignados",             0, 100,100,100,  "%"),
        ("Cumplimiento politica de acceso",   0,  80, 90,100,  "%"),
        ("Nivel madurez DAMA promedio",       1.18,1.5,2.0,3.0,"pts"),
        ("Reduccion incidentes de datos",     0,   0, 20, 40,  "%"),
    ]
    kpis_gd_df = pd.DataFrame(kpis_gd,
        columns=["KPI","Base_2026","Meta_2026","Meta_2027","Meta_2029","Unidad"])

    st.dataframe(kpis_gd_df, use_container_width=True, hide_index=True)

    # ── Roadmap de implementación ─────────────────────────────────
    st.subheader("Hoja de Ruta DAMA-DMBOK2 — 2026-2029")

    roadmap = [
        {"Hito":"Constituir DGC y DGO + Data Owners",
         "Inicio":"2026-01-01","Fin":"2026-03-31","Fase":"Fundacion","Prioridad":"Alta"},
        {"Hito":"Catalogo de datos v1.0 (50 activos)",
         "Inicio":"2026-03-01","Fin":"2026-06-30","Fase":"Fundacion","Prioridad":"Alta"},
        {"Hito":"Clasificacion de sensibilidad + Politica de acceso",
         "Inicio":"2026-04-01","Fin":"2026-07-31","Fase":"Proteccion","Prioridad":"Alta"},
        {"Hito":"Reglas de calidad + Dashboard calidad datos",
         "Inicio":"2026-06-01","Fin":"2026-09-30","Fase":"Calidad","Prioridad":"Alta"},
        {"Hito":"Glosario empresarial (100 terminos)",
         "Inicio":"2026-08-01","Fin":"2026-12-31","Fase":"Metadatos","Prioridad":"Media"},
        {"Hito":"Repositorio de datos maestros",
         "Inicio":"2027-01-01","Fin":"2027-06-30","Fase":"Integracion","Prioridad":"Media"},
        {"Hito":"Fuentes oficiales formalizadas + OpenMetadata",
         "Inicio":"2027-04-01","Fin":"2027-12-31","Fase":"Integracion","Prioridad":"Media"},
        {"Hito":"Data contracts para proyectos IA/IoT PETI",
         "Inicio":"2028-01-01","Fin":"2028-06-30","Fase":"Crecimiento","Prioridad":"Media"},
        {"Hito":"Modelo de datos empresarial CVC",
         "Inicio":"2028-06-01","Fin":"2029-12-31","Fase":"Optimizacion","Prioridad":"Baja"},
    ]
    roadmap_df = pd.DataFrame(roadmap)
    roadmap_df["Inicio"] = pd.to_datetime(roadmap_df["Inicio"])
    roadmap_df["Fin"]    = pd.to_datetime(roadmap_df["Fin"])

    COLORES_FASE = {
        "Fundacion":   "#3498db",
        "Proteccion":  "#e74c3c",
        "Calidad":     "#2ecc71",
        "Metadatos":   "#9b59b6",
        "Integracion": "#e67e22",
        "Crecimiento": "#1abc9c",
        "Optimizacion":"#f1c40f",
    }
    fig_road = px.timeline(
        roadmap_df, x_start="Inicio", x_end="Fin",
        y="Hito", color="Fase",
        color_discrete_map=COLORES_FASE,
        labels={"Hito":""}, height=500,
        title="Gantt — Hoja de Ruta Gobernanza de Datos")
    fig_road.update_yaxes(autorange="reversed", tickfont=dict(size=11))
    fig_road.update_xaxes(dtick="M3", tickformat="%b %Y",
                          range=["2025-10-01","2030-03-01"], gridcolor="#1e3a5f")
    fig_road.update_layout(
        plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
        font_color="white", legend_title_text="Fase",
        margin=dict(l=10,r=20,t=50,b=20))
    st.plotly_chart(fig_road, use_container_width=True)

    # ── Dominios de datos y Data Owners ──────────────────────────
    st.subheader("Dominios de Datos y Roles de Gobierno")

    dominios = [
        ("Datos Ambientales",      "Subdir. Gestion Ambiental", "Monitoreo cuencas, biodiversidad, calidad agua/aire",      "Confidencial"),
        ("Datos Geoespaciales",    "Jefe Grupo SIA / GeoCVC",   "Cartografia, geodatabase, coberturas territoriales",       "Publico"),
        ("Datos Financieros",      "Subdir. Administrativo",    "Presupuesto, ejecucion, contratos",                        "Confidencial"),
        ("Datos de TI",            "Jefe OTI",                  "Infraestructura, activos, indicadores COBIT/BSC",          "Interno"),
        ("Datos Ciudadanos",       "Jefe Juridica",             "PQRS, datos personales, servicios ciudadano",              "Reservado"),
        ("Datos Talento Humano",   "Jefe Talento Humano",       "Planta de personal, competencias, nomina",                 "Confidencial"),
        ("Datos Proyectos PETI",   "Jefe OTI + Planeacion",     "Portafolio, cronogramas, presupuesto TI",                  "Interno"),
    ]
    dom_df = pd.DataFrame(dominios,
        columns=["Dominio","Data Owner","Descripcion","Clasificacion"])

    COLORES_CLAS = {"Publico":"#2ecc71","Interno":"#3498db",
                    "Confidencial":"#e67e22","Reservado":"#e74c3c"}
    dom_df["Color"] = dom_df["Clasificacion"].map(COLORES_CLAS)

    fig_dom = px.bar(
        dom_df, x="Dominio", y=[1]*len(dom_df),
        color="Clasificacion",
        color_discrete_map=COLORES_CLAS,
        text="Data Owner",
        labels={"y":"","Dominio":""},
        height=300,
        title="Dominios de Datos por nivel de clasificacion")
    fig_dom.update_traces(textposition="inside", textfont_size=11)
    fig_dom.update_yaxes(visible=False)
    fig_dom.update_xaxes(tickangle=-20)
    fig_dom.update_layout(
        plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
        font_color="white", showlegend=True,
        margin=dict(l=10,r=10,t=50,b=60))
    st.plotly_chart(fig_dom, use_container_width=True)

    st.dataframe(dom_df[["Dominio","Data Owner","Clasificacion","Descripcion"]],
                 use_container_width=True, hide_index=True)

    # ── Dimensiones de calidad de datos ──────────────────────────
    st.subheader("Dimensiones de Calidad de Datos — Estado Actual")

    calidad_dims = [
        ("Completitud",  60, 98, "Expedientes con campos obligatorios completos"),
        ("Unicidad",     70, 99, "Ausencia de duplicados en datos maestros de titulares"),
        ("Validez",      75, 99, "Coordenadas geoespaciales dentro del territorio CVC"),
        ("Consistencia", 50, 98, "Coherencia financiera JD Edwards vs informes OTI"),
        ("Oportunidad",  65, 95, "Indicadores BSC actualizados antes del dia 10 de cada mes"),
        ("Exactitud",    55, 99, "Superficie areas protegidas vs actos administrativos"),
    ]
    cal_df = pd.DataFrame(calidad_dims,
        columns=["Dimension","Actual_%","Meta_%","Descripcion"])

    fig_cal = px.bar(
        cal_df, x="Dimension", y=["Actual_%","Meta_%"],
        barmode="group",
        color_discrete_map={"Actual_%":"#e74c3c","Meta_%":"#2ecc71"},
        text_auto=True,
        labels={"value":"Porcentaje","variable":"","Dimension":""},
        height=380,
        title="Calidad de Datos: Estado actual vs Meta por dimension")
    fig_cal.update_layout(
        plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
        font_color="white", xaxis=dict(gridcolor="#1e3a5f"),
        yaxis=dict(gridcolor="#1e3a5f", range=[0,110]),
        margin=dict(l=10,r=10,t=50,b=20))
    st.plotly_chart(fig_cal, use_container_width=True)

    caja_analisis(
        f"La CVC parte de un nivel de madurez DAMA promedio de <b>{mad_prom:.2f}/5</b>, "
        f"con <b>Metadatos en nivel 0</b> (inexistente) como brecha mas critica. "
        f"Las dimensiones de calidad de datos presentan brechas significativas: "
        f"Consistencia ({cal_df[cal_df.Dimension=='Consistencia']['Actual_%'].values[0]}%) "
        f"y Exactitud ({cal_df[cal_df.Dimension=='Exactitud']['Actual_%'].values[0]}%) son las mas rezagadas. "
        f"La hoja de ruta 2026-2029 prioriza fundacion y proteccion en el primer año "
        f"para alcanzar madurez DAMA 3.0 alineada con el nivel IT Governance actual."
    )


with tab_ia:

    # ════════════════════════════════════════════════════════════════
    #  PESTAÑA 3 — GOBIERNO DE IA
    # ════════════════════════════════════════════════════════════════

    st.subheader("Gobierno de IA — Hoja de Ruta CVC")
    st.caption("Marco: EU AI Act | NIST AI RMF | ISO 42001:2023 | ACM 2022 | UNESCO 2021 | ONU 2024 | CONPES 3975 | CONPES 4144 | Decreto 620/2020")

    # ── Clasificación del sistema ─────────────────────────────────
    ia1, ia2, ia3, ia4 = st.columns(4)
    ia1.metric("Clasificacion EU AI Act", "Riesgo Limitado")
    ia2.metric("Modelo LLM en uso",       "LLaMA 3.3-70b")
    ia3.metric("Proveedor API",           "Groq (gratuito)")
    ia4.metric("Nivel ISO 42001",         "En implementacion")

    # ── Evaluación AIA por principio ACM ─────────────────────────
    st.subheader("Evaluacion de Impacto Algoritmico (AIA) — Principios ACM")

    acm_data = [
        ("Legitimidad y competencia",      3, "Cumple",              "#2ecc71"),
        ("Minimizacion del dano",          2, "Cumple con controles","#e67e22"),
        ("Seguridad y privacidad",         3, "Cumple",              "#2ecc71"),
        ("Transparencia",                  2, "Cumple parcialmente", "#e67e22"),
        ("Interpretabilidad",              2, "Cumple parcialmente", "#e67e22"),
        ("Mantenibilidad",                 2, "Cumple con mejoras",  "#e67e22"),
        ("Auditabilidad",                  3, "Cumple",              "#2ecc71"),
        ("Rendicion de cuentas",           1, "Requiere formalizacion","#e74c3c"),
        ("Impacto ambiental",              1, "Requiere atencion",   "#e74c3c"),
    ]
    acm_df = pd.DataFrame(acm_data,
        columns=["Principio","Puntaje","Estado","Color"])

    col_acm1, col_acm2 = st.columns([1,1])

    with col_acm1:
        fig_acm = px.bar(
            acm_df, x="Puntaje", y="Principio", orientation="h",
            color="Estado",
            color_discrete_map={
                "Cumple":"#2ecc71",
                "Cumple con controles":"#e67e22",
                "Cumple parcialmente":"#e67e22",
                "Cumple con mejoras":"#e67e22",
                "Requiere formalizacion":"#e74c3c",
                "Requiere atencion":"#e74c3c",
            },
            text="Estado",
            labels={"Puntaje":"Nivel (0-3)","Principio":""},
            height=420,
            title="Cumplimiento principios ACM")
        fig_acm.add_vline(x=3, line_dash="dash", line_color="#2ecc71",
                          annotation_text="Meta", annotation_font_color="#2ecc71")
        fig_acm.update_traces(textposition="outside", textfont_size=10)
        fig_acm.update_layout(
            plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
            font_color="white", showlegend=False,
            xaxis=dict(range=[0,4.5], gridcolor="#1e3a5f"),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10,r=10,t=50,b=20))
        st.plotly_chart(fig_acm, use_container_width=True)

    with col_acm2:
        # Radar NIST AI RMF
        nist_funciones = ["GOVERN","MAP","MEASURE","MANAGE"]
        nist_actual    = [1, 2, 2, 1]
        nist_meta      = [4, 4, 4, 4]
        fig_nist = go.Figure()
        fig_nist.add_trace(go.Scatterpolar(
            r=nist_actual + [nist_actual[0]],
            theta=nist_funciones + [nist_funciones[0]],
            fill="toself", fillcolor="rgba(52,152,219,0.25)",
            line=dict(color="#3498db", width=2), name="Estado actual"))
        fig_nist.add_trace(go.Scatterpolar(
            r=nist_meta + [nist_meta[0]],
            theta=nist_funciones + [nist_funciones[0]],
            fill="toself", fillcolor="rgba(46,204,113,0.1)",
            line=dict(color="#2ecc71", dash="dot", width=2), name="Meta"))
        fig_nist.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0,5],
                                gridcolor="#1e3a5f", tickfont=dict(color="white")),
                angularaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="white", size=12)),
                bgcolor="#0d1b2a"),
            paper_bgcolor="#0d1b2a", font_color="white",
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            height=420, title="NIST AI RMF — Estado actual vs Meta")
        st.plotly_chart(fig_nist, use_container_width=True)

    # ── Mapa de riesgos IA ────────────────────────────────────────
    st.subheader("Mapa de Riesgos IA — NIST AI RMF")

    riesgos_ia = [
        ("G-1","Sin politica formal de IA",                  "Alta","Alto", "Aprobar politica uso responsable IA",          "GOVERN","NIST+ONU 2024"),
        ("G-2","Responsabilidad difusa sobre LLM",            "Media","Alto","Designar AI Officer mediante acto admin.",     "GOVERN","NIST+ACM"),
        ("G-3","Ausencia de voz unica institucional sobre IA","Media","Medio","OTI como unica dependencia autorizada para IA","GOVERN","ONU 2024"),
        ("M-1","Datos desactualizados en COBIT",              "Media","Alto","Ciclo actualizacion trimestral validado",      "MAP",   "NIST"),
        ("M-2","Uso fuera de contexto de diseno",             "Media","Alto","Disclaimer visible en dashboard",              "MAP",   "NIST+ACM"),
        ("M-3","Brecha digital CVC vs ecosistema global IA",  "Alta","Medio","Participar en redes SINA (IDEAM, ANLA, CAR)", "MAP",   "ONU 2024"),
        ("ME-1","Alucinaciones del LLM",                      "Media","Medio","Temperatura 0.3 + revision humana",           "MEASURE","NIST+ACM"),
        ("ME-2","Inconsistencia entre ejecuciones",           "Alta","Bajo", "Historial trazable en Google Sheets",          "MEASURE","NIST"),
        ("ME-3","Dependencia proveedor Groq",                 "Baja","Alto", "Alternativa Ollama local documentada",         "MEASURE","NIST"),
        ("ME-4","Huella ambiental del LLM",                   "Media","Medio","Modelos pequenos + documentar emisiones",     "MEASURE","ONU 2024+ACM"),
        ("MA-1","Deprecacion del modelo LLM",                 "Media","Medio","Monitoreo console.groq.com mensual",          "MANAGE","NIST"),
        ("MA-2","Acceso no autorizado al Sheet",              "Baja","Alto", "Restringir permisos a usuarios OTI",           "MANAGE","NIST"),
    ]
    riesgos_df = pd.DataFrame(riesgos_ia,
        columns=["ID","Riesgo","Probabilidad","Impacto","Mitigacion","Funcion_NIST","Marco"])

    PROB_NUM = {"Alta":3,"Media":2,"Baja":1}
    IMP_NUM  = {"Alto":3,"Medio":2,"Bajo":1}
    riesgos_df["Prob_n"] = riesgos_df["Probabilidad"].map(PROB_NUM)
    riesgos_df["Imp_n"]  = riesgos_df["Impacto"].map(IMP_NUM)
    riesgos_df["Score"]  = riesgos_df["Prob_n"] * riesgos_df["Imp_n"]

    fig_risk = px.scatter(
        riesgos_df,
        x="Prob_n", y="Imp_n",
        color="Funcion_NIST",
        size="Score", text="ID",
        hover_data={"Riesgo":True,"Mitigacion":True,"Prob_n":False,"Imp_n":False},
        labels={"Prob_n":"Probabilidad (1=Baja, 3=Alta)",
                "Imp_n":"Impacto (1=Bajo, 3=Alto)"},
        height=420,
        title="Mapa de Calor de Riesgos IA (NIST AI RMF)",
        color_discrete_map={
            "GOVERN":"#1abc9c","MAP":"#3498db",
            "MEASURE":"#e67e22","MANAGE":"#e74c3c"})
    fig_risk.add_shape(type="rect", x0=2.5,x1=3.5,y0=2.5,y1=3.5,
                       fillcolor="rgba(231,76,60,0.15)", line_width=0)
    fig_risk.add_shape(type="rect", x0=0.5,x1=2.5,y0=0.5,y1=2.5,
                       fillcolor="rgba(46,204,113,0.08)", line_width=0)
    fig_risk.update_traces(textposition="top center", textfont_size=10)
    fig_risk.update_layout(
        plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
        font_color="white",
        xaxis=dict(range=[0.5,3.5], dtick=1, gridcolor="#1e3a5f"),
        yaxis=dict(range=[0.5,3.5], dtick=1, gridcolor="#1e3a5f"),
        margin=dict(l=10,r=10,t=50,b=20))
    st.plotly_chart(fig_risk, use_container_width=True)

    with st.expander("Detalle de riesgos y mitigaciones"):
        st.dataframe(
            riesgos_df[["ID","Funcion_NIST","Marco","Riesgo","Probabilidad","Impacto","Mitigacion"]],
            use_container_width=True, hide_index=True)

    # ── Plan ISO 42001:2023 ───────────────────────────────────────
    st.subheader("Plan de Gobernanza ISO 42001:2023 — Objetivos AIMS")

    iso_objetivos = [
        ("OBJ-1","Disponibilidad del sistema >= 95%",               "Operacion",    2026, 95,  80,  "%"),
        ("OBJ-2","Reduccion tiempo informe TI: 5 dias -> 2 horas",  "Eficiencia",   2026, 100, 40,  "%"),
        ("OBJ-3","Nivel COBIT promedio: 1.4 -> 2.5 en 2029",        "Mejora",       2029, 2.5, 1.4, "pts"),
        ("OBJ-4","Aceptacion recomendaciones IA >= 60%",            "Calidad",      2027, 60,  0,   "%"),
        ("OBJ-5","Evaluacion impacto algoritmico anual completada",  "Cumplimiento", 2026, 100, 0,   "%"),
        ("OBJ-6","Reducir huella carbono IA 10% anual",             "Ambiental",    2027, 10,  0,   "%"),
        ("OBJ-7","Cero usos de IA fuera del proposito declarado",   "Integridad",   2026, 0,   0,   "incidentes"),
    ]
    iso_df = pd.DataFrame(iso_objetivos,
        columns=["ID","Objetivo","Categoria","Año_meta","Meta","Actual","Unidad"])

    fig_iso = px.bar(
        iso_df, x="ID",
        y=["Actual","Meta"],
        barmode="group",
        color_discrete_map={"Actual":"#e74c3c","Meta":"#2ecc71"},
        text_auto=True,
        labels={"value":"Valor","variable":"","ID":"Objetivo"},
        height=350,
        title="Objetivos AIMS — Estado actual vs Meta (ISO 42001:2023)")
    fig_iso.update_layout(
        plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a",
        font_color="white",
        xaxis=dict(gridcolor="#1e3a5f"),
        yaxis=dict(gridcolor="#1e3a5f"),
        margin=dict(l=10,r=10,t=50,b=20))
    st.plotly_chart(fig_iso, use_container_width=True)

    st.dataframe(
        iso_df[["ID","Objetivo","Categoria","Año_meta","Actual","Meta","Unidad"]],
        use_container_width=True, hide_index=True)

    # ── Métricas de fairness ──────────────────────────────────────
    st.subheader("Metricas de Fairness e ISO/IEC 42001")

    fairness = [
        ("F-1","Consistencia de resultados",             "Harvard",   80, 100, "%",  "Variacion nivel COBIT entre ejecuciones <= 0.1"),
        ("F-2","Cobertura de dominios COBIT",            "Harvard",   40, 100, "%",  "Todos los dominios mencionados en cada analisis"),
        ("F-3","Proporcionalidad de recomendaciones",    "Harvard",   60, 100, "%",  "100% procesos nivel 0 en plan de accion"),
        ("F-4","Equidad en beneficio institucional",     "ONU 2024",  30, 100, "%",  "Recomendaciones que benefician a todas las areas CVC"),
        ("M-1","Tasa aceptacion recomendaciones IA",     "ISO 42001",  0,  60, "%",  "Recomendaciones implementadas / generadas"),
        ("M-2","Tiempo generacion analisis",             "ISO 42001",  5,   2, "min","Desde trigger hasta resultado en Sheets"),
        ("M-3","Disponibilidad del sistema",             "ISO 42001", 80,  95, "%",  "Ejecuciones exitosas / intentos totales"),
        ("M-4","Antiguedad datos diagnostico",           "ISO 42001",180,  90, "dias","Dias desde ultima actualizacion COBIT"),
        ("M-5","Satisfaccion usuario Jefe OTI",          "ISO 42001",  0,   4, "1-5","Valoracion utilidad analisis generados"),
        ("M-6","Cobertura dominios COBIT en analisis",   "ISO 42001",  0, 100, "%",  "% dominios (EDM/APO/BAI/DSS/MEA) mencionados"),
        ("M-7","Huella carbono por ejecucion",           "ACM+ONU",    0,   0, "gCO2","Documentar y reducir 10% anual"),
    ]
    fair_df = pd.DataFrame(fairness,
        columns=["ID","Metrica","Marco","Actual","Meta","Unidad","Descripcion"])

    col_f1, col_f2 = st.columns([2,1])
    with col_f1:
        st.dataframe(
            fair_df[["ID","Marco","Metrica","Actual","Meta","Unidad","Descripcion"]],
            use_container_width=True, hide_index=True)
    with col_f2:
        fig_fair = px.scatter(
            fair_df,
            x="Actual", y="Meta",
            color="Marco", text="ID",
            labels={"Actual":"Valor actual","Meta":"Valor meta"},
            height=380,
            title="Actual vs Meta — Fairness",
            color_discrete_map={"Harvard":"#3498db","ISO 42001":"#2ecc71"})
        max_val = fair_df[["Actual","Meta"]].max().max()
        fig_fair.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val,
                           line=dict(color="white", dash="dot", width=1))
        fig_fair.update_traces(textposition="top center", textfont_size=10)
        fig_fair.update_layout(
            plot_bgcolor="#0d1b2a", paper_bgcolor="#0d1b2a", font_color="white",
            margin=dict(l=10,r=10,t=50,b=20))
        st.plotly_chart(fig_fair, use_container_width=True)

    caja_analisis(
        "El sistema COBIT-AI de la CVC esta clasificado como <b>Riesgo Limitado</b> bajo el EU AI Act (Art. 50), "
        "con obligaciones de transparencia activas. "
        "Segun el Informe ONU 2024, Colombia pertenece al grupo de 118 paises del Sur Global sin representacion "
        "plena en los foros globales de gobernanza de IA — la CVC puede contribuir a cerrar esta brecha implementando "
        "buenas practicas replicables en el sector ambiental publico. "
        "Los riesgos mas criticos (NIST AI RMF) son la ausencia de politica formal (G-1), "
        "la responsabilidad difusa sobre el LLM (G-2) y la falta de voz unica institucional (G-3). "
        "Se incorporan 3 nuevos riesgos derivados del informe ONU: brecha digital (M-3), huella ambiental (ME-4) "
        "y 2 nuevos objetivos AIMS: reduccion de carbono (OBJ-6) y cero usos fuera de proposito (OBJ-7). "
        "El CONPES 4144 refuerza la necesidad de articular el sistema con el SIAC y los estandares de datos "
        "abiertos del sector ambiental colombiano. "
        "Accion prioritaria: aprobar la Politica de Uso Responsable de IA como primer acto administrativo del programa."
    )