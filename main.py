from nicegui import ui
import subprocess
import os

ESTRATEGIAS = ["estrategia_basica_medias"]
MODOS = ["simulacion", "real", "test"]

def ejecutar_modo(modo: str, estrategia: str):
    os.environ['ESTRATEGIA'] = estrategia
    os.environ['MODO_OPERACION'] = modo

    if modo == "simulacion":
        comando = ["python", "-m", "athacore.analisis.principal_analisis"]
    elif modo == "real":
        comando = ["python", "-m", "athacore.ejecucion.principal_ejecucion"]
    elif modo == "test":
        comando = ["python", "-m", "athacore.decisiones.principal_decisiones"]
    else:
        ui.notify(f"❌ Modo no reconocido: {modo}", type='negative')
        return

    subprocess.Popen(comando)
    ui.notify(f"✅ Modo '{modo}' ejecutado con estrategia '{estrategia}'", type='positive')

ui.label("🧠 Panel de control de trading algorítmico").classes("text-2xl mb-4")

with ui.card().classes("w-1/2"):
    ui.label("📈 Selecciona una estrategia y un modo de operación")
    estrategia = ui.select(ESTRATEGIAS, value=ESTRATEGIAS[0]).classes("mb-4")
    modo = ui.select(MODOS, value=MODOS[0]).classes("mb-4")
    ui.button("▶️ Ejecutar", on_click=lambda: ejecutar_modo(modo.value, estrategia.value))

ui.run(title="Panel de Trading Algorítmico")
