from nicegui import ui
from athacore.core.strategy.strategy_engine import run_analysis


def render_strategy_view():
    with ui.column().classes('p-4'):
        ui.label('🧠 Estrategias de Trading')

        ESTRATEGIAS=['estrategia_basica_medias', 'estrategia_rsi_simple', 'estrategia_macd_cruce']
        estrategia = ui.select(
            options=ESTRATEGIAS,
            label='Selecciona estrategia',
            value=ESTRATEGIAS[0]
        )
        ticker = ui.input('Ticker (ej: AAPL)').props('outlined')
        start = ui.input('Fecha inicio (YYYY-MM-DD)').props('outlined')
        end = ui.input('Fecha fin (YYYY-MM-DD)').props('outlined')
        output = ui.column()

        def ejecutar():
            try:
                señales = run_analysis(
                    strategy_name=estrategia.value,
                    ticker=ticker.value,
                    start=start.value,
                    end=end.value
                )
                
                with output:
                    ui.label(f'Se generaron {len(señales)} señales:\n').classes("font-bold")
                    ui.table(
                        columns = [
                            {'name': 'indice', 'label': 'Índice', 'field': 'indice', 'align': 'center'},
                            {'name': 'fecha', 'label': 'Fecha', 'field': 'fecha', 'align': 'left'},
                            {'name': 'accion', 'label': 'Acción', 'field': 'accion', 'align': 'left'}],
                        rows = [{"indice": index, "fecha": fecha.date(), "accion": accion} for index, fecha, accion in señales])
                    
            except Exception as e:
                output.set_text(f'Error: {e}')

        ui.button('Ejecutar estrategia', on_click=ejecutar)
