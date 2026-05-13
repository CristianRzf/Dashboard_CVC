import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
 
# Verificar archivos antes de cargar
archivos = {
    "kpis": "datos/kpis_bsc.xlsx",
    "proyectos": "datos/proyectos_peti.xlsx",
    "calor": "datos/matriz_calor.xlsx",
    "madurez": "datos/madurez_digital.xlsx"
}
 
for nombre, ruta in archivos.items():
    if not os.path.exists(ruta):
        print(f"Error: No se encuentra el archivo {ruta}")
        exit(1)
    else:
        print(f"Archivo encontrado: {ruta}")
 
# Cargar datos
kpis = pd.read_excel(archivos["kpis"])
proyectos = pd.read_excel(archivos["proyectos"])
calor = pd.read_excel(archivos["calor"])
madurez = pd.read_excel(archivos["madurez"])
 
# ============================================
# CONVERTIR COLUMNAS A NÚMEROS
# ============================================
for col in ["Valor", "Target"]:
    if col in kpis.columns:
        kpis[col] = pd.to_numeric(kpis[col], errors="coerce")
 
for col in ["Puntaje"]:
    if col in madurez.columns:
        madurez[col] = pd.to_numeric(madurez[col], errors="coerce")
 
for col in ["Puntuación"]:
    if col in calor.columns:
        calor[col] = pd.to_numeric(calor[col], errors="coerce")
 
for col in ["Presupuesto_MCOP"]:
    if col in proyectos.columns:
        proyectos[col] = pd.to_numeric(proyectos[col], errors="coerce")
 
print("Datos cargados y convertidos correctamente")
 
# ============================================
# 1. Gráfico de KPIs 2026 (barras)
# ============================================
kpis_2026 = kpis[kpis["Año"] == 2026].copy()
# Filtrar solo KPIs numéricos
kpis_numericos = kpis_2026[~kpis_2026["KPI"].str.contains("madurez|MSPI|fuentes|procesos|IA", case=False, na=False)]
kpis_numericos = kpis_numericos.dropna(subset=["Valor", "Target"])
 
if not kpis_numericos.empty:
    fig_kpis = px.bar(kpis_numericos, x="Valor", y="KPI", color="Perspectiva",
                      title="KPIs 2026 - Valor vs Meta",
                      text_auto='.0%', labels={"Valor": "", "KPI": ""})
    
    for i, row in kpis_numericos.iterrows():
        fig_kpis.add_annotation(x=row["Target"] + 0.02, y=row["KPI"], 
                                text=f"Meta: {row['Target']:.0%}", showarrow=False,
                                font=dict(size=10))
else:
    fig_kpis = go.Figure()
    fig_kpis.add_annotation(text="No hay datos numéricos de KPIs para 2026", x=0.5, y=0.5, showarrow=False)
 
# ============================================
# 2. Balanced Scorecard (Barras por año)
# ============================================
kpis_numericos_todos = kpis[~kpis["KPI"].str.contains("madurez|MSPI|fuentes|procesos|IA", case=False, na=False)]
kpis_numericos_todos = kpis_numericos_todos.dropna(subset=["Valor"])
 
if not kpis_numericos_todos.empty:
    fig_bsc = px.bar(kpis_numericos_todos, x="Año", y="Valor", color="KPI", 
                     facet_col="Perspectiva",
                     title="Balanced Scorecard 2026-2029", barmode="group",
                     labels={"Valor": "Valor (%)", "KPI": "Indicador"})
else:
    fig_bsc = go.Figure()
    fig_bsc.add_annotation(text="Datos de BSC no disponibles", x=0.5, y=0.5, showarrow=False)
 
# ============================================
# 3. Mapa de calor (Excel ya limpio)
# ============================================
if "Proceso" in calor.columns and "Área" in calor.columns and "Puntuación" in calor.columns:
    calor["Puntuación"] = pd.to_numeric(calor["Puntuación"], errors="coerce")

    pivot = calor.groupby(["Área", "Proceso"])["Puntuación"].max().reset_index()

    # Área en filas (9), Proceso en columnas (4)
    pivot = pivot.pivot(index="Área", columns="Proceso", values="Puntuación")

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

    pivot = pivot.reindex(index=orden_filas).reindex(columns=orden_cols)

    fig_heat = px.imshow(
        pivot, text_auto=True, color_continuous_scale="RdYlGn",
        title="Mapa de Calor – Priorización Digital (0-9)",
        aspect="auto", zmin=0, zmax=9,
        labels={"x": "Iniciativa Digital", "y": "Área Organizacional", "color": "Puntuación"},
    )
    fig_heat.update_xaxes(tickangle=0, tickfont=dict(size=11), side="top")
    fig_heat.update_yaxes(tickfont=dict(size=11))
    fig_heat.update_layout(height=500, margin=dict(l=300, r=40, t=160, b=40))
else:
    fig_heat = go.Figure()
    fig_heat.add_annotation(text="Datos de mapa de calor no disponibles", x=0.5, y=0.5, showarrow=False)

# ============================================
# 4. Madurez digital
# ============================================
if "Pregunta_ID" in madurez.columns and "Puntaje" in madurez.columns:
    madurez_clean = madurez.dropna(subset=["Puntaje"])
    if not madurez_clean.empty:
        fig_mad = px.bar(madurez_clean, x="Pregunta_ID", y="Puntaje", color="Dimensión",
                         title="Madurez Digital - Resultados del cuestionario",
                         labels={"Puntaje": "Puntuación (1-3)", "Pregunta_ID": "Pregunta"})
        fig_mad.add_hline(y=1.5, line_dash="dash", line_color="red", annotation_text="Umbral bajo")
        fig_mad.add_hline(y=2.5, line_dash="dash", line_color="green", annotation_text="Umbral alto")
    else:
        fig_mad = go.Figure()
        fig_mad.add_annotation(text="Datos de madurez digital vacíos", x=0.5, y=0.5, showarrow=False)
else:
    fig_mad = go.Figure()
    fig_mad.add_annotation(text="Datos de madurez digital no disponibles", x=0.5, y=0.5, showarrow=False)
 
# ============================================
# 5. Portafolio Gantt
# ============================================
if "Inicio" in proyectos.columns and "Fin" in proyectos.columns:
    proyectos["Inicio_dt"] = pd.to_datetime(proyectos["Inicio"], format="%Y", errors="coerce")
    proyectos["Fin_dt"] = pd.to_datetime(proyectos["Fin"], format="%Y", errors="coerce")
    proyectos = proyectos.dropna(subset=["Inicio_dt", "Fin_dt"])
    
    if not proyectos.empty:
        fig_gantt = px.timeline(proyectos, x_start="Inicio_dt", x_end="Fin_dt", y="Nombre",
                                 color="Prioridad", title="Portafolio PETI 2026-2029")
        fig_gantt.update_yaxes(autorange="reversed")
    else:
        fig_gantt = go.Figure()
        fig_gantt.add_annotation(text="No hay proyectos con fechas válidas", x=0.5, y=0.5, showarrow=False)
else:
    fig_gantt = go.Figure()
    fig_gantt.add_annotation(text="Datos de proyectos no disponibles", x=0.5, y=0.5, showarrow=False)
 
# ============================================
# Guardar todos los gráficos en un solo HTML
# ============================================
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Estratégico CVC</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f0f2f6; }}
        h1 {{ color: #2c3e50; text-align: center; }}
        h3 {{ color: #34495e; margin-top: 30px; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        .container {{ max-width: 1400px; margin: auto; }}
        .footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #7f8c8d; }}
    </style>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>Dashboard Estratégico de TI – CVC</h1>
        <p style="text-align: center">Corporación Autónoma Regional del Valle del Cauca | 2026-2029</p>
        
        <h3>Indicadores Clave 2026</h3>
        <div id="kpis"></div>
        
        <h3>Balanced Scorecard 2026-2029</h3>
        <div id="bsc"></div>
        
        <h3>Mapa de Calor – Vacíos Digitales</h3>
        <div id="heatmap"></div>
        
        <h3>Madurez Digital</h3>
        <div id="madurez"></div>
        
        <h3>Portafolio PETI – Hoja de Ruta</h3>
        <div id="gantt"></div>
        
        <div class="footer">
            <p>Fuente: PETI CVC 2026-2029, análisis DOFA, BSC y matriz de madurez digital</p>
        </div>
    </div>
    <script>
        const kpis = {fig_kpis.to_json()};
        const bsc = {fig_bsc.to_json()};
        const heatmap = {fig_heat.to_json()};
        const madurez = {fig_mad.to_json()};
        const gantt = {fig_gantt.to_json()};
        
        Plotly.newPlot('kpis', kpis.data, kpis.layout, {{responsive: true}});
        Plotly.newPlot('bsc', bsc.data, bsc.layout, {{responsive: true}});
        Plotly.newPlot('heatmap', heatmap.data, heatmap.layout, {{responsive: true}});
        Plotly.newPlot('madurez', madurez.data, madurez.layout, {{responsive: true}});
        Plotly.newPlot('gantt', gantt.data, gantt.layout, {{responsive: true}});
    </script>
</body>
</html>
"""
 
# Guardar archivo HTML
with open("dashboard_cvc.html", "w", encoding="utf-8") as f:
    f.write(html_content)
 
print("\n" + "="*50)
print("Dashboard guardado como 'dashboard_cvc.html'")
print("Puedes abrir este archivo en tu navegador")
print("Para publicar en GitHub Pages, renombra a index.html")
print("="*50)