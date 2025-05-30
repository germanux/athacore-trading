from nicegui import ui
from athacore.core.strategy.strategy_engine import mostrar_estrategias, run_analysis
from athacore.core.execution.order_executor import execute_order
from datetime import date
import pandas as pd


def render_strategy_view():
    with ui.card().classes('p-4 w-full'):
        ui.label('📈 Estrategias de Trading y Ejecución en IB Gateway').classes('text-2xl font-bold')

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

            output = ui.column().classes("w-2/3")

        def ejecutar():
            if not (estrategia.value and ticker.value and start.value):
                ui.notify("Debes seleccionar estrategia, ticker y fecha de inicio.", type='warning')
                return

            try:
                fecha_fin = date.today().isoformat()

                señales = run_analysis(
                    strategy_name=estrategia.value,
                    ticker=ticker.value.upper(),
                    start=start.value,
                    end=fecha_fin
                )

                if señales.empty:
                    output.clear()
                    with output:
                        ui.label('⚠️ No se generaron señales con los datos seleccionados.').classes('text-yellow-600 font-semibold')
                    return

                # Convertir datetime a string para evitar errores en JSON
                for col in señales.columns:
                    if pd.api.types.is_datetime64_any_dtype(señales[col]):
                        señales[col] = señales[col].astype(str)

                if pd.api.types.is_datetime64_any_dtype(señales.index):
                    señales = señales.reset_index()
                    for col in señales.columns:
                        if pd.api.types.is_datetime64_any_dtype(señales[col]):
                            señales[col] = señales[col].astype(str)

                señales_dicc = señales.to_dict(orient="records")

                output.clear()
                with output:
                    ui.label(f'✅ Estrategia ejecutada: {len(señales_dicc)} señales generadas').classes("font-bold")
                    ui.table(
                        title="📊 Resultado de señales",
                        columns=[
                            {'name': 'indice', 'label': 'Índice', 'field': 'indice', 'align': 'center'},
                            {'name': 'fecha', 'label': 'Fecha', 'field': 'fecha', 'align': 'left'},
                            {'name': 'volumen', 'label': 'Volumen', 'field': 'volumen', 'align': 'left'},
                            {'name': 'cierre', 'label': 'Precio cierre', 'field': 'cierre', 'align': 'left'},
                            {'name': 'compra', 'label': 'Compra', 'field': 'compra', 'align': 'center'},
                            {'name': 'venta', 'label': 'Venta', 'field': 'venta', 'align': 'center'},
                        ],
                        rows=señales_dicc,
                        pagination={'rowsPerPage': 10}
                    )

                    for i, señal in enumerate(señales_dicc):
                        volumen = int(señal.get('volumen', 0))
                        volumen = min(volumen, 1000)  # Límite seguro para evitar errores IBKR

                        if señal.get('compra'):
                            with ui.row().classes('items-center gap-4'):
                                ui.label(f"{i+1}. Recomendación: ✅ COMPRAR {volumen} de {ticker.value.upper()}")

                                def crear_handler_compra(s=señal):
                                    async def handler():
                                        try:
                                            cantidad = min(int(s.get('volumen', 0)), 1000)
                                            resultado = await execute_order(
                                                symbol=ticker.value.upper(),
                                                action="BUY",
                                                quantity=cantidad,
                                                mode='real'
                                            )
                                            ui.notify(resultado, type='success' if 'Orden' in resultado else 'warning')
                                        except Exception as e:
                                            ui.notify(f'❌ Error al ejecutar orden: {e}', type='negative')
                                    return handler

                                ui.button('Ejecutar orden de COMPRA', on_click=crear_handler_compra()).props('color=primary')

                        elif señal.get('venta'):
                            with ui.row().classes('items-center gap-4'):
                                ui.label(f"{i+1}. Recomendación: 🔻 VENDER {volumen} de {ticker.value.upper()}")

                                def crear_handler_venta(s=señal):
                                    async def handler():
                                        try:
                                            cantidad = min(int(s.get('volumen', 0)), 1000)
                                            resultado = await execute_order(
                                                symbol=ticker.value.upper(),
                                                action="SELL",
                                                quantity=cantidad,
                                                mode='real'
                                            )
                                            ui.notify(resultado, type='success' if 'Orden' in resultado else 'warning')
                                        except Exception as e:
                                            ui.notify(f'❌ Error al ejecutar orden: {e}', type='negative')
                                    return handler

                                ui.button('Ejecutar orden de VENTA', on_click=crear_handler_venta()).props('color=negative')

                        else:
                            with ui.row().classes('items-center gap-4'):
                                ui.label(f"{i+1}. Recomendación: 🟡 MANTENER posición en {ticker.value.upper()}")

            except Exception as e:
                output.clear()
                with output:
                    ui.label(f'❌ Error al ejecutar la estrategia: {e}').classes('text-red-600 font-bold')

        with inputs:
            ui.button('Ejecutar estrategia', on_click=ejecutar).props('color=secondary')
