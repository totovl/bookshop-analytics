"""
build_dashboard.py
==================
Reads ventas_libreria_completo.csv and generates docs/index.html
with an interactive dashboard using Chart.js.

Usage:
    python build_dashboard.py
"""

import pandas as pd
import json
import os
from datetime import datetime

# ─── 1. Read and process CSV ────────────────────────────────────────────────
def load_and_process():
    df = pd.read_csv("ventas_libreria_completo.csv")
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Año_Mes"] = df["Fecha"].dt.to_period("M").astype(str)
    df["Dia_Semana_N"] = df["Fecha"].dt.weekday
    dias_es = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
               4: "Viernes", 5: "Sábado", 6: "Domingo"}
    df["Dia_Semana_ES"] = df["Dia_Semana_N"].map(dias_es)
    return df

df = load_and_process()

# ─── 2. Convert raw data to JSON for client-side processing ─────────────────
records = []
for _, row in df.iterrows():
    records.append({
        "id": row["ID_Transaccion"],
        "fecha": row["Fecha"].strftime("%Y-%m-%d"),
        "titulo": row["Titulo"],
        "genero": row["Genero"],
        "precio": round(float(row["Precio_Unitario"]), 2),
        "cantidad": int(row["Cantidad"]),
        "total": round(float(row["Total_Transaccion"]), 2),
        "metodo_pago": row["Metodo_Pago"],
        "año_mes": row["Año_Mes"],
        "dia_semana": row["Dia_Semana_ES"],
        "dia_semana_n": int(row["Dia_Semana_N"])
    })

data_json = json.dumps(records, ensure_ascii=False)

# Get unique values for filters
genres = sorted(df["Genero"].unique().tolist())
payment_methods = sorted(df["Metodo_Pago"].unique().tolist())
min_date = df["Fecha"].min().strftime("%Y-%m-%d")
max_date = df["Fecha"].max().strftime("%Y-%m-%d")

genres_json = json.dumps(genres, ensure_ascii=False)
payments_json = json.dumps(payment_methods, ensure_ascii=False)

# ─── 3. Generate HTML ───────────────────────────────────────────────────────
html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Dashboard interactivo de Business Intelligence para BookShop Analytics - Análisis de ventas, inventario y tendencias de mercado editorial.">
    <title>BookShop Analytics | Dashboard BI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
    <style>
        /* ================================================================
           RESET & VARIABLES
           ================================================================ */
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        :root {{
            --primary: #6C5CE7;
            --primary-light: #A29BFE;
            --primary-dark: #5A4BD1;
            --primary-bg: rgba(108, 92, 231, 0.08);
            --primary-bg-hover: rgba(108, 92, 231, 0.14);
            --success: #00B894;
            --success-bg: rgba(0, 184, 148, 0.10);
            --danger: #E17055;
            --danger-bg: rgba(225, 112, 85, 0.10);
            --warning: #FDCB6E;
            --warning-bg: rgba(253, 203, 110, 0.12);
            --info: #74B9FF;
            --bg-body: #F0F2F8;
            --bg-card: #FFFFFF;
            --bg-sidebar: #1B1F3B;
            --bg-sidebar-hover: #272B4A;
            --bg-sidebar-active: rgba(108, 92, 231, 0.25);
            --text-primary: #2D3436;
            --text-secondary: #636E72;
            --text-muted: #B2BEC3;
            --text-sidebar: #DFE6E9;
            --text-sidebar-muted: #8395A7;
            --border: #E8ECF1;
            --border-light: #F1F3F7;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
            --shadow-md: 0 4px 16px rgba(0,0,0,0.06);
            --shadow-lg: 0 8px 32px rgba(0,0,0,0.08);
            --shadow-card: 0 2px 12px rgba(0,0,0,0.04);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 20px;
            --sidebar-width: 260px;
        }}

        html {{ scroll-behavior: smooth; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-body);
            color: var(--text-primary);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }}

        /* ================================================================
           SIDEBAR
           ================================================================ */
        .sidebar {{
            position: fixed;
            left: 0; top: 0;
            width: var(--sidebar-width);
            height: 100vh;
            background: var(--bg-sidebar);
            display: flex;
            flex-direction: column;
            z-index: 100;
            padding: 0;
            overflow-y: auto;
        }}
        .sidebar-logo {{
            padding: 28px 24px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }}
        .sidebar-logo .logo-icon {{
            width: 40px; height: 40px;
            background: linear-gradient(135deg, var(--primary), var(--primary-light));
            border-radius: var(--radius-sm);
            display: flex; align-items: center; justify-content: center;
            font-size: 20px;
            flex-shrink: 0;
        }}
        .sidebar-logo .logo-text {{
            color: #FFFFFF;
            font-size: 16px;
            font-weight: 700;
            letter-spacing: -0.3px;
        }}
        .sidebar-logo .logo-sub {{
            color: var(--text-sidebar-muted);
            font-size: 11px;
            font-weight: 400;
            margin-top: 2px;
        }}
        .sidebar-nav {{
            padding: 16px 12px;
            flex: 1;
        }}
        .sidebar-nav .nav-section {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-sidebar-muted);
            padding: 16px 12px 8px;
            font-weight: 600;
        }}
        .sidebar-nav a {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 12px;
            color: var(--text-sidebar);
            text-decoration: none;
            border-radius: var(--radius-sm);
            font-size: 13.5px;
            font-weight: 500;
            transition: all 0.2s ease;
            margin-bottom: 2px;
        }}
        .sidebar-nav a:hover {{
            background: var(--bg-sidebar-hover);
            color: #FFFFFF;
        }}
        .sidebar-nav a.active {{
            background: var(--bg-sidebar-active);
            color: var(--primary-light);
        }}
        .sidebar-nav a .nav-icon {{
            width: 20px;
            text-align: center;
            font-size: 15px;
            flex-shrink: 0;
        }}
        .sidebar-footer {{
            padding: 16px 20px 24px;
            border-top: 1px solid rgba(255,255,255,0.06);
        }}
        .sidebar-footer p {{
            color: var(--text-sidebar-muted);
            font-size: 11px;
            line-height: 1.5;
        }}

        /* ================================================================
           MAIN CONTENT
           ================================================================ */
        .main {{
            margin-left: var(--sidebar-width);
            padding: 28px 36px 60px;
            min-height: 100vh;
        }}

        .page-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 28px;
        }}
        .page-header h1 {{
            font-size: 26px;
            font-weight: 800;
            color: var(--text-primary);
            letter-spacing: -0.5px;
        }}
        .page-header .subtitle {{
            color: var(--text-secondary);
            font-size: 14px;
            margin-top: 4px;
            font-weight: 400;
        }}

        /* ================================================================
           FILTER BAR
           ================================================================ */
        .filter-bar {{
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            padding: 16px 24px;
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 28px;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-light);
            flex-wrap: wrap;
        }}
        .filter-bar .filter-label {{
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            display: flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }}
        .filter-bar .filter-badge {{
            background: var(--primary);
            color: #fff;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 10px;
        }}
        .filter-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .filter-group label {{
            font-size: 12px;
            color: var(--text-secondary);
            font-weight: 500;
            white-space: nowrap;
        }}
        .filter-group input[type="date"],
        .filter-group select {{
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            background: var(--bg-body);
            color: var(--text-primary);
            outline: none;
            transition: border-color 0.2s;
            cursor: pointer;
        }}
        .filter-group input[type="date"]:focus,
        .filter-group select:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px var(--primary-bg);
        }}
        .filter-group select {{
            min-width: 160px;
        }}
        .filter-separator {{
            width: 1px;
            height: 28px;
            background: var(--border);
        }}
        .btn-reset {{
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 600;
            padding: 8px 16px;
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            background: var(--bg-card);
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        .btn-reset:hover {{
            background: var(--bg-body);
            border-color: var(--primary);
            color: var(--primary);
        }}

        /* ================================================================
           KPI CARDS
           ================================================================ */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 28px;
        }}
        .kpi-card {{
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            padding: 22px 24px;
            box-shadow: var(--shadow-card);
            border: 1px solid var(--border-light);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary), var(--primary-light));
            opacity: 0;
            transition: opacity 0.3s;
        }}
        .kpi-card:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-lg);
        }}
        .kpi-card:hover::before {{
            opacity: 1;
        }}
        .kpi-card .kpi-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 14px;
        }}
        .kpi-card .kpi-label {{
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .kpi-card .kpi-icon {{
            width: 36px; height: 36px;
            border-radius: var(--radius-sm);
            display: flex; align-items: center; justify-content: center;
            font-size: 16px;
            flex-shrink: 0;
        }}
        .kpi-card .kpi-icon.purple {{ background: var(--primary-bg); }}
        .kpi-card .kpi-icon.green {{ background: var(--success-bg); }}
        .kpi-card .kpi-icon.orange {{ background: var(--danger-bg); }}
        .kpi-card .kpi-icon.blue {{ background: rgba(116, 185, 255, 0.12); }}
        .kpi-card .kpi-value {{
            font-size: 28px;
            font-weight: 800;
            color: var(--text-primary);
            line-height: 1.1;
            letter-spacing: -0.5px;
            margin-bottom: 8px;
        }}
        .kpi-card .kpi-delta {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
        }}
        .kpi-card .kpi-delta.up {{
            color: var(--success);
            background: var(--success-bg);
        }}
        .kpi-card .kpi-delta.down {{
            color: var(--danger);
            background: var(--danger-bg);
        }}
        .kpi-card .kpi-delta.neutral {{
            color: var(--text-muted);
            background: rgba(178, 190, 195, 0.12);
        }}
        .kpi-card .kpi-comparison {{
            font-size: 11px;
            color: var(--text-muted);
            margin-left: 6px;
            font-weight: 400;
        }}
        .kpi-card .kpi-subtext {{
            font-size: 11px;
            color: var(--primary);
            font-weight: 600;
            margin-top: 6px;
        }}

        /* ================================================================
           SECTIONS & CARDS
           ================================================================ */
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section-title .section-icon {{ font-size: 20px; }}
        .section-divider {{
            height: 1px;
            background: var(--border);
            margin: 8px 0 32px;
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: 2fr 1.2fr;
            gap: 24px;
            margin-bottom: 32px;
        }}
        .grid-2-equal {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 32px;
        }}
        .grid-3-1 {{
            display: grid;
            grid-template-columns: 2.2fr 1fr;
            gap: 24px;
            margin-bottom: 32px;
        }}
        .card {{
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow-card);
            border: 1px solid var(--border-light);
            transition: box-shadow 0.3s;
        }}
        .card:hover {{ box-shadow: var(--shadow-md); }}
        .card-title {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 4px;
        }}
        .card-subtitle {{
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 20px;
        }}
        .chart-container {{
            position: relative;
            width: 100%;
        }}
        .chart-container canvas {{ width: 100% !important; }}

        /* ================================================================
           TABLES
           ================================================================ */
        .data-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 13px;
        }}
        .data-table thead th {{
            text-align: left;
            padding: 10px 14px;
            font-weight: 600;
            color: var(--text-secondary);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            border-bottom: 2px solid var(--border);
            background: var(--bg-body);
        }}
        .data-table thead th:first-child {{ border-radius: var(--radius-sm) 0 0 0; }}
        .data-table thead th:last-child {{ border-radius: 0 var(--radius-sm) 0 0; }}
        .data-table tbody td {{
            padding: 11px 14px;
            border-bottom: 1px solid var(--border-light);
            color: var(--text-primary);
            vertical-align: middle;
        }}
        .data-table tbody tr {{
            transition: background 0.15s;
        }}
        .data-table tbody tr:hover {{
            background: var(--primary-bg);
        }}
        .data-table tbody tr:last-child td {{ border-bottom: none; }}
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            white-space: nowrap;
        }}
        .badge.green {{ background: var(--success-bg); color: var(--success); }}
        .badge.red {{ background: var(--danger-bg); color: var(--danger); }}
        .badge.yellow {{ background: var(--warning-bg); color: #E17055; }}
        .badge.purple {{ background: var(--primary-bg); color: var(--primary); }}

        /* ================================================================
           INSIGHT BOXES
           ================================================================ */
        .insight-box {{
            padding: 16px 20px;
            border-radius: var(--radius-md);
            font-size: 13px;
            line-height: 1.65;
            margin-top: 16px;
            border-left: 4px solid;
        }}
        .insight-box.opportunity {{
            background: var(--primary-bg);
            border-color: var(--primary);
            color: var(--text-primary);
        }}
        .insight-box.risk {{
            background: var(--danger-bg);
            border-color: var(--danger);
            color: var(--text-primary);
        }}
        .insight-box.tip {{
            background: var(--success-bg);
            border-color: var(--success);
            color: var(--text-primary);
        }}
        .insight-box strong {{
            display: block;
            margin-bottom: 4px;
            font-size: 13px;
        }}

        .donut-wrapper {{
            position: relative;
            display: flex;
            justify-content: center;
        }}
        .donut-center {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            pointer-events: none;
        }}
        .donut-center .donut-value {{
            font-size: 18px;
            font-weight: 800;
            color: var(--danger);
        }}
        .donut-center .donut-label {{
            font-size: 10px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .pareto-result {{
            margin-top: 16px;
            padding: 14px 18px;
            background: var(--primary-bg);
            border-radius: var(--radius-md);
            font-size: 13px;
            color: var(--text-primary);
            line-height: 1.6;
        }}
        .dashboard-footer {{
            text-align: center;
            padding: 32px 0 0;
            color: var(--text-muted);
            font-size: 12px;
        }}

        /* Animations */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(16px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .animate-in {{ animation: fadeInUp 0.5s ease forwards; }}
        .delay-1 {{ animation-delay: 0.05s; }}
        .delay-2 {{ animation-delay: 0.10s; }}
        .delay-3 {{ animation-delay: 0.15s; }}
        .delay-4 {{ animation-delay: 0.20s; }}
        .delay-5 {{ animation-delay: 0.25s; }}
        .delay-6 {{ animation-delay: 0.30s; }}

        /* Scrollbar */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}

        /* Responsive */
        @media (max-width: 1200px) {{
            .grid-2, .grid-3-1, .grid-2-equal {{ grid-template-columns: 1fr; }}
        }}
        @media (max-width: 768px) {{
            .sidebar {{ display: none; }}
            .main {{ margin-left: 0; padding: 20px 16px; }}
            .kpi-grid {{ grid-template-columns: repeat(2, 1fr); gap: 12px; }}
            .filter-bar {{ flex-direction: column; align-items: flex-start; }}
            .page-header h1 {{ font-size: 22px; }}
        }}
    </style>
</head>
<body>

<!-- SIDEBAR -->
<aside class="sidebar">
    <div class="sidebar-logo">
        <div class="logo-icon">📚</div>
        <div>
            <div class="logo-text">BookShop</div>
            <div class="logo-sub">Analytics Dashboard</div>
        </div>
    </div>
    <nav class="sidebar-nav">
        <div class="nav-section">Principal</div>
        <a href="#overview" class="active">
            <span class="nav-icon">📊</span> Overview
        </a>
        <a href="#revenue">
            <span class="nav-icon">💰</span> Ingresos & Evolución
        </a>
        <a href="#operations">
            <span class="nav-icon">📦</span> Operaciones & Stock
        </a>
        <div class="nav-section">Análisis</div>
        <a href="#trends">
            <span class="nav-icon">🔮</span> Tendencias MoM
        </a>
        <a href="#pareto">
            <span class="nav-icon">🎯</span> Pareto & Patrones
        </a>
    </nav>
    <div class="sidebar-footer">
        <p>Dashboard de Portfolio<br>Datos simulados 2025-2026</p>
    </div>
</aside>

<!-- MAIN CONTENT -->
<main class="main">
    <div class="page-header">
        <div>
            <h1 id="overview">📊 Business Intelligence Dashboard</h1>
            <p class="subtitle">Gestión y análisis de rendimiento de librería — datos actualizados al {max_date}</p>
        </div>
    </div>

    <!-- FILTER BAR -->
    <div class="filter-bar">
        <div class="filter-label">
            Filtros activos <span class="filter-badge" id="filterCount">0</span>
        </div>
        <div class="filter-separator"></div>
        <div class="filter-group">
            <label for="dateFrom">Desde</label>
            <input type="date" id="dateFrom" value="{min_date}" min="{min_date}" max="{max_date}">
        </div>
        <div class="filter-group">
            <label for="dateTo">Hasta</label>
            <input type="date" id="dateTo" value="{max_date}" min="{min_date}" max="{max_date}">
        </div>
        <div class="filter-separator"></div>
        <div class="filter-group">
            <label for="genreFilter">Categoría</label>
            <select id="genreFilter"><option value="all">Todas las categorías</option></select>
        </div>
        <div class="filter-separator"></div>
        <div class="filter-group">
            <label for="paymentFilter">Método de pago</label>
            <select id="paymentFilter"><option value="all">Todos los métodos</option></select>
        </div>
        <div class="filter-separator"></div>
        <button class="btn-reset" onclick="resetFilters()">Restablecer filtros</button>
    </div>

    <!-- KPI CARDS -->
    <div class="kpi-grid" id="kpiGrid"></div>

    <!-- REVENUE & EVOLUTION -->
    <div class="section-divider"></div>
    <h2 class="section-title" id="revenue"><span class="section-icon">📈</span> Evolución Temporal & Canales Financieros</h2>
    <div class="grid-2">
        <div class="card">
            <div class="card-title">Facturación Mensual por Categoría</div>
            <div class="card-subtitle">Evolución de ingresos segmentada por género literario</div>
            <div class="chart-container"><canvas id="chartEvolucion" height="300"></canvas></div>
        </div>
        <div class="card">
            <div class="card-title">Canales de Cobro & Comisiones</div>
            <div class="card-subtitle">Distribución de ingresos según método de pago</div>
            <div class="donut-wrapper">
                <div class="chart-container" style="max-width: 320px;">
                    <canvas id="chartDonut" height="280"></canvas>
                </div>
                <div class="donut-center">
                    <div class="donut-label">Fuga Comisiones</div>
                    <div class="donut-value" id="comisionValue">$0</div>
                </div>
            </div>
            <div class="insight-box tip" id="insightComisiones" style="margin-top: 12px;"></div>
        </div>
    </div>

    <!-- OPERATIONS & STOCK -->
    <div class="section-divider"></div>
    <h2 class="section-title" id="operations"><span class="section-icon">📦</span> Operaciones e Inventario</h2>
    <div class="grid-3-1">
        <div class="card">
            <div class="card-title">Top 20 Libros con Mayor Demanda</div>
            <div class="card-subtitle">Títulos con mayor rotación en el período seleccionado</div>
            <div class="chart-container"><canvas id="chartTopBooks" height="420"></canvas></div>
        </div>
        <div class="card">
            <div class="card-title">Reposición Prioritaria</div>
            <div class="card-subtitle">Stock de seguridad — Top 10 alta rotación</div>
            <div id="tableReposicion"></div>
            <div class="insight-box tip" style="margin-top: 14px;">
                <strong>💡 Regla de Oro en Retail</strong>
                Aplica un factor de <strong>1.5x de stock de seguridad</strong> para el Bestseller actual en meses estacionales (Nov/Dic) para evitar quiebres de stock.
            </div>
        </div>
    </div>

    <!-- MoM TRENDS -->
    <div class="section-divider"></div>
    <h2 class="section-title" id="trends"><span class="section-icon">🔮</span> Análisis de Tendencias Trimestrales</h2>
    <div class="grid-2">
        <div class="card">
            <div class="card-title">Crecimiento Mensual Reciente por Género</div>
            <div class="card-subtitle" id="momPeriod">Último trimestre evaluado</div>
            <div id="tableMoM"></div>
        </div>
        <div class="card">
            <div class="card-title">🎯 Decisiones Presupuestarias</div>
            <div class="card-subtitle">Alertas basadas en tendencias de mercado</div>
            <div id="insightAlerts"></div>
        </div>
    </div>

    <!-- HEATMAP -->
    <div class="card" style="margin-bottom: 32px;">
        <div class="card-title">🗺️ Mapa de Calor Mensual — Ventas por Género</div>
        <div class="card-subtitle">Identifica picos y ciclos estacionales para planificar campañas de marketing y stock</div>
        <div class="chart-container"><canvas id="chartHeatmap" height="280"></canvas></div>
    </div>

    <!-- PARETO & PATTERNS -->
    <div class="section-divider"></div>
    <h2 class="section-title" id="pareto"><span class="section-icon">🎯</span> Análisis de Valor Comercial</h2>
    <div class="grid-2-equal">
        <div class="card">
            <div class="card-title">Regla de Pareto (80/20) del Portafolio</div>
            <div class="card-subtitle">¿Qué proporción de los títulos genera el 80% de ingresos?</div>
            <div class="chart-container"><canvas id="chartPareto" height="300"></canvas></div>
            <div class="pareto-result" id="paretoResult"></div>
        </div>
        <div class="card">
            <div class="card-title">Facturación por Día de la Semana</div>
            <div class="card-subtitle">Patrones semanales para organizar promociones y personal</div>
            <div class="chart-container"><canvas id="chartDias" height="300"></canvas></div>
            <div class="insight-box opportunity" id="insightDias" style="margin-top: 14px;"></div>
        </div>
    </div>

    <div class="dashboard-footer">
        Dashboard construido para Portfolio Profesional · Datos de simulación basados en investigación de mercado editorial 2025-2026
    </div>
</main>

<script>
const RAW_DATA = {data_json};
const ALL_GENRES = {genres_json};
const ALL_PAYMENTS = {payments_json};
const DATE_MIN = "{min_date}";
const DATE_MAX = "{max_date}";
const COMISIONES = {{"Efectivo":0,"Mercado Pago":0.035,"Tarjeta de Crédito":0.025,"Tarjeta de Débito":0.012,"Transferencia":0.001}};
const PALETTE = ['#6C5CE7','#A29BFE','#00B894','#74B9FF','#E17055','#FDCB6E','#FD79A8','#00CEC9','#636E72','#55EFC4','#0984E3','#D63031','#E84393','#2D3436','#B2BEC3'];
let charts = {{}};

document.addEventListener('DOMContentLoaded', () => {{
    populateFilters();
    applyFilters();
    document.getElementById('dateFrom').addEventListener('change', applyFilters);
    document.getElementById('dateTo').addEventListener('change', applyFilters);
    document.getElementById('genreFilter').addEventListener('change', applyFilters);
    document.getElementById('paymentFilter').addEventListener('change', applyFilters);
    setupScrollSpy();
}});

function populateFilters() {{
    const gs = document.getElementById('genreFilter');
    ALL_GENRES.forEach(g => {{ const o = document.createElement('option'); o.value = g; o.textContent = g; gs.appendChild(o); }});
    const ps = document.getElementById('paymentFilter');
    ALL_PAYMENTS.forEach(p => {{ const o = document.createElement('option'); o.value = p; o.textContent = p; ps.appendChild(o); }});
}}

function resetFilters() {{
    document.getElementById('dateFrom').value = DATE_MIN;
    document.getElementById('dateTo').value = DATE_MAX;
    document.getElementById('genreFilter').value = 'all';
    document.getElementById('paymentFilter').value = 'all';
    applyFilters();
}}

function applyFilters() {{
    const from = document.getElementById('dateFrom').value;
    const to = document.getElementById('dateTo').value;
    const genre = document.getElementById('genreFilter').value;
    const payment = document.getElementById('paymentFilter').value;
    let count = 0;
    if (from !== DATE_MIN) count++;
    if (to !== DATE_MAX) count++;
    if (genre !== 'all') count++;
    if (payment !== 'all') count++;
    document.getElementById('filterCount').textContent = count;
    const filtered = RAW_DATA.filter(r => {{
        if (r.fecha < from || r.fecha > to) return false;
        if (genre !== 'all' && r.genero !== genre) return false;
        if (payment !== 'all' && r.metodo_pago !== payment) return false;
        return true;
    }});
    const daysDiff = Math.round((new Date(to) - new Date(from)) / 86400000) + 1;
    const prevTo = new Date(new Date(from).getTime() - 86400000);
    const prevFrom = new Date(prevTo.getTime() - (daysDiff - 1) * 86400000);
    const prevFromStr = prevFrom.toISOString().slice(0, 10);
    const prevToStr = prevTo.toISOString().slice(0, 10);
    const prevFiltered = RAW_DATA.filter(r => {{
        if (r.fecha < prevFromStr || r.fecha > prevToStr) return false;
        if (genre !== 'all' && r.genero !== genre) return false;
        if (payment !== 'all' && r.metodo_pago !== payment) return false;
        return true;
    }});
    renderKPIs(filtered, prevFiltered);
    renderEvolucion(filtered);
    renderDonut(filtered);
    renderTopBooks(filtered);
    renderReposicionTable(filtered);
    renderMoM();
    renderHeatmap();
    renderPareto(filtered);
    renderDias(filtered);
}}

function calcKPIs(data) {{
    const ingresos = data.reduce((s, r) => s + r.total, 0);
    const unidades = data.reduce((s, r) => s + r.cantidad, 0);
    const txns = new Set(data.map(r => r.id)).size;
    const ticket = txns > 0 ? ingresos / txns : 0;
    return {{ ingresos, unidades, txns, ticket }};
}}

function getDelta(act, prev) {{
    if (prev === 0) return {{ str: 'N/A', status: 'neutral' }};
    const pct = ((act - prev) / prev) * 100;
    return {{ str: (pct >= 0 ? '+' : '') + pct.toFixed(1) + '%', status: pct > 0 ? 'up' : pct < 0 ? 'down' : 'neutral' }};
}}

function renderKPIs(filtered, prevFiltered) {{
    const curr = calcKPIs(filtered);
    const prev = calcKPIs(prevFiltered);
    const genMap = {{}};
    filtered.forEach(r => {{ genMap[r.genero] = (genMap[r.genero] || 0) + r.total; }});
    let generoLider = 'N/A', porcentajeLider = 0, maxGen = 0;
    for (const [g, v] of Object.entries(genMap)) {{ if (v > maxGen) {{ maxGen = v; generoLider = g; }} }}
    if (curr.ingresos > 0) porcentajeLider = (maxGen / curr.ingresos * 100);
    const bookMap = {{}};
    filtered.forEach(r => {{ bookMap[r.titulo] = (bookMap[r.titulo] || 0) + r.cantidad; }});
    let bestseller = 'N/A', bestsellerQty = 0;
    for (const [t, q] of Object.entries(bookMap)) {{ if (q > bestsellerQty) {{ bestsellerQty = q; bestseller = t; }} }}
    const d1 = getDelta(curr.ingresos, prev.ingresos);
    const d2 = getDelta(curr.unidades, prev.unidades);
    const d3 = getDelta(curr.ticket, prev.ticket);
    const d4 = getDelta(curr.txns, prev.txns);
    document.getElementById('kpiGrid').innerHTML =
        kpiCard('Ingresos Totales', '$' + formatNum(curr.ingresos), d1, '💰', 'purple', '', 1) +
        kpiCard('Unidades Vendidas', formatInt(curr.unidades), d2, '📦', 'green', '', 2) +
        kpiCard('Ticket Promedio', '$' + curr.ticket.toFixed(2), d3, '🧾', 'blue', '', 3) +
        kpiCard('Transacciones', formatInt(curr.txns), d4, '🔄', 'orange', '', 4) +
        kpiCard('Categoría Líder', generoLider, {{ str: porcentajeLider.toFixed(1) + '%', status: 'neutral' }}, '🏆', 'purple', 'Participación Ventas', 5) +
        kpiCard('Bestseller', bestseller.length > 25 ? bestseller.slice(0,22) + '...' : bestseller, {{ str: bestsellerQty + ' uds', status: 'up' }}, '⭐', 'green', 'Reposición Activa', 6);
}}

function kpiCard(label, value, delta, icon, iconClass, subtext, delay) {{
    const arr = delta.status === 'up' ? '↑' : delta.status === 'down' ? '↓' : '•';
    return '<div class="kpi-card animate-in delay-' + delay + '">' +
        '<div class="kpi-header"><div class="kpi-label">' + label + '</div><div class="kpi-icon ' + iconClass + '">' + icon + '</div></div>' +
        '<div class="kpi-value">' + value + '</div>' +
        '<div><span class="kpi-delta ' + delta.status + '">' + arr + ' ' + delta.str + '</span><span class="kpi-comparison">vs. período anterior</span></div>' +
        (subtext ? '<div class="kpi-subtext">' + subtext + '</div>' : '') +
        '</div>';
}}

function renderEvolucion(filtered) {{
    const monthGenre = {{}}, months = new Set(), genres = new Set();
    filtered.forEach(r => {{ months.add(r.año_mes); genres.add(r.genero); const k = r.año_mes + '|' + r.genero; monthGenre[k] = (monthGenre[k] || 0) + r.total; }});
    const sM = [...months].sort(), sG = [...genres].sort();
    const datasets = sG.map((g, i) => ({{
        label: g, data: sM.map(m => monthGenre[m + '|' + g] || 0),
        borderColor: PALETTE[i % PALETTE.length], backgroundColor: PALETTE[i % PALETTE.length] + '18',
        borderWidth: 2.5, fill: true, tension: 0.4, pointRadius: 3, pointHoverRadius: 6, pointBackgroundColor: PALETTE[i % PALETTE.length]
    }}));
    destroyChart('chartEvolucion');
    charts.chartEvolucion = new Chart(document.getElementById('chartEvolucion'), {{
        type: 'line', data: {{ labels: sM, datasets }},
        options: {{ responsive: true, maintainAspectRatio: false, interaction: {{ mode: 'index', intersect: false }},
            plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ family: 'Inter', size: 11 }}, padding: 16, usePointStyle: true, pointStyle: 'circle' }} }},
                tooltip: {{ backgroundColor: '#1B1F3B', titleFont: {{ family: 'Inter', weight: '600' }}, bodyFont: {{ family: 'Inter' }}, padding: 12, cornerRadius: 8, callbacks: {{ label: ctx => ctx.dataset.label + ': $' + formatNum(ctx.parsed.y) }} }} }},
            scales: {{ x: {{ grid: {{ color: 'rgba(0,0,0,0.04)' }}, ticks: {{ font: {{ family: 'Inter', size: 11 }}, maxRotation: 45 }} }},
                y: {{ grid: {{ color: 'rgba(0,0,0,0.04)' }}, ticks: {{ font: {{ family: 'Inter', size: 11 }}, callback: v => '$' + (v >= 1000 ? (v/1000).toFixed(0) + 'K' : v) }} }} }} }}
    }});
}}

function renderDonut(filtered) {{
    const payMap = {{}};
    filtered.forEach(r => {{ payMap[r.metodo_pago] = (payMap[r.metodo_pago] || 0) + r.total; }});
    const labels = Object.keys(payMap).sort(), values = labels.map(l => payMap[l]);
    const totalComision = labels.reduce((s, l) => s + (payMap[l] * (COMISIONES[l] || 0)), 0);
    document.getElementById('comisionValue').textContent = '$' + formatNum(totalComision);
    document.getElementById('insightComisiones').innerHTML = '<strong>💡 Análisis de pasarelas</strong>Se estiman pérdidas de <strong>$' + formatNum(totalComision) + '</strong> por aranceles bancarios. Incentivar Transferencias y Efectivo para reducir el impacto financiero.';
    const donutColors = ['#6C5CE7', '#A29BFE', '#74B9FF', '#00B894', '#FDCB6E'];
    destroyChart('chartDonut');
    charts.chartDonut = new Chart(document.getElementById('chartDonut'), {{
        type: 'doughnut', data: {{ labels, datasets: [{{ data: values, backgroundColor: donutColors.slice(0, labels.length), borderColor: '#FFFFFF', borderWidth: 3, hoverOffset: 8 }}] }},
        options: {{ responsive: true, maintainAspectRatio: false, cutout: '65%',
            plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ family: 'Inter', size: 11 }}, padding: 12, usePointStyle: true, pointStyle: 'circle' }} }},
                tooltip: {{ backgroundColor: '#1B1F3B', titleFont: {{ family: 'Inter', weight: '600' }}, bodyFont: {{ family: 'Inter' }}, padding: 12, cornerRadius: 8,
                    callbacks: {{ label: ctx => {{ const t = ctx.dataset.data.reduce((a, b) => a + b, 0); return ctx.label + ': $' + formatNum(ctx.parsed) + ' (' + ((ctx.parsed / t) * 100).toFixed(1) + '%)'; }} }} }} }} }}
    }});
}}

function renderTopBooks(filtered) {{
    const bookMap = {{}}, bookGenre = {{}};
    filtered.forEach(r => {{ bookMap[r.titulo] = (bookMap[r.titulo] || 0) + r.cantidad; bookGenre[r.titulo] = r.genero; }});
    const sorted = Object.entries(bookMap).sort((a, b) => b[1] - a[1]).slice(0, 20).reverse();
    const labels = sorted.map(e => e[0].length > 35 ? e[0].slice(0, 32) + '...' : e[0]);
    const values = sorted.map(e => e[1]);
    const colors = sorted.map(e => {{ const gi = ALL_GENRES.indexOf(bookGenre[e[0]]); return PALETTE[gi % PALETTE.length]; }});
    destroyChart('chartTopBooks');
    charts.chartTopBooks = new Chart(document.getElementById('chartTopBooks'), {{
        type: 'bar', data: {{ labels, datasets: [{{ data: values, backgroundColor: colors.map(c => c + 'CC'), borderColor: colors, borderWidth: 1, borderRadius: 4, barThickness: 18 }}] }},
        options: {{ responsive: true, maintainAspectRatio: false, indexAxis: 'y',
            plugins: {{ legend: {{ display: false }}, tooltip: {{ backgroundColor: '#1B1F3B', titleFont: {{ family: 'Inter', weight: '600' }}, bodyFont: {{ family: 'Inter' }}, padding: 12, cornerRadius: 8,
                callbacks: {{ title: ctx => sorted[ctx[0].dataIndex]?.[0] || '', label: ctx => 'Unidades vendidas: ' + formatInt(ctx.parsed.x) }} }} }},
            scales: {{ x: {{ grid: {{ color: 'rgba(0,0,0,0.04)' }}, ticks: {{ font: {{ family: 'Inter', size: 11 }} }} }}, y: {{ grid: {{ display: false }}, ticks: {{ font: {{ family: 'Inter', size: 11 }} }} }} }} }}
    }});
}}

function renderReposicionTable(filtered) {{
    const bookMap = {{}}, bookGenre = {{}};
    filtered.forEach(r => {{ bookMap[r.titulo] = (bookMap[r.titulo] || 0) + r.cantidad; bookGenre[r.titulo] = r.genero; }});
    const sorted = Object.entries(bookMap).sort((a, b) => b[1] - a[1]).slice(0, 10);
    let html = '<table class="data-table"><thead><tr><th>#</th><th>Título</th><th>Categoría</th><th>Uds.</th></tr></thead><tbody>';
    sorted.forEach(([title, qty], i) => {{ html += '<tr><td style="color:var(--primary);font-weight:700;">' + (i + 1) + '</td><td>' + title + '</td><td><span class="badge purple">' + bookGenre[title] + '</span></td><td style="font-weight:700;">' + formatInt(qty) + '</td></tr>'; }});
    html += '</tbody></table>';
    document.getElementById('tableReposicion').innerHTML = html;
}}

function renderMoM() {{
    const monthGenre = {{}}, months = new Set(), genres = new Set();
    RAW_DATA.forEach(r => {{ months.add(r.año_mes); genres.add(r.genero); const k = r.año_mes + '|' + r.genero; monthGenre[k] = (monthGenre[k] || 0) + r.total; }});
    const sM = [...months].sort(), sG = [...genres].sort();
    if (sM.length < 3) {{ document.getElementById('tableMoM').innerHTML = '<p style="color:var(--text-muted)">Datos insuficientes.</p>'; return; }}
    const lastThree = sM.slice(-3);
    document.getElementById('momPeriod').textContent = 'Evaluado sobre: ' + lastThree.join(', ');
    const growthByGenre = {{}};
    sG.forEach(g => {{
        const vals = sM.map(m => monthGenre[m + '|' + g] || 0);
        const pcts = [];
        for (let i = 1; i < vals.length; i++) {{ if (vals[i-1] > 0) pcts.push(((vals[i] - vals[i-1]) / vals[i-1]) * 100); }}
        const l3 = pcts.slice(-3);
        growthByGenre[g] = l3.length > 0 ? l3.reduce((a, b) => a + b, 0) / l3.length : 0;
    }});
    const sorted = Object.entries(growthByGenre).sort((a, b) => b[1] - a[1]);
    function classify(pct) {{ if (pct > 1.5) return ['🟢 Crecimiento Rápido (Invertir)', 'green']; if (pct < -1.5) return ['🔴 Declive Sostenido (Liquidar)', 'red']; return ['🟡 Estable (Mantener)', 'yellow']; }}
    let html = '<table class="data-table"><thead><tr><th>Género</th><th>Crecimiento MoM</th><th>Recomendación</th></tr></thead><tbody>';
    sorted.forEach(([genre, pct]) => {{ const [recText, badgeClass] = classify(pct); html += '<tr><td style="font-weight:600;">' + genre + '</td><td style="font-weight:700;color:' + (pct >= 0 ? 'var(--success)' : 'var(--danger)') + '">' + (pct >= 0 ? '+' : '') + pct.toFixed(2) + '%</td><td><span class="badge ' + badgeClass + '">' + recText + '</span></td></tr>'; }});
    html += '</tbody></table>';
    document.getElementById('tableMoM').innerHTML = html;
    const top = sorted[0], low = sorted[sorted.length - 1];
    document.getElementById('insightAlerts').innerHTML =
        '<div class="insight-box opportunity"><strong>🚀 OPORTUNIDAD: CATEGORÍA EN ASCENSO</strong><strong>' + top[0] + '</strong> lidera con crecimiento mensual promedio del <strong>' + (top[1] >= 0 ? '+' : '') + top[1].toFixed(2) + '%</strong>.<br><em>Acción:</em> Asignar un 15% extra del presupuesto de compras a novedades de este género.</div>' +
        '<div class="insight-box risk" style="margin-top:12px;"><strong>⚠️ RIESGO: CATEGORÍA PERDIENDO TERRENO</strong><strong>' + low[0] + '</strong> muestra contracción de <strong>' + low[1].toFixed(2) + '%</strong> mensual.<br><em>Acción:</em> Frenar compras de fondo de catálogo y realizar campañas de liquidación.</div>';
}}

function renderHeatmap() {{
    const monthGenre = {{}}, months = new Set(), genres = new Set();
    RAW_DATA.forEach(r => {{ months.add(r.año_mes); genres.add(r.genero); const k = r.año_mes + '|' + r.genero; monthGenre[k] = (monthGenre[k] || 0) + r.total; }});
    const sM = [...months].sort(), sG = [...genres].sort();
    const data = []; let maxVal = 0;
    sG.forEach((g, gi) => {{ sM.forEach((m, mi) => {{ const v = monthGenre[m + '|' + g] || 0; if (v > maxVal) maxVal = v; data.push({{ x: mi, y: gi, v }}); }}); }});
    destroyChart('chartHeatmap');
    charts.chartHeatmap = new Chart(document.getElementById('chartHeatmap'), {{
        type: 'bubble', data: {{ datasets: [{{ data: data.map(d => ({{ x: d.x, y: d.y, r: Math.max(3, (d.v / maxVal) * 22) }})),
            backgroundColor: data.map(d => {{ const i = d.v / maxVal; return 'rgba(' + Math.round(108 + 132*(1-i)) + ',' + Math.round(92 + 150*(1-i)) + ',' + Math.round(231 + 17*(1-i)) + ',0.75)'; }}),
            borderColor: 'rgba(108,92,231,0.3)', borderWidth: 1 }}] }},
        options: {{ responsive: true, maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }}, tooltip: {{ backgroundColor: '#1B1F3B', titleFont: {{ family: 'Inter', weight: '600' }}, bodyFont: {{ family: 'Inter' }}, padding: 12, cornerRadius: 8,
                callbacks: {{ title: ctx => {{ const d = data[ctx[0].dataIndex]; return sG[d.y] + ' — ' + sM[d.x]; }}, label: ctx => 'Ventas: $' + formatNum(data[ctx.dataIndex].v) }} }} }},
            scales: {{ x: {{ type: 'linear', min: -0.5, max: sM.length - 0.5, grid: {{ color: 'rgba(0,0,0,0.04)' }}, ticks: {{ font: {{ family: 'Inter', size: 10 }}, stepSize: 1, callback: v => sM[v] || '' }} }},
                y: {{ type: 'linear', min: -0.5, max: sG.length - 0.5, grid: {{ color: 'rgba(0,0,0,0.04)' }}, ticks: {{ font: {{ family: 'Inter', size: 11 }}, stepSize: 1, callback: v => sG[v] || '' }} }} }} }}
    }});
}}

function renderPareto(filtered) {{
    const bookMap = {{}};
    filtered.forEach(r => {{ bookMap[r.titulo] = (bookMap[r.titulo] || 0) + r.total; }});
    const sorted = Object.entries(bookMap).sort((a, b) => b[1] - a[1]);
    const top30 = sorted.slice(0, 30), totalRev = sorted.reduce((s, e) => s + e[1], 0);
    let cum = 0;
    const cumPcts = top30.map(([, v]) => {{ cum += v; return (cum / totalRev) * 100; }});
    let cutoffSum = 0, cutoffIdx = 0;
    for (let i = 0; i < sorted.length; i++) {{ cutoffSum += sorted[i][1]; if ((cutoffSum / totalRev) * 100 >= 80) {{ cutoffIdx = i; break; }} }}
    const pctBooks80 = ((cutoffIdx + 1) / sorted.length * 100).toFixed(1);
    document.getElementById('paretoResult').innerHTML = '📈 <strong>Resultado Pareto:</strong> El <strong>' + pctBooks80 + '%</strong> de los títulos (' + (cutoffIdx + 1) + ' de ' + sorted.length + ') genera el <strong>80%</strong> de tus ventas. Mantener inventario impecable de estos títulos core es crítico para el flujo de caja.';
    destroyChart('chartPareto');
    charts.chartPareto = new Chart(document.getElementById('chartPareto'), {{
        type: 'bar', data: {{ labels: top30.map((e, i) => '#' + (i + 1)),
            datasets: [{{ label: 'Ventas (USD)', data: top30.map(e => e[1]), backgroundColor: '#6C5CE7AA', borderColor: '#6C5CE7', borderWidth: 1, borderRadius: 4, yAxisID: 'y', order: 2 }},
                {{ label: '% Acumulado', data: cumPcts, type: 'line', borderColor: '#E17055', backgroundColor: 'transparent', borderWidth: 2.5, pointRadius: 0, pointHoverRadius: 4, tension: 0.3, yAxisID: 'y2', order: 1 }}] }},
        options: {{ responsive: true, maintainAspectRatio: false,
            plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ family: 'Inter', size: 11 }}, padding: 14, usePointStyle: true }} }},
                tooltip: {{ backgroundColor: '#1B1F3B', titleFont: {{ family: 'Inter', weight: '600' }}, bodyFont: {{ family: 'Inter' }}, padding: 12, cornerRadius: 8,
                    callbacks: {{ title: ctx => top30[ctx[0].dataIndex]?.[0] || '', label: ctx => ctx.datasetIndex === 0 ? 'Ventas: $' + formatNum(ctx.parsed.y) : 'Acumulado: ' + ctx.parsed.y.toFixed(1) + '%' }} }} }},
            scales: {{ x: {{ grid: {{ display: false }}, ticks: {{ font: {{ family: 'Inter', size: 10 }} }} }},
                y: {{ grid: {{ color: 'rgba(0,0,0,0.04)' }}, ticks: {{ font: {{ family: 'Inter', size: 11 }}, callback: v => '$' + (v >= 1000 ? (v/1000).toFixed(0) + 'K' : v) }} }},
                y2: {{ position: 'right', min: 0, max: 105, grid: {{ display: false }}, ticks: {{ font: {{ family: 'Inter', size: 11 }}, callback: v => v + '%' }} }} }} }}
    }});
}}

function renderDias(filtered) {{
    const dayOrder = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
    const dayMap = {{}};
    filtered.forEach(r => {{ dayMap[r.dia_semana] = (dayMap[r.dia_semana] || 0) + r.total; }});
    const labels = dayOrder.filter(d => dayMap[d] !== undefined), values = labels.map(d => dayMap[d] || 0);
    let peakDay = labels[0], peakVal = 0;
    labels.forEach((d, i) => {{ if (values[i] > peakVal) {{ peakVal = values[i]; peakDay = d; }} }});
    document.getElementById('insightDias').innerHTML = '<strong>🛒 Día de mayor afluencia: ' + peakDay + '</strong>Considerar lanzamiento de promociones relámpago a mitad de semana (Martes/Miércoles) para suavizar la estacionalidad semanal.';
    const barColors = labels.map(d => d === peakDay ? '#6C5CE7' : '#A29BFE88');
    destroyChart('chartDias');
    charts.chartDias = new Chart(document.getElementById('chartDias'), {{
        type: 'bar', data: {{ labels, datasets: [{{ data: values, backgroundColor: barColors, borderColor: labels.map(d => d === peakDay ? '#5A4BD1' : '#A29BFE'), borderWidth: 1, borderRadius: 6, barThickness: 36 }}] }},
        options: {{ responsive: true, maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }}, tooltip: {{ backgroundColor: '#1B1F3B', titleFont: {{ family: 'Inter', weight: '600' }}, bodyFont: {{ family: 'Inter' }}, padding: 12, cornerRadius: 8,
                callbacks: {{ label: ctx => 'Ventas: $' + formatNum(ctx.parsed.y) }} }} }},
            scales: {{ x: {{ grid: {{ display: false }}, ticks: {{ font: {{ family: 'Inter', size: 12, weight: '500' }} }} }},
                y: {{ grid: {{ color: 'rgba(0,0,0,0.04)' }}, ticks: {{ font: {{ family: 'Inter', size: 11 }}, callback: v => '$' + (v >= 1000 ? (v/1000).toFixed(0) + 'K' : v) }} }} }} }}
    }});
}}

function formatNum(n) {{ return n.toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }}); }}
function formatInt(n) {{ return n.toLocaleString('en-US'); }}
function destroyChart(id) {{ if (charts[id]) {{ charts[id].destroy(); delete charts[id]; }} }}

function setupScrollSpy() {{
    const sections = ['overview', 'revenue', 'operations', 'trends', 'pareto'];
    const links = document.querySelectorAll('.sidebar-nav a');
    window.addEventListener('scroll', () => {{
        let current = 'overview';
        sections.forEach(id => {{ const el = document.getElementById(id); if (el && window.scrollY >= el.offsetTop - 120) current = id; }});
        links.forEach(a => {{ a.classList.toggle('active', a.getAttribute('href') === '#' + current); }});
    }});
}}
</script>
</body>
</html>'''

# ─── 4. Write output ────────────────────────────────────────────────────────
os.makedirs("docs", exist_ok=True)
output_path = os.path.join("docs", "index.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[OK] Dashboard generated successfully: {output_path}")
print(f"   Records embedded: {len(records):,}")
print(f"   Genres: {len(genres)}")
print(f"   Payment methods: {len(payment_methods)}")
print(f"   Date range: {min_date} to {max_date}")
