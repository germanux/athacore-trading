from nicegui import ui
from athacore.core.strategy.strategy_engine import mostrar_estrategias, run_analysis
from athacore.core.execution.order_executor import execute_order, send_order_to_ibkr, simulate_order, IBClient  # ✅ IMPORTACIÓN AÑADIDA

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
                modo = ui.select(['simulacion', 'real'], label='Modo ejecución').props('outlined dense')  # ✅ AÑADIDO

            output = ui.column().classes("w-2/3")

        def ejecutar():
            try:
                señales = run_analysis(
                    strategy_name=estrategia.value,
                    ticker=ticker.value,
                    start=start.value,
                    end=end.value
                )

                señales["fecha"] = señales["fecha"].astype(str)
                señales_dicc = señales.to_dict(orient="records")

                output.clear()
                with output:
                    ui.label(f'Se generaron {len(señales)} señales:\n').classes("font-bold")
                    ui.table(
                        title="Listado de señales",
                        columns=[
                            {'name': 'indice', 'label': 'Índice', 'field': 'indice', 'align': 'center'},
                            {'name': 'fecha', 'label': 'Fecha', 'field': 'fecha', 'align': 'left'},
                            {'name': 'volumen', 'label': 'Volumen', 'field': 'volumen', 'align': 'left'},
                            {'name': 'cierre', 'label': 'Precio cierre', 'field': 'cierre', 'align': 'left'},
                            {'name': 'compra', 'label': 'Compra', 'field': 'compra', 'align': 'left'}],
                        rows=señales_dicc,
                        pagination={'rowsPerPage': 10}
                    )

                    # ✅ NUEVO: Sección de ejecución de órdenes si hay señales de compra o venta
                    for i, señal in enumerate(señales_dicc):
                        if señal.get('compra', False):
                            with ui.row().classes('items-center gap-4'):
                                ui.label(f"{i+1}. Ejecutar compra de {señal['volumen']} {ticker.value.upper()}")

                                def crear_handler_compra(s=señal):
                                    async def handler():
                                        resultado = execute_order(
                                            symbol=ticker.value.upper(),
                                            action="BUY",
                                            quantity=int(s['volumen']),
                                            mode=modo.value
                                        )
                                        ui.notify(resultado, type='info' if 'Simulación' in resultado else 'success')
                                    return handler

                                ui.button('Ejecutar orden compra', on_click=crear_handler_compra()).props('color=primary')

                        # Supongamos que la señal de venta está en una columna 'venta' (bool)
                        if señal.get('venta', False):
                            with ui.row().classes('items-center gap-4'):
                                ui.label(f"{i+1}. Ejecutar venta de {señal['volumen']} {ticker.value.upper()}")

                                def crear_handler_venta(s=señal):
                                    async def handler():
                                        resultado = execute_order(
                                            symbol=ticker.value.upper(),
                                            action="SELL",
                                            quantity=int(s['volumen']),
                                            mode=modo.value
                                        )
                                        ui.notify(resultado, type='info' if 'Simulación' in resultado else 'success')
                                    return handler

                                ui.button('Ejecutar orden venta', on_click=crear_handler_venta()).props('color=negative')

            except Exception as e:
                output.clear()
                with output:
                    ui.label(f'Error: {e}').classes('text-red-600 font-bold')

        with inputs:
            ui.button('Ejecutar estrategia', on_click=ejecutar)

