# BookShop Analytics — Interactive BI Dashboard

![Dashboard Preview](https://img.shields.io/badge/Status-Live-brightgreen) ![HTML](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white) ![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?logo=chartdotjs&logoColor=white)

## 📊 About

Interactive Business Intelligence dashboard for a simulated bookshop retail operation. Built as a portfolio piece demonstrating data analysis, visualization, and strategic business insights.

**🔗 [View Live Dashboard](https://totovl.github.io/bookshop-analytics/)**

## Features

- **6 Key Performance Indicators** with period-over-period comparison
- **Interactive Filters**: Date range, literary genre, and payment method
- **Revenue Evolution** by literary category (line chart)
- **Payment Channel Analysis** with commission estimation (doughnut chart)
- **Top 20 Books** demand ranking (horizontal bar chart)
- **Priority Restocking** recommendations table
- **MoM Trend Analysis** with growth classification
- **Seasonality Heatmap** (genre × month)
- **Pareto 80/20 Analysis** of the book portfolio
- **Day-of-Week Sales Patterns** for operational planning
- **Business Insights & Recommendations** throughout

## Tech Stack

- **HTML5 + CSS3** — Responsive layout with Inter font
- **Chart.js v4** — Interactive charts via CDN
- **Vanilla JavaScript** — Client-side data filtering and calculations
- **Python (build script)** — CSV preprocessing and HTML generation

## How It Works

1. `build_dashboard.py` reads the CSV dataset
2. Converts ~12,000 transactions to embedded JSON
3. Generates `docs/index.html` — a fully self-contained dashboard
4. GitHub Pages serves the static HTML

## Local Development

```bash
# Generate the dashboard
python build_dashboard.py

# Open in browser
start docs/index.html
```

## Dataset

Simulated bookshop sales data (Jan 2025 - Jun 2026):
- ~12,000 transactions
- 12 literary genres
- 5 payment methods
- Generated with `generar_ventas_libreria.py`

---

*Built for professional portfolio — Data simulation based on editorial market research 2025-2026.*
