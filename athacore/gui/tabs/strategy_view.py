from nicegui import ui
from athacore.core.strategy.strategy_engine import mostrar_estrategias, run_analysis

def render_strategy_view():
    with ui.card().classes('p-4 w-full'):
        ui.label('🧠 Estrategias de Trading')

        ESTRATEGIAS = list(mostrar_estrategias().keys())

        with ui.row().classes("w-full gap-0"):
            inputs = ui.column().classes("w-1/3")
            with inputs:
                estrategia = ui.select(
                    options=ESTRATEGIAS,
                    label='Selecciona estrategia',
                    value=ESTRATEGIAS[0]
                )
                ticker = ui.input('Ticker (ej: AAPL)').props('outlined')
                start = ui.input('Fecha inicio (YYYY-MM-DD)').props('outlined')
                end = ui.input('Fecha fin (YYYY-MM-DD)').props('outlined')
            output = ui.column().classes("w-2/3")

        def ejecutar():
            try:
                señales = run_analysis(
                    strategy_name=estrategia.value,
                    ticker=ticker.value,
                    start=start.value,
                    end=end.value
                )
                
                # Ajustado datos
                señales["fecha"]=señales["fecha"].astype(str)
                señales_dicc=señales.to_dict(orient="records")

                output.clear()
                with output:
                    ui.label(f'Se generaron {len(señales)} señales:\n').classes("font-bold")
                    ui.table(
                        title = "Listado de señales",
                        columns = [
                            {'name': 'indice', 'label': 'Índice', 'field': 'indice', 'align': 'center'},
                            {'name': 'fecha', 'label': 'Fecha', 'field': 'fecha', 'align': 'left'},
                            {'name': 'volumen', 'label': 'Volumen', 'field': 'volumen', 'align': 'left'},
                            {'name': 'cierre', 'label': 'Precio cierre', 'field': 'cierre', 'align': 'left'},
                            {'name': 'compra', 'label': 'Compra', 'field': 'compra', 'align': 'left'}],
                        rows = señales_dicc,
                        pagination={'rowsPerPage': 10})
                    
            except Exception as e:
                output.set_text(f'Error: {e}')

        with inputs:
            ui.button('Ejecutar estrategia', on_click=ejecutar)
