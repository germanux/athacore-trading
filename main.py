from nicegui import ui

#Libreias que se deberían quitar tras la modularización
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd

from athacore.analisis import principal_analisis
from athacore.decisiones import principal_decisiones
from athacore.ejecucion import principal_ejecucion

#Modularaización de gráficas
from data_view.graficas_isabel import grafica_simple

ESTRATEGIAS = ["estrategia_basica_medias"]
MODOS_EJECUCION = ["simulacion", "real"]

ACTIVOS=["AAPL"]
METODOS_GRAFICAS = ["Simple", "Comparación", "Anual", "Diferecial"]

"""
Gráfica mes a mes total de un activo
Gráfica que compare la evolución de dos activos
Gráfica que muestre un año concreto
Grafica que muestre cuánto creció /decreció (es decir, la diferencia) un activo en un periodo
"""

def ejecutar_analisis(estrategia: str, ticker: str, inicio: str, fin: str):
    principal_analisis.ejecutar_analisis(estrategia, ticker, inicio, fin)
    ui.notify("✅ Análisis lanzado")

def evaluar_ahora(estrategia: str, ticker: str):
    modo = "test"
    principal_decisiones.ejecutar_decision(estrategia, ticker, modo)
    ui.notify("✅ Evaluación lanzada (modo test)")

def ejecutar_estrategia(estrategia: str, ticker: str, modo: str):
    principal_decisiones.ejecutar_decision(estrategia, ticker, modo)
    ui.notify(f"✅ Estrategia lanzada en modo '{modo}'")


# INICIO DE LA INTERFAZ

ui.label("🧠 Panel de control de trading algorítmico").classes("text-2xl mb-4")

with ui.card().classes("w-1/2"):
    ui.label("📊 Análisis de estrategia (histórico)")
    estrategia_1 = ui.select(ESTRATEGIAS, value=ESTRATEGIAS[0])
    ticker_1 = ui.input("Ticker", value="AAPL")
    inicio = ui.input("Fecha inicio (YYYY-MM-DD)", value="2023-01-01")
    fin = ui.input("Fecha fin (YYYY-MM-DD)", value="2023-12-31")
    ui.button("▶️ Analizar", on_click=lambda: ejecutar_analisis(estrategia_1.value, ticker_1.value, inicio.value, fin.value))

with ui.card().classes("w-1/2 mt-6"):
    ui.label("🧪 Evaluar ahora (modo test, no ejecuta)")
    estrategia_2 = ui.select(ESTRATEGIAS, value=ESTRATEGIAS[0])
    ticker_2 = ui.input("Ticker", value="AAPL")
    ui.button("▶️ Evaluar", on_click=lambda: evaluar_ahora(estrategia_2.value, ticker_2.value))

with ui.card().classes("w-1/2 mt-6"):
    ui.label("⚙️ Ejecutar estrategia (simulación o real)")
    estrategia_3 = ui.select(ESTRATEGIAS, value=ESTRATEGIAS[0])
    ticker_3 = ui.input("Ticker", value="AAPL")
    modo_3 = ui.select(MODOS_EJECUCION, value=MODOS_EJECUCION[0])
    ui.button("▶️ Ejecutar", on_click=lambda: ejecutar_estrategia(estrategia_3.value, ticker_3.value, modo_3.value))


with ui.card().classes("w-full mt-6"):
    ui.label("📊 Gráfica simple")
    activo_selecionado = ui.select(ACTIVOS, value=ACTIVOS[0])
    lista_inputs_simple = ui.row()
    with lista_inputs_simple:
        fecha_1 = ui.date("Fecha desde la que quieres empezar el seguimiento")
    contenedor_grafica_simple = ui.row()

    def dibujar_grafica_simple():
        contenedor_grafica_simple.clear()
        with contenedor_grafica_simple:
            grafica_simple(fecha_1.value, activo_selecionado.value)

    ui.button("Generar gráfica", on_click=lambda: dibujar_grafica_simple())

ui.run(title="Panel de Trading Algorítmico")
