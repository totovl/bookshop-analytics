import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="BookShop Analytics | Dashboard de Portafolio",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# 1. ESTILOS CSS PERSONALIZADOS (Aesthetics & Glassmorphism)
# =============================================================================
st.markdown("""
<style>
    /* Fondo principal y textos */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Contenedores con efecto Glassmorphism */
    div.css-1r6g82t, div.stCard, .metric-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    div.metric-card:hover {
        border-color: rgba(0, 173, 181, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(0, 173, 181, 0.15);
    }
    
    /* Estilo de los KPI */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #00ADB5;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #94A3B8;
        margin-bottom: 8px;
    }
    .metric-delta-up {
        font-size: 0.85rem;
        color: #10B981;
        font-weight: 600;
    }
    .metric-delta-down {
        font-size: 0.85rem;
        color: #EF4444;
        font-weight: 600;
    }
    .metric-delta-neutral {
        font-size: 0.85rem;
        color: #94A3B8;
        font-weight: 600;
    }

    /* Modificaciones estéticas de Streamlit */
    .stButton>button {
        background-color: #00ADB5 !important;
        color: #F8FAFC !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background-color: #00E8C6 !important;
        box-shadow: 0 0 15px rgba(0, 232, 198, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 2. CARGA Y LIMPIEZA DE DATOS
# =============================================================================
@st.cache_data
def load_data():
    # Leer el archivo CSV local
    df = pd.read_csv("ventas_libreria_completo.csv")
    
    # Limpieza de fechas
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Año_Mes"] = df["Fecha"].dt.to_period("M").astype(str)
    df["Dia_Semana"] = df["Fecha"].dt.day_name()
    df["Dia_Semana_N"] = df["Fecha"].dt.weekday  # 0=Lunes, 6=Domingo
    
    # Mapeo de días de la semana a español
    dias_es = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
    }
    df["Dia_Semana_ES"] = df["Dia_Semana"].map(dias_es)
    
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"Error al cargar el archivo de datos 'ventas_libreria_completo.csv': {e}")
    st.info("Asegúrate de haber ejecutado el script 'generar_ventas_libreria.py' previamente para generar el dataset.")
    st.stop()

# =============================================================================
# 3. SIDEBAR - FILTROS INTERACTIVOS
# =============================================================================
st.sidebar.markdown("<h2 style='color:#00ADB5; text-align:center;'>🎛️ Panel de Filtros</h2>", unsafe_allow_html=True)

# --- Selector Dinámico de Moneda ---
st.sidebar.subheader("💱 Moneda y Cotización")
moneda = st.sidebar.selectbox("Selecciona la moneda:", options=["ARS", "USD"], index=0)
tipo_cambio_usd_ars = st.sidebar.number_input("Cotización USD a ARS:", value=1550.0, min_value=1.0, step=10.0)
simbolo_moneda = "$" if moneda == "ARS" else "US$"

# Crear campo calculado dinámico para la moneda
df_raw["Total_Transaccion_Calc"] = np.where(
    moneda == "ARS", 
    df_raw["Total_Transaccion"] * tipo_cambio_usd_ars, 
    df_raw["Total_Transaccion"]
)

st.sidebar.write("Ajusta las variables de negocio para analizar el comportamiento:")

# Filtro 1: Selector de Rango de Fechas
min_date = df_raw["Fecha"].min().date()
max_date = df_raw["Fecha"].max().date()

st.sidebar.subheader("📅 Período de Análisis")
date_range = st.sidebar.date_input(
    "Selecciona el rango de fechas:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filtro 2: Selector de Géneros Literarios (Multi-filtro)
st.sidebar.subheader("📚 Categorías Literarias")
all_genres = sorted(df_raw["Genero"].unique())
selected_genres = st.sidebar.multiselect(
    "Filtrar por Géneros:",
    options=all_genres,
    default=all_genres
)

# Filtro 3: Selector de Métodos de Pago
st.sidebar.subheader("💳 Métodos de Pago")
all_payments = sorted(df_raw["Metodo_Pago"].unique())
selected_payments = st.sidebar.multiselect(
    "Filtrar por Canal de Pago:",
    options=all_payments,
    default=all_payments
)

# Resetear Filtros
if st.sidebar.button("Restablecer todos los filtros"):
    st.rerun()

# ── Aplicar Filtros al Dataset ───────────────────────────────────────────────
# Control de seguridad para el rango de fechas
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_date, end_date = pd.to_datetime(min_date), pd.to_datetime(max_date)

df_filtered = df_raw[
    (df_raw["Fecha"] >= start_date) & 
    (df_raw["Fecha"] <= end_date) &
    (df_raw["Genero"].isin(selected_genres)) &
    (df_raw["Metodo_Pago"].isin(selected_payments))
]

# Mensaje si no hay datos que coincidan
if df_filtered.empty:
    st.warning("⚠️ No hay transacciones que coincidan con la selección de filtros actual. Por favor amplía los filtros.")
    st.stop()

# =============================================================================
# 4. CÁLCULO DE MÉTRICAS (Presente vs Histórico/Pasado)
# =============================================================================
# Para calcular deltas correctos, definimos el período anterior con la misma duración
días_seleccionados = (end_date - start_date).days + 1
start_prev = start_date - timedelta(days=días_seleccionados)
end_prev = start_date - timedelta(days=1)

# Dataset histórico del mismo tamaño de ventana
df_prev = df_raw[
    (df_raw["Fecha"] >= start_prev) & 
    (df_raw["Fecha"] <= end_prev) &
    (df_raw["Genero"].isin(selected_genres)) &
    (df_raw["Metodo_Pago"].isin(selected_payments))
]

def calculate_kpis(df):
    ingresos = df["Total_Transaccion_Calc"].sum()
    unidades = df["Cantidad"].sum()
    transacciones = df["ID_Transaccion"].nunique()
    ticket_promedio = ingresos / transacciones if transacciones > 0 else 0
    return ingresos, unidades, transacciones, ticket_promedio

ingresos_act, unidades_act, txns_act, ticket_act = calculate_kpis(df_filtered)
ingresos_prev, unidades_prev, txns_prev, ticket_prev = calculate_kpis(df_prev)

# Función para dar formato al delta (%)
def get_delta_str(act, prev, is_currency=False):
    if prev == 0:
        return "N/A", "neutral"
    pct_change = ((act - prev) / prev) * 100
    sign = "+" if pct_change >= 0 else ""
    formatted_pct = f"{sign}{pct_change:.1f}%"
    status = "up" if pct_change > 0 else ("down" if pct_change < 0 else "neutral")
    return formatted_pct, status

delta_ingresos, status_ingresos = get_delta_str(ingresos_act, ingresos_prev)
delta_unidades, status_unidades = get_delta_str(unidades_act, unidades_prev)
delta_ticket, status_ticket = get_delta_str(ticket_act, ticket_prev)
delta_txns, status_txns = get_delta_str(txns_act, txns_prev)

# Determinar Género Líder en ventas
genero_lider_series = df_filtered.groupby("Genero")["Total_Transaccion_Calc"].sum()
if not genero_lider_series.empty:
    genero_lider = genero_lider_series.idxmax()
    genero_lider_monto = genero_lider_series.max()
    porcentaje_lider = (genero_lider_monto / ingresos_act) * 100
else:
    genero_lider, porcentaje_lider = "N/A", 0

# Libro más vendido
libro_lider_series = df_filtered.groupby("Titulo")["Cantidad"].sum()
libro_lider = libro_lider_series.idxmax() if not libro_lider_series.empty else "N/A"
libro_lider_cant = libro_lider_series.max() if not libro_lider_series.empty else 0

# =============================================================================
# 5. RENDERIZADO DEL DASHBOARD (Layout Principal)
# =============================================================================
st.markdown("<h1 style='text-align: center; color: #F8FAFC; margin-bottom: 0;'>📈 Dashboard BookShop Analytics</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 1.1rem; margin-bottom: 30px;'>Demo de portafolio para toma de decisiones comerciales y operativas en retail de libros</p>", unsafe_allow_html=True)

# ── SECCIÓN A: KPI CARDS (Métricas del Presente y Salud del Negocio) ─────────
st.subheader("💡 Salud Financiera y Operativa Actual")

col1, col2, col3, col4, col5, col6 = st.columns(6)

def render_custom_card(col, title, value, delta, status, subtext=""):
    delta_class = "metric-delta-up" if status == "up" else ("metric-delta-down" if status == "down" else "metric-delta-neutral")
    delta_arrow = "▲" if status == "up" else ("▼" if status == "down" else "•")
    
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div style="margin-top: 8px;">
                <span class="{delta_class}">{delta_arrow} {delta}</span>
                <span style="color: #64748B; font-size: 0.75rem;"> vs. período ant.</span>
            </div>
            {f'<div style="color: #00ADB5; font-size: 0.75rem; font-weight:600; margin-top:4px;">{subtext}</div>' if subtext else ''}
        </div>
        """, unsafe_allow_html=True)

render_custom_card(col1, "Ingresos Totales", f"{simbolo_moneda} {ingresos_act:,.2f}", delta_ingresos, status_ingresos)
render_custom_card(col2, "Unidades Vendidas", f"{unidades_act:,}", delta_unidades, status_unidades)
render_custom_card(col3, "Ticket Promedio", f"{simbolo_moneda} {ticket_act:.2f}", delta_ticket, status_ticket)
render_custom_card(col4, "Transacciones", f"{txns_act:,}", delta_txns, status_txns)
render_custom_card(col5, "Categoría Líder", genero_lider, f"{porcentaje_lider:.1f}%", "neutral", "Participación Ventas")
render_custom_card(col6, "Bestseller Período", libro_lider, f"{libro_lider_cant} uds", "up", "Reposición Activa")

st.markdown("<br>", unsafe_allow_html=True)

# ── SECCIÓN B: VISUALIZACIONES PRINCIPALES (Evolución, Reposición y Canales) ──
col_left, col_right = st.columns([2, 1.2])

with col_left:
    # A) "Evolución y Destino": Gráfico de Líneas Temporal Multivariable
    st.subheader("📈 Evolución Temporal por Género Literario")
    
    # Agrupamos por mes y por género
    df_temporal = df_filtered.groupby(["Año_Mes", "Genero"])["Total_Transaccion_Calc"].sum().reset_index()
    
    fig_lineas = px.line(
        df_temporal,
        x="Año_Mes",
        y="Total_Transaccion_Calc",
        color="Genero",
        title="Facturación Mensual Acumulada por Categoría",
        labels={"Año_Mes": "Mes", "Total_Transaccion_Calc": f"Ingresos ({moneda})", "Genero": "Categoría"},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig_lineas.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickangle=-30),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="left", x=0),
        height=480
    )
    st.plotly_chart(fig_lineas, use_container_width=True)

with col_right:
    # C) "Distribución de Canales": Distribución de Ventas por Método de Pago
    st.subheader("💳 Canales y Comisiones Financieras")
    
    # Agrupar transacciones y montos por método de pago
    df_pagos = df_filtered.groupby("Metodo_Pago").agg(
        Transacciones=("ID_Transaccion", "count"),
        Monto=("Total_Transaccion_Calc", "sum")
    ).reset_index()
    
    # Añadir columna de comisiones estimadas reales de pasarelas de pago
    # Efectivo: 0%, MP: 3.5%, Tarjeta Crédito: 2.5%, Tarjeta Débito: 1.2%, Transferencia: 0.1%
    comisiones_dict = {
        "Efectivo": 0.00,
        "Mercado Pago": 0.035,
        "Tarjeta de Crédito": 0.025,
        "Tarjeta de Débito": 0.012,
        "Transferencia": 0.001
    }
    df_pagos["Comision_Estimada"] = df_pagos["Monto"] * df_pagos["Metodo_Pago"].map(comisiones_dict)
    total_comision = df_pagos["Comision_Estimada"].sum()
    
    fig_donut = px.pie(
        df_pagos,
        names="Metodo_Pago",
        values="Monto",
        hole=0.45,
        title="Ingresos según Canal de Cobro",
        color_discrete_sequence=px.colors.sequential.Tealgrn_r
    )
    
    fig_donut.update_traces(
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        marker=dict(line=dict(color="#0F172A", width=2))
    )
    
    fig_donut.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=False,
        height=380,
        annotations=[
            dict(
                text=f"Fuga Comisiones:<br><b>{simbolo_moneda} {total_comision:,.1f}</b>",
                showarrow=False,
                font=dict(size=14, color="#EF4444")
            )
        ]
    )
    st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown(f"""
    💡 **Análisis de pasarelas**: Se estiman pérdidas de **{simbolo_moneda} {total_comision:,.2f}** por aranceles bancarios. 
    *Tip de Negocio*: Incentivar Transferencias bancarias y Efectivo para reducir el impacto financiero.
    """)

# ── SECCIÓN C: STOCK Y LOGÍSTICA (B — Reposición Prioritaria) ─────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🛒 Operaciones e Inventario: Decisiones de Compra Directa")

col_bar, col_insights = st.columns([2.2, 1])

with col_bar:
    # B) "Decisión de Compra Directa": Top 20 Libros Más Vendidos
    # Obtener el top 20 por unidades vendidas
    df_top_books = df_filtered.groupby(["Titulo", "Genero"])["Cantidad"].sum().reset_index()
    df_top_books = df_top_books.sort_values(by="Cantidad", ascending=True).tail(20) # Para horizontal se grafica al revés
    
    fig_barras = px.bar(
        df_top_books,
        x="Cantidad",
        y="Titulo",
        color="Genero",
        orientation="h",
        title="Top 20 Libros con Mayor Demanda en Período Seleccionado",
        labels={"Cantidad": "Unidades Vendidas", "Titulo": "Título del Libro", "Genero": "Categoría"},
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    
    fig_barras.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", dtick=1),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="left", x=0),
        height=550
    )
    st.plotly_chart(fig_barras, use_container_width=True)

with col_insights:
    st.markdown("### 📋 Sugerencia de Reposición Prioritaria (Stock de Seguridad)")
    st.write("""
    Esta lista representa los títulos reales de alta rotación que corren riesgo de quiebre de stock (*out of stock*). 
    Debes emitir órdenes de compra prioritarias para el Top 5 de esta lista.
    """)
    
    # Presentar tabla accionable
    df_top_table = df_top_books.sort_values(by="Cantidad", ascending=False).head(10)[["Titulo", "Genero", "Cantidad"]]
    df_top_table.columns = ["Título", "Categoría", "Uds. Vendidas"]
    
    st.dataframe(
        df_top_table,
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("""
    > 💡 **Regla de Oro en Retail**: Aplica un factor de **1.5x de stock de seguridad** para el Bestseller actual en meses estacionales (Noviembre/Diciembre) para evitar dejar dinero sobre la mesa.
    """)

# =============================================================================
# 6. SECCIÓN INNOVADORA - ANALÍTICA PREDICTIVA Y TENDENCIAS MoM
# =============================================================================
st.markdown("<br><hr style='border: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
st.subheader("🔮 Análisis de Tendencias Trimestrales (Hacia dónde va el negocio)")

# Lógica para análisis MoM (Month over Month) de tendencias recientes
# Agrupamos facturación por mes y género para calcular el histórico
df_mom = df_raw.groupby(["Año_Mes", "Genero"])["Total_Transaccion_Calc"].sum().reset_index()

# Pivotamos para tener meses como filas y géneros como columnas
pivot_mom = df_mom.pivot(index="Año_Mes", columns="Genero", values="Total_Transaccion_Calc").fillna(0)

# Calcular tasa de crecimiento MoM para todos los meses (porcentaje de cambio)
mom_growth = pivot_mom.pct_change(fill_method=None) * 100

# Tomar los últimos 3 meses del dataset histórico general para evaluar la tendencia reciente
# (Nota: El dataset termina en Junio 2026, así que evaluamos Abril, Mayo y Junio 2026)
ultimos_meses = pivot_mom.index[-3:].tolist()

if len(pivot_mom) >= 3:
    # Crecimiento promedio del último trimestre
    crecimiento_trimestral = mom_growth.iloc[-3:].mean().reset_index()
    crecimiento_trimestral.columns = ["Género", "Crecimiento Promedio MoM (%)"]
    
    # Clasificación de tendencia
    def clasificar_tendencia(pct):
        if pct > 1.5:
            return "🟢 Crecimiento Rápido (Invertir)"
        elif pct < -1.5:
            return "🔴 Declive Sostenido (Liquidar)"
        else:
            return "🟡 Estable (Mantener)"
            
    crecimiento_trimestral["Recomendación Operativa"] = crecimiento_trimestral["Crecimiento Promedio MoM (%)"].apply(clasificar_tendencia)
    crecimiento_trimestral = crecimiento_trimestral.sort_values(by="Crecimiento Promedio MoM (%)", ascending=False)
    
    col_table, col_pred_insights = st.columns([1.5, 1])
    
    with col_table:
        st.markdown("#### Tasa de Crecimiento Mensual Reciente por Género (Último Trimestre)")
        st.write("Crecimiento mensual promedio evaluado sobre los meses de: " + ", ".join(ultimos_meses))
        
        # Mostrar tabla estilizada con barras internas de crecimiento
        st.dataframe(
            crecimiento_trimestral.style.format({"Crecimiento Promedio MoM (%)": "{:,.2f}%"}).background_gradient(
                cmap="RdYlGn", subset=["Crecimiento Promedio MoM (%)"]
            ),
            use_container_width=True,
            hide_index=True
        )
        
    with col_pred_insights:
        st.markdown("#### 🎯 Decisiones Presupuestarias y Alertas")
        
        genero_top_growth = crecimiento_trimestral.iloc[0]["Género"]
        tasa_top = crecimiento_trimestral.iloc[0]["Crecimiento Promedio MoM (%)"]
        
        genero_low_growth = crecimiento_trimestral.iloc[-1]["Género"]
        tasa_low = crecimiento_trimestral.iloc[-1]["Crecimiento Promedio MoM (%)"]
        
        st.info(f"""
        🚀 **ALERTA DE OPORTUNIDAD: CATEGORÍA EN ASCENSO**  
        **{genero_top_growth}** está liderando la aceleración trimestral con una tasa de crecimiento mensual promedio del **{tasa_top:.2f}%**.  
        *Acción*: Asignar un **15% extra del presupuesto de compras** a novedades de este género para capturar la tendencia de mercado.
        """)
        
        st.error(f"""
        ⚠️ **ALERTA DE RIESGO: CATEGORÍA PERDIENDO TERRENO**  
        **{genero_low_growth}** muestra la mayor contracción con un retroceso promedio de **{tasa_low:.2f}%** mensual.  
        *Acción*: Frenar compras de fondo de catálogo de este género y realizar campañas de **liquidación/promociones** para liberar capital de trabajo inmovilizado.
        """)
else:
    st.info("El análisis de tendencias MoM requiere al menos 3 meses de historial en la selección temporal.")

# Heatmap de Estacionalidad de Ventas (Extra analítico de alto impacto)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"#### 🗺️ Mapa de Calor Mensual (Ventas en {moneda} por Género)")
st.write("Identifica picos y ciclos estacionales de ventas para planificar campañas de marketing y stock mínimo.")

# Armar datos para heatmap
heatmap_data = pivot_mom.T  # Géneros en filas, meses en columnas
fig_heatmap = px.imshow(
    heatmap_data,
    labels=dict(x="Mes", y="Género Literario", color=f"Ventas ({moneda})"),
    x=heatmap_data.columns,
    y=heatmap_data.index,
    color_continuous_scale="Viridis",
    aspect="auto"
)
fig_heatmap.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#F8FAFC"),
    margin=dict(l=10, r=10, t=30, b=10),
    height=400
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# =============================================================================
# 7. SECCIÓN ADICIONAL - ANÁLISIS DE NEGOCIO AVANZADO (Métricas del Librero)
# =============================================================================
st.markdown("<br><hr style='border: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
st.subheader("📊 Análisis de Valor Comercial y Pareto del Catálogo")

col_pareto, col_dias = st.columns([1.2, 1])

with col_pareto:
    st.markdown("#### 🎯 Regla de Pareto (80/20) del Portafolio")
    st.write("¿Qué proporción de los títulos representa el 80% de los ingresos totales de la librería?")
    
    # Calcular Pareto
    df_pareto = df_filtered.groupby("Titulo")["Total_Transaccion_Calc"].sum().sort_values(ascending=False).reset_index()
    df_pareto["Acumulado"] = df_pareto["Total_Transaccion_Calc"].cumsum()
    total_recaudacion = df_pareto["Total_Transaccion_Calc"].sum()
    df_pareto["% Acumulado"] = (df_pareto["Acumulado"] / total_recaudacion) * 100
    df_pareto["Indice_Libro"] = df_pareto.index + 1
    df_pareto["% Libros"] = (df_pareto["Indice_Libro"] / len(df_pareto)) * 100
    
    # Encontrar el punto exacto de corte del 80%
    punto_corte = df_pareto[df_pareto["% Acumulado"] >= 80].iloc[0]
    porcentaje_libros_80 = punto_corte["% Libros"]
    cantidad_libros_80 = int(punto_corte["Indice_Libro"])
    
    fig_pareto = go.Figure()
    # Barra de ventas
    fig_pareto.add_trace(
        go.Bar(
            x=df_pareto["Titulo"][:30], # Top 30 para visualización limpia
            y=df_pareto["Total_Transaccion_Calc"][:30],
            name="Ventas Individuales",
            marker=dict(color="#00ADB5")
        )
    )
    # Línea de acumulado
    fig_pareto.add_trace(
        go.Scatter(
            x=df_pareto["Titulo"][:30],
            y=df_pareto["% Acumulado"][:30],
            name="% Acumulado (Eje Secundario)",
            yaxis="y2",
            line=dict(color="#EF4444", width=3)
        )
    )
    
    fig_pareto.update_layout(
        title="Distribución de Ventas y Curva Pareto (Top 30)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(showticklabels=False), # Ocultar nombres de libros abajo para evitar amontonamiento
        yaxis=dict(title=f"Ventas Unitarias ({moneda})", gridcolor="rgba(255,255,255,0.05)"),
        yaxis2=dict(title="% Acumulado", overlaying="y", side="right", range=[0, 105], showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="left", x=0),
        height=380
    )
    
    st.plotly_chart(fig_pareto, use_container_width=True)
    st.markdown(f"""
    📈 **Resultado del Análisis Pareto**: El **{porcentaje_libros_80:.1f}%** de los títulos (`{cantidad_libros_80}` libros de `{len(df_pareto)}` totales) genera el **80% de tus ventas**.  
    *Insight*: Es vital mantener inventario impecable de estos pocos títulos "core". Perder stock de un bestseller afecta drásticamente el flujo de caja.
    """)

with col_dias:
    st.markdown("#### 🕒 Ventas por Día de la Semana y Comportamiento")
    st.write("Identifica patrones semanales de consumo para organizar promociones y personal de caja.")
    
    # Agrupar ventas por día
    df_dias = df_filtered.groupby(["Dia_Semana_ES", "Dia_Semana_N"])["Total_Transaccion_Calc"].sum().reset_index()
    df_dias = df_dias.sort_values(by="Dia_Semana_N")
    
    fig_dias = px.bar(
        df_dias,
        x="Dia_Semana_ES",
        y="Total_Transaccion_Calc",
        title="Facturación Total según Día de la Semana",
        labels={"Dia_Semana_ES": "Día de la Semana", "Total_Transaccion_Calc": f"Ventas ({moneda})"},
        color_discrete_sequence=["#00E8C6"]
    )
    
    fig_dias.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        height=380
    )
    st.plotly_chart(fig_dias, use_container_width=True)
    
    # Día pico
    dia_pico = df_dias.loc[df_dias["Total_Transaccion_Calc"].idxmax()]["Dia_Semana_ES"]
    st.markdown(f"""
    🛒 **Día de mayor afluencia**: El día comercial líder del período es el **{dia_pico}**.  
    *Estrategia*: Considerar el lanzamiento de promociones relámpago a mitad de semana (Martes/Miércoles) para suavizar la estacionalidad semanal y equilibrar las operaciones físicas.
    """)

# Pie de página descriptivo
st.markdown("<br><hr style='border: 1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.85rem; padding: 20px 0;">
    Dashboard construido en Python para Portfolio Profesional. Datos de simulación basados en investigación de mercado editorial 2025-2026.
</div>
""", unsafe_allow_html=True)
