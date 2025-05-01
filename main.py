from nicegui import ui
import subprocess
import os

import plotly.graph_objects as go #Version simple
import yfinance as yf
import pandas as pd

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
    os.environ['ESTRATEGIA'] = estrategia
    os.environ['TICKER'] = ticker
    os.environ['FECHA_INICIO'] = inicio
    os.environ['FECHA_FIN'] = fin
    subprocess.Popen(["python", "-m", "athacore.analisis.principal_analisis"])
    ui.notify("✅ Análisis lanzado")

def evaluar_ahora(estrategia: str, ticker: str):
    os.environ['ESTRATEGIA'] = estrategia
    os.environ['TICKER'] = ticker
    os.environ['MODO_OPERACION'] = "test"
    subprocess.Popen(["python", "-m", "athacore.decisiones.principal_decisiones"])
    ui.notify("✅ Evaluación lanzada (modo test)")

def ejecutar_estrategia(estrategia: str, ticker: str, modo: str):
    os.environ['ESTRATEGIA'] = estrategia
    os.environ['TICKER'] = ticker
    os.environ['MODO_OPERACION'] = modo
    subprocess.Popen(["python", "-m", "athacore.decisiones.principal_decisiones"])
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



    """
    
    def actualizar_inputs(event):
        if event.value == "Simple":
            fecha_1 = ui.date("Fecha inicio")
            fecha_2 = ui.date("Fecha inicio")
        elif event.value == "Comparación":
            pass
        elif event.value == "Anual":
            pass
        elif event.value == "Diferecial":
            pass
    fecha_1 = ui.date("Fecha inicio")
    metodo_grafica_selecionada.on_value_change(actualizar_inputs)
    """

with ui.card().classes("w-full mt-6"):
    ui.label("Gráficas")
    metodo_grafica_selecionada = ui.select(METODOS_GRAFICAS, value=METODOS_GRAFICAS[0])
    lista_inputs = ui.row()
    contenedor_graficas = ui.row()

    # Mostrar número de inputs según el tipo de grafica que se quiera
    def actualizar_inputs(event):
        lista_inputs.clear()
    
        if event.value.strip() == "Simple":
            with lista_inputs:
                fecha_1 = ui.date("Fecha desde la que quieres empezar el seguimiento")
            activo_selecionado = ui.select(ACTIVOS, value=ACTIVOS[0])
            ui.button("Generar gráfica", on_click=lambda: grafica_simple(fecha_1.value, activo_selecionado.value))
        elif event.value == "Comparación":
            pass
        elif event.value == "Anual":
            pass
        elif event.value == "Diferecial":
            pass
    actualizar_inputs(metodo_grafica_selecionada)
    metodo_grafica_selecionada.on_value_change(actualizar_inputs)

    """
    GRAFICA SIMPLE DE EJEMPLO
    def primeraGrafica():
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=["2023-01-01", "2024-01-01", "2025-01-01", "2026-01-01"],
            y=[45, -12, 120, 71]
        ))
        ui.plotly(fig).classes("w-full h-100")
    primeraGrafica()
    """
    
    def grafica_simple(fecha_inicio:str, activo:str):
        print(f"Datos pasados a la gráfica:\n- Fecha de inicio: {fecha_inicio}\n- Activo: {activo}")

        fecha_final = "2025-4-1" #Se podria implementar la libreria de datetime para poner la fecha actual
        
        # TOMAR DATOS
        data = yf.download(activo, fecha_inicio, fecha_final)
        data = data.reset_index()

        # Limpiar multinivel
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        #Limpiar gráfica anterior
        contenedor_graficas.clear()

        # CREAR GRÁFICA
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x = data["Date"],
            y = data["Volume"],
        ))
        
        fig.update_layout(
            title=f"Volumen de {activo} entre {fecha_inicio} y {fecha_final}",
            xaxis_title="Fecha",
            yaxis_title="Volumen",
            xaxis=dict(
                tickformat="%Y-%m-%d",
                type="date"
            )
        )
        
        with contenedor_graficas:
            ui.plotly(fig).classes("w-full h-200")
        
        #Prints que he usado para comprobar datos
        print(data)
        print(data["Date"])
        print(data["Volume"])
        print(data.columns)

ui.run(title="Panel de Trading Algorítmico")
