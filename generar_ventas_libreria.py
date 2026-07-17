"""
===============================================================================
 PIPELINE DE GENERACIÓN DE DATOS TRANSACCIONALES - LIBRERÍA BOOKSHOP
 ===============================================================================
 Autor: Pipeline generado con investigación de mercado editorial 2024-2026
 Fuentes: Circana BookScan, Publishers Weekly, Statista, Mordor Intelligence
 
 Este script genera un dataset de ventas simuladas altamente realista para
 alimentar un dashboard de Power BI de portafolio profesional.
===============================================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ─── Semilla para reproducibilidad ───────────────────────────────────────────
np.random.seed(42)
random.seed(42)

# =============================================================================
# 1. DEFINICIÓN DE CATEGORÍAS / GÉNEROS (12 categorías basadas en investigación)
# =============================================================================
# Tendencia: "alza", "estable", "descenso"
# Basado en datos reales de Circana BookScan 2024-2025

GENEROS_INFO = {
    "Fantasía / Romantasy": {
        "tendencia": "alza",
        "peso_base": 0.14,       # Cuota de mercado base
        "crecimiento_mensual": 0.008,  # Incremento mensual de cuota
    },
    "Romance": {
        "tendencia": "alza",
        "peso_base": 0.12,
        "crecimiento_mensual": 0.005,
    },
    "Ciencia Ficción": {
        "tendencia": "alza",
        "peso_base": 0.09,
        "crecimiento_mensual": 0.006,
    },
    "Manga / Novela Gráfica": {
        "tendencia": "alza",
        "peso_base": 0.10,
        "crecimiento_mensual": 0.007,
    },
    "Thriller / Suspense": {
        "tendencia": "estable",
        "peso_base": 0.10,
        "crecimiento_mensual": -0.001,
    },
    "Distopía / Especulativa": {
        "tendencia": "alza",
        "peso_base": 0.05,
        "crecimiento_mensual": 0.004,
    },
    "Infantil": {
        "tendencia": "estable",
        "peso_base": 0.08,
        "crecimiento_mensual": 0.001,
    },
    "Young Adult": {
        "tendencia": "descenso",
        "peso_base": 0.07,
        "crecimiento_mensual": -0.002,
    },
    "Autoayuda / Desarrollo Personal": {
        "tendencia": "descenso",
        "peso_base": 0.07,
        "crecimiento_mensual": -0.004,
    },
    "Religión / Espiritualidad": {
        "tendencia": "alza",
        "peso_base": 0.06,
        "crecimiento_mensual": 0.003,
    },
    "Biografía / Memorias": {
        "tendencia": "descenso",
        "peso_base": 0.06,
        "crecimiento_mensual": -0.003,
    },
    "Negocios / Técnicos": {
        "tendencia": "descenso",
        "peso_base": 0.06,
        "crecimiento_mensual": -0.003,
    },
}

# =============================================================================
# 2. CATÁLOGO DE LIBROS (100 títulos ficticios pero realistas)
# =============================================================================
# Precios basados en rangos reales del mercado (USD)
# Formato: (Título, Precio_Unitario)

CATALOGO = {
    # ── FANTASÍA / ROMANTASY (12 títulos) ────────────────────────────────────
    "Fantasía / Romantasy": [
        ("El Trono de Cenizas Eternas", 24.99),
        ("Corte de Espinas y Sombras", 22.99),
        ("La Heredera del Viento Oscuro", 18.99),
        ("Pacto de Sangre y Estrellas", 19.99),
        ("El Último Hechicero de Aldara", 17.99),
        ("Reinos de Cristal Roto", 23.99),
        ("La Marca del Fénix Plateado", 21.99),
        ("Crónicas del Mar Encantado", 16.99),
        ("El Jardín de las Brujas Perdidas", 18.99),
        ("Fuego en la Corte de Hielo", 25.99),
        ("La Canción del Dragón Dormido", 20.99),
        ("Sombras Bajo la Luna Roja", 19.99),
    ],
    # ── ROMANCE (10 títulos) ─────────────────────────────────────────────────
    "Romance": [
        ("Volver a Quererte en Otoño", 15.99),
        ("Cartas que Nunca Envié", 16.99),
        ("El Café de los Corazones Rotos", 14.99),
        ("Promesas Bajo la Lluvia", 17.99),
        ("Cuando el Destino Insiste", 15.99),
        ("Mareas de Verano", 13.99),
        ("El Último Beso en París", 18.99),
        ("Junto al Fuego de Diciembre", 16.99),
        ("Tal Vez Mañana", 14.99),
        ("La Librería de los Sueños Compartidos", 17.99),
    ],
    # ── CIENCIA FICCIÓN (9 títulos) ──────────────────────────────────────────
    "Ciencia Ficción": [
        ("Código Génesis: Protocolo IA", 24.99),
        ("La Última Colonia de Marte", 22.99),
        ("Ecos del Futuro Perdido", 19.99),
        ("Neurolink: El Despertar", 26.99),
        ("Horizonte Cuántico", 21.99),
        ("La Singularidad de Vega", 23.99),
        ("Exoplaneta Siete", 18.99),
        ("Máquinas que Sueñan", 20.99),
        ("El Algoritmo de la Conciencia", 25.99),
    ],
    # ── MANGA / NOVELA GRÁFICA (10 títulos) ──────────────────────────────────
    "Manga / Novela Gráfica": [
        ("Kaze no Senshi Vol. 1", 12.99),
        ("Tsuki Academy Vol. 3", 11.99),
        ("Akira Reborn: Edición Integral", 29.99),
        ("El Clan de la Serpiente Dorada Vol. 2", 13.99),
        ("Yūrei: Espíritus Errantes Vol. 1", 10.99),
        ("Cyberpunk Shibuya", 14.99),
        ("Samurai Nocturno Vol. 5", 12.99),
        ("Hana no Kokoro Vol. 1", 11.99),
        ("Neon District: Año Cero", 15.99),
        ("Mecha Warriors: Amanecer Vol. 4", 13.99),
    ],
    # ── THRILLER / SUSPENSE (9 títulos) ──────────────────────────────────────
    "Thriller / Suspense": [
        ("La Habitación 217", 18.99),
        ("Nadie Sale Inocente", 16.99),
        ("El Testigo Silencioso", 19.99),
        ("Tres Días para Morir", 17.99),
        ("La Mujer del Espejo Roto", 21.99),
        ("Secretos en la Niebla", 15.99),
        ("El Pacto del Silencio", 18.99),
        ("Oscuridad al Mediodía", 16.99),
        ("La Verdad Detrás del Fuego", 20.99),
    ],
    # ── DISTOPÍA / ESPECULATIVA (6 títulos) ──────────────────────────────────
    "Distopía / Especulativa": [
        ("El Año en que Callaron las Máquinas", 19.99),
        ("Ciudadanos de Segunda", 17.99),
        ("La República del Silencio", 21.99),
        ("Zona de Exclusión", 18.99),
        ("2084: El Nuevo Orden", 22.99),
        ("Utopía Fracturada", 16.99),
    ],
    # ── INFANTIL (8 títulos) ─────────────────────────────────────────────────
    "Infantil": [
        ("Las Aventuras de Lila y el Gato Mágico", 12.99),
        ("El Bosque de los Animales Parlantes", 14.99),
        ("Mi Primer Atlas del Universo", 18.99),
        ("Cuentos para Soñar Despierto", 11.99),
        ("Dino Rex y la Isla Misteriosa", 13.99),
        ("La Princesa que Quería Ser Astronauta", 12.99),
        ("El Robot Amigable de Tomás", 10.99),
        ("Colores del Mundo: Un Viaje Ilustrado", 16.99),
    ],
    # ── YOUNG ADULT (7 títulos) ──────────────────────────────────────────────
    "Young Adult": [
        ("El Verano que Cambió Todo", 16.99),
        ("Nosotros, los Invisibles", 14.99),
        ("Código de Silencio en el Instituto", 15.99),
        ("La Chica del Último Vagón", 13.99),
        ("Más Allá de las Estrellas (YA)", 17.99),
        ("Rebeldes sin Señal", 14.99),
        ("Días de Cristal y Acero", 16.99),
    ],
    # ── AUTOAYUDA / DESARROLLO PERSONAL (8 títulos) ──────────────────────────
    "Autoayuda / Desarrollo Personal": [
        ("Despierta Tu Mejor Versión", 19.99),
        ("Hábitos de Titanio", 22.99),
        ("La Mente Imparable", 18.99),
        ("Finanzas Personales para Mortales", 21.99),
        ("El Arte de Soltar y Avanzar", 17.99),
        ("Ansiedad Cero: Guía Práctica", 20.99),
        ("Liderazgo Silencioso", 23.99),
        ("Minimalismo Emocional", 16.99),
    ],
    # ── RELIGIÓN / ESPIRITUALIDAD (7 títulos) ────────────────────────────────
    "Religión / Espiritualidad": [
        ("Biblia de Estudio Contemporánea", 39.99),
        ("Camino de Luz Interior", 16.99),
        ("365 Devocionales para el Alma", 18.99),
        ("Meditaciones del Peregrino", 14.99),
        ("Fe en Tiempos Modernos", 19.99),
        ("El Diario de Gratitud Espiritual", 12.99),
        ("Sabiduría Ancestral para Hoy", 17.99),
    ],
    # ── BIOGRAFÍA / MEMORIAS (7 títulos) ─────────────────────────────────────
    "Biografía / Memorias": [
        ("Contra Todo Pronóstico: Mi Historia", 26.99),
        ("El Inventor que Cambió el Mundo", 28.99),
        ("Memorias de un Chef Callejero", 22.99),
        ("La Música en Mis Venas", 24.99),
        ("De la Favela a las Estrellas", 21.99),
        ("Vida de una Activista Silenciosa", 19.99),
        ("El Legado del Abuelo Navegante", 23.99),
    ],
    # ── NEGOCIOS / TÉCNICOS (7 títulos) ──────────────────────────────────────
    "Negocios / Técnicos": [
        ("Inteligencia Artificial para Directivos", 32.99),
        ("Estrategia Digital 360°", 29.99),
        ("Data Science: De Cero a Experto", 39.99),
        ("El Nuevo Marketing: Era de la IA", 27.99),
        ("Emprender en Latinoamérica 2025", 24.99),
        ("Blockchain y Finanzas Descentralizadas", 34.99),
        ("Gestión Ágil de Proyectos Reales", 28.99),
    ],
}


# =============================================================================
# 3. PARÁMETROS DE SIMULACIÓN
# =============================================================================

FECHA_INICIO = datetime(2025, 1, 1)
FECHA_FIN = datetime(2026, 6, 30)
TOTAL_TRANSACCIONES_OBJETIVO = 12500  # ~12,500 transacciones (dentro del rango 10k-15k)

METODOS_PAGO = [
    "Tarjeta de Crédito",
    "Tarjeta de Débito",
    "Efectivo",
    "Mercado Pago",
    "Transferencia",
]
PESO_METODOS_PAGO = [0.30, 0.25, 0.20, 0.15, 0.10]

# Distribución de cantidad por transacción: mayormente 1, ocasionalmente 2 o 3
CANTIDADES = [1, 2, 3]
PESO_CANTIDADES = [0.78, 0.17, 0.05]


# =============================================================================
# 4. FUNCIONES DE LÓGICA TEMPORAL Y TENDENCIAS
# =============================================================================

def calcular_multiplicador_estacional(fecha):
    """
    Calcula un multiplicador de volumen de ventas basado en estacionalidad.
    - Diciembre (Navidad): pico máximo (~2.2x)
    - Noviembre (Black Friday): repunte (~1.5x)
    - Junio-Julio (vacaciones de invierno en LatAm / verano en US): repunte (~1.3x)
    - Febrero: mes más bajo (~0.75x)
    - Fines de semana: +40% sobre el volumen del día
    """
    mes = fecha.month
    dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo

    # ── Multiplicador mensual base ───────────────────────────────────────
    multiplicadores_mes = {
        1: 0.85,   # Enero: post-navidad, baja
        2: 0.75,   # Febrero: mes más bajo
        3: 0.90,   # Marzo: recuperación gradual
        4: 0.95,   # Abril: estable
        5: 1.00,   # Mayo: Día de la Madre, leve repunte
        6: 1.15,   # Junio: vacaciones
        7: 1.25,   # Julio: vacaciones de invierno
        8: 0.95,   # Agosto: vuelta a la normalidad
        9: 1.00,   # Septiembre: vuelta al cole
        10: 1.05,  # Octubre: pre-navidad lento
        11: 1.40,  # Noviembre: Black Friday / CyberMonday
        12: 2.20,  # Diciembre: Navidad, pico máximo
    }
    mult = multiplicadores_mes.get(mes, 1.0)

    # ── Picos específicos dentro del mes ─────────────────────────────────
    dia = fecha.day

    # Semana de Navidad (15-25 Dic): pico extra
    if mes == 12 and 15 <= dia <= 25:
        mult *= 1.25

    # Black Friday (última semana de noviembre)
    if mes == 11 and dia >= 22:
        mult *= 1.20

    # Día de San Valentín
    if mes == 2 and 10 <= dia <= 14:
        mult *= 1.30

    # Día del Libro (23 de abril)
    if mes == 4 and 20 <= dia <= 23:
        mult *= 1.35

    # Día de la Madre (segundo domingo de mayo aprox)
    if mes == 5 and 8 <= dia <= 14:
        mult *= 1.15

    # ── Multiplicador de fin de semana (+40%) ────────────────────────────
    if dia_semana >= 5:  # Sábado o Domingo
        mult *= 1.40

    return mult


def calcular_pesos_genero_mes(mes_offset):
    """
    Calcula los pesos de cada género para un mes dado (0 = Enero 2025).
    Los géneros 'en alza' ganan cuota progresivamente.
    Los géneros 'en descenso' pierden cuota progresivamente.
    Se normaliza para que los pesos sumen 1.0.
    """
    pesos = {}
    for genero, info in GENEROS_INFO.items():
        peso = info["peso_base"] + (info["crecimiento_mensual"] * mes_offset)
        # Asegurar que nunca baje de un mínimo del 2%
        peso = max(peso, 0.02)
        pesos[genero] = peso

    # Normalizar para que sumen 1.0
    total = sum(pesos.values())
    for genero in pesos:
        pesos[genero] /= total

    return pesos


def calcular_ventas_diarias_base():
    """
    Calcula el volumen base diario para alcanzar el objetivo total.
    Total objetivo / días totales = base, luego se ajusta por estacionalidad.
    """
    total_dias = (FECHA_FIN - FECHA_INICIO).days + 1
    # Calculamos el multiplicador promedio esperado para ajustar la base
    multiplicadores = []
    fecha = FECHA_INICIO
    while fecha <= FECHA_FIN:
        multiplicadores.append(calcular_multiplicador_estacional(fecha))
        fecha += timedelta(days=1)

    mult_promedio = np.mean(multiplicadores)
    base_diaria = TOTAL_TRANSACCIONES_OBJETIVO / (total_dias * mult_promedio)
    return base_diaria


# =============================================================================
# 5. GENERACIÓN DE TRANSACCIONES
# =============================================================================

def generar_transacciones():
    """
    Motor principal de generación de datos transaccionales.
    """
    print("=" * 70)
    print(" PIPELINE DE GENERACIÓN - BOOKSHOP TRANSACTIONAL DATA")
    print("=" * 70)
    print()

    # ── Calcular volumen base diario ─────────────────────────────────────
    base_diaria = calcular_ventas_diarias_base()
    print(f"📊 Volumen base diario calculado: {base_diaria:.1f} transacciones")

    # ── Preparar catálogo plano ──────────────────────────────────────────
    catalogo_plano = {}
    total_titulos = 0
    for genero, libros in CATALOGO.items():
        catalogo_plano[genero] = libros
        total_titulos += len(libros)
    print(f"📚 Catálogo cargado: {total_titulos} títulos en {len(CATALOGO)} géneros")

    # ── Generar transacciones día a día ──────────────────────────────────
    transacciones = []
    id_counter = 10001
    fecha_actual = FECHA_INICIO

    while fecha_actual <= FECHA_FIN:
        # Calcular el offset de meses desde el inicio
        mes_offset = (fecha_actual.year - FECHA_INICIO.year) * 12 + \
                     (fecha_actual.month - FECHA_INICIO.month)

        # Obtener multiplicador estacional y pesos de género para este mes
        mult_estacional = calcular_multiplicador_estacional(fecha_actual)
        pesos_genero = calcular_pesos_genero_mes(mes_offset)

        # Número de transacciones para este día (con variación aleatoria ±15%)
        n_transacciones = int(base_diaria * mult_estacional)
        n_transacciones = max(1, int(n_transacciones * np.random.uniform(0.85, 1.15)))

        # Generar cada transacción del día
        generos_lista = list(pesos_genero.keys())
        generos_pesos = list(pesos_genero.values())

        for _ in range(n_transacciones):
            # Seleccionar género ponderado
            genero = np.random.choice(generos_lista, p=generos_pesos)

            # Seleccionar libro aleatorio dentro del género
            libros_genero = catalogo_plano[genero]
            titulo, precio_unitario = random.choice(libros_genero)

            # Variación de precio leve (±3%) para simular ediciones/descuentos
            precio_final = round(precio_unitario * np.random.uniform(0.97, 1.03), 2)

            # Cantidad (mayormente 1)
            cantidad = np.random.choice(CANTIDADES, p=PESO_CANTIDADES)

            # Total
            total = round(precio_final * cantidad, 2)

            # Método de pago
            metodo_pago = np.random.choice(METODOS_PAGO, p=PESO_METODOS_PAGO)

            # Agregar transacción
            transacciones.append({
                "ID_Transaccion": f"T-{id_counter}",
                "Fecha": fecha_actual.strftime("%Y-%m-%d"),
                "Titulo": titulo,
                "Genero": genero,
                "Precio_Unitario": precio_final,
                "Cantidad": int(cantidad),
                "Total_Transaccion": total,
                "Metodo_Pago": metodo_pago,
            })
            id_counter += 1

        fecha_actual += timedelta(days=1)

    # ── Crear DataFrame ──────────────────────────────────────────────────
    df = pd.DataFrame(transacciones)
    print(f"✅ Transacciones generadas: {len(df):,}")
    print()

    return df


# =============================================================================
# 6. EXPORTACIÓN Y REPORTE
# =============================================================================

def exportar_y_reportar(df):
    """
    Exporta el DataFrame a CSV y genera un reporte estadístico.
    """
    # ── Exportar CSV ─────────────────────────────────────────────────────
    ruta_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "ventas_libreria_completo.csv")
    df.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
    print(f"💾 Archivo CSV guardado en: {ruta_csv}")
    print()

    # ── Reporte estadístico ──────────────────────────────────────────────
    print("=" * 70)
    print(" REPORTE ESTADÍSTICO DEL DATASET GENERADO")
    print("=" * 70)
    print()

    facturacion_total = df["Total_Transaccion"].sum()
    print(f"📈 Total de filas (transacciones): {len(df):,}")
    print(f"💰 Facturación total simulada:     ${facturacion_total:,.2f} USD")
    print(f"📅 Rango de fechas:                {df['Fecha'].min()} → {df['Fecha'].max()}")
    print(f"💳 Ticket promedio:                ${df['Total_Transaccion'].mean():.2f} USD")
    print(f"📦 Cantidad promedio por txn:       {df['Cantidad'].mean():.2f} unidades")
    print()

    # ── Categorías y su participación ────────────────────────────────────
    print("─" * 50)
    print(" PARTICIPACIÓN POR GÉNERO")
    print("─" * 50)
    genero_stats = df.groupby("Genero").agg(
        Transacciones=("ID_Transaccion", "count"),
        Facturacion=("Total_Transaccion", "sum")
    ).sort_values("Facturacion", ascending=False)

    genero_stats["% Txns"] = (genero_stats["Transacciones"] / len(df) * 100).round(1)
    genero_stats["% Facturación"] = (genero_stats["Facturacion"] / facturacion_total * 100).round(1)
    genero_stats["Facturacion"] = genero_stats["Facturacion"].apply(lambda x: f"${x:,.2f}")
    print(genero_stats.to_string())
    print()

    # ── Métodos de pago ──────────────────────────────────────────────────
    print("─" * 50)
    print(" DISTRIBUCIÓN POR MÉTODO DE PAGO")
    print("─" * 50)
    pago_stats = df["Metodo_Pago"].value_counts()
    for metodo, count in pago_stats.items():
        print(f"  {metodo:<25} {count:>6} txns ({count/len(df)*100:.1f}%)")
    print()

    # ── Muestra de las primeras 5 filas ──────────────────────────────────
    print("─" * 50)
    print(" MUESTRA: PRIMERAS 5 FILAS")
    print("─" * 50)
    print(df.head(5).to_string(index=False))
    print()

    # ── Evolución mensual para verificar tendencias ──────────────────────
    print("─" * 50)
    print(" EVOLUCIÓN MENSUAL DE VENTAS")
    print("─" * 50)
    df_temp = df.copy()
    df_temp["Mes"] = pd.to_datetime(df_temp["Fecha"]).dt.to_period("M")
    mensual = df_temp.groupby("Mes").agg(
        Txns=("ID_Transaccion", "count"),
        Facturacion=("Total_Transaccion", "sum")
    )
    for mes, row in mensual.iterrows():
        barra = "█" * int(row["Txns"] / 30)
        print(f"  {mes}  {row['Txns']:>5} txns  ${row['Facturacion']:>10,.2f}  {barra}")
    print()
    print("=" * 70)
    print(" ✅ PIPELINE COMPLETADO EXITOSAMENTE")
    print("=" * 70)


# =============================================================================
# 7. EJECUCIÓN PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    df = generar_transacciones()
    exportar_y_reportar(df)
