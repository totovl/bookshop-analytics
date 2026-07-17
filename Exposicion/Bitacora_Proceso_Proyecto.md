# Bitácora de Proceso: BookShop Analytics BI Project 📚📊

Este documento detalla la metodología de punta a punta empleada para la concepción, desarrollo, optimización y publicación del proyecto **BookShop Analytics**, sirviendo como registro de la evolución del proyecto y su arquitectura final.

---

## 🧭 1. Concepción del Problema de Negocio
Todo proyecto de Business Intelligence eficaz nace de la necesidad de responder preguntas críticas y resolver ineficiencias de negocio mediante los datos. En el sector minorista de libros (*book retail*), los desafíos típicos identificados fueron:

1. **Gestión de Stock Ineficiente:** Dificultad para predecir qué títulos o géneros requieren reposición inmediata, ocasionando pérdidas de venta por quiebre de stock (*out-of-stock*) o exceso de inventario inmovilizado.
2. **Fuga Financiera por Comisiones:** Falta de visibilidad sobre los costos implícitos al procesar diferentes canales de cobro (Tarjetas, Mercado Pago, etc.).
3. **Pérdida de Contexto Macroeconómico:** Necesidad de visualizar el rendimiento comercial tanto en moneda local (ARS) con inflación/tipo de cambio variable, como en una moneda fuerte estable de comparación (USD), sin alterar el sistema de base de datos original.
4. **Planificación de Campañas:** Ausencia de datos claros sobre estacionalidad (meses fuertes) y patrones semanales (días de mayor afluencia) para programar promociones y distribución del personal.

---

## 🗄️ 2. Generación e Invención del Dataset
Para resolver este problema sin comprometer datos confidenciales, se diseñó un pipeline de simulación de datos transaccionales altamente realista en Python (`generar_ventas_libreria.py`).

*   **Fundamento de Mercado:** Las variables de tendencia, peso de géneros y estacionalidad se basaron en estudios reales de mercado editorial global y regional de fuentes como **Circana BookScan**, **Publishers Weekly** y **Statista** (periodo 2024-2026).
*   **Composición del Dataset:**
    *   **Volumen:** ~12,000 transacciones simuladas entre el 1 de enero de 2025 y el 30 de junio de 2026.
    *   **Dimensiones:** 12 géneros literarios diferenciados (ej. *Romantasy* y *Manga* al alza; *Autoayuda* y *Negocios* a la baja), 100 títulos realistas con precios unitarios parametrizados y 5 métodos de pago (Efectivo, MP, Débito, Crédito, Transferencia).
    *   **Reglas de Simulación:** El script inyectó de manera probabilística picos estacionales de ventas (Navidad, inicio de clases), correlaciones de volumen de compra por transacción (descuentos por cantidad) y tasas de comisiones por método de pago.

---

## 🔄 3. Comprensión y Normalización de Datos
El dataset generado fue sometido a un proceso de limpieza y preparación lógica para asegurar cálculos precisos y veloces:
*   **Estandarización de Fechas:** Las marcas temporales se normalizaron a formato estándar `YYYY-MM-DD`.
*   **Tratamiento de Comisiones:** Se mapearon los aranceles específicos cobrados por las pasarelas de pago:
    *   *Efectivo:* 0% · *Transferencia:* 0.1% · *Débito:* 1.2% · *Crédito:* 2.5% · *Mercado Pago:* 3.5%
*   **Estructura de Datos Indexable:** Se generó un archivo final `ventas_libreria_completo.csv` optimizado para lectura en memoria.

---

## 🏷️ 4. Definición de Métricas y Reglas de Negocio (KPIs)
Se establecieron fórmulas matemáticas y criterios analíticos alineados con la toma de decisiones:
*   **Ingresos Totales (ARS / USD):** Calculados dinámicamente según la moneda seleccionada. Si la moneda activa es ARS, los ingresos base (en USD en la base) se multiplican por un tipo de cambio regulable (`exchangeRate`).
*   **Ticket Promedio:** $\text{Ingresos Totales} \div \text{Cantidad de Transacciones Únicas}$.
*   **Regla de Pareto (80/20):** Algoritmo para identificar qué porcentaje de títulos del catálogo genera el 80% de la facturación histórica, categorizando el valor estratégico del catálogo.
*   **Regla de Reposición Prioritaria:** Alerta para sugerir un factor de **1.5x de stock de seguridad** para títulos de alta rotación durante los periodos estacionales más críticos (noviembre/diciembre).
*   **Crecimiento Trimestral MoM:** Clasificación del porcentaje de crecimiento mensual por categoría para determinar tendencias inmediatas.

---

## 💻 5. Fase de Prototipado: Streamlit y Repositorio Privado
Para la primera iteración rápida del dashboard se utilizó el framework **Streamlit** en Python (`dashboard_bookshop.py`).

*   **Interactividad:** Se implementó mediante gráficos interactivos de **Plotly** (Líneas de evolución, Donut de pasarelas, Pareto y Heatmap de estacionalidad).
*   **Entorno de Nube:** El código se consolidó en un repositorio privado en **GitHub**, lo que facilitó el acceso remoto, pruebas en múltiples dispositivos y la colaboración segura manteniendo protegidos los scripts y los datos crudos del negocio.

---

## 🚀 6. Fase de Producción: Dashboard Estático y GitHub Pages
Para presentar el proyecto de manera pública y profesional como pieza clave de portafolio (evitando los límites de tiempo de inactividad de las plataformas de hosting de Python gratuitas), se migró el dashboard a una arquitectura estática sin servidor.

### Arquitectura Técnica
1.  **Motor de Compilación (`build_dashboard.py`):** Un script en Python encargado de cargar los datos de `ventas_libreria_completo.csv`, serializar el contenido a JSON embebido y compilar un único archivo auto-contenido: `docs/index.html`.
2.  **Tecnologías Frontend:**
    *   **HTML5 Semántico:** Para una correcta accesibilidad y estructura (SEO Optimizado).
    *   **Vanilla CSS:** Layout adaptativo basado en CSS Grid y Flexbox.
    *   **Chart.js (v4):** Librería JavaScript ligera y rápida para la renderización de los gráficos interactivos del lado del cliente.
    *   **Vanilla JS:** Manejo lógico de filtros reactivos en tiempo real (Fechas, Categoría, Método de Pago, Moneda y Cotización) sobre el JSON embebido, evitando peticiones de backend.
3.  **Despliegue Continuo (CI):** Alojado en **GitHub Pages**, ofreciendo tiempos de respuesta de milisegundos y disponibilidad del 100% de manera gratuita.

### Rediseño UX/UI Reciente
*   **Single-Page Web Layout:** El layout se adaptó recientemente a una vista continua de desplazamiento vertical fluido dividido en 3 grandes secciones:
    1.  *Hero/KPIs:* Título, barra interactiva de filtros y tarjetas de KPIs consolidados.
    2.  *Análisis Principal:* Tendencias de evolución de facturación y análisis de stock/operaciones prioritarias.
    3.  *Análisis Secundario:* Comportamientos semanales, mapa de calor estacional y análisis de concentración de catálogo (Pareto).
*   **Ajustes de Alturas:** Ajuste fino de alturas para todos los `canvas` y tablas con el fin de evitar scrollbars internos molestos dentro de las tarjetas.
*   **Estética Minimalista:** Paleta refinada basada en fondos limpios blancos/grisáceos y acentos en azul corporativo moderno (`#2563EB`) para garantizar legibilidad, profesionalidad y contraste.
*   **Conversor de Moneda Reactivo:** Slider/Selector dinámico integrado directamente en la barra de filtros del cliente para ajustar la cotización del dólar y recalcular instantáneamente todas las visualizaciones numéricas de ingresos y tickets promedio.

---

## 📄 7. Informe y Comunicación con Stakeholders
Una vez consolidadas las visualizaciones, se procedió a documentar formalmente las conclusiones clave del negocio para la gerencia general:
*   **Informe de BI:** Se compiló un reporte en PDF (`Exposicion/Reporte_BI_BookShop_Analytics.pdf`) con resúmenes ejecutivos, problemas clave (ej. costo por comisiones en Mercado Pago de 3.5%, reposición necesaria de Bestsellers) y soluciones estratégicas sugeridas.
*   **Presentación Interactiva en Gamma:** Este informe ejecutivo fue procesado a través de la herramienta **Gamma App** para generar una presentación visual moderna, interactiva y dinámica, ideal para reuniones con inversionistas y directivos de la distribuidora.

---

## 🏁 Conclusión del Proyecto
El proyecto **BookShop Analytics** demuestra con éxito el ciclo de vida completo de una solución de inteligencia de negocios:

1. **Identificar Problema de Negocio**
2. **Crear/Preprocesar Datos**
3. **Definir Reglas y Métricas en Python**
4. **Prototipar en Streamlit**
5. **Compilar a Dashboard Estático Ligero**
6. **Publicar en GitHub Pages**
7. **Generar Reporte y Exposición en Gamma**

La combinación de una sólida lógica de negocio, optimización técnica frontend (sin backend) y comunicación estratégica garantiza que los tomadores de decisiones puedan extraer insights valiosos e inmediatos para guiar el rumbo de la librería en el periodo fiscal en curso.

---
*Bitácora de Desarrollo del Portafolio Profesional · BookShop Analytics 2026.*
