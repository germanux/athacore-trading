from nicegui import ui
import subprocess
import os

ESTRATEGIAS = ["estrategia_basica_medias"]
MODOS_EJECUCION = ["simulacion", "real"]

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

ui.run(title="Panel de Trading Algorítmico")
