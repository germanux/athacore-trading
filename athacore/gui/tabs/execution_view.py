from nicegui import ui
from athacore.core.execution.order_executor_2 import execute_order
import asyncio


def render_execution_view():
    with ui.column().classes('p-4'):
        symbol_input = ui.input('Símbolo').props('outlined')
        quantity_input = ui.number('Cantidad', value=10).props('outlined')
        status_label = ui.label()

        def enviar_orden(tipo):
            async def handler():
                try:
                    resultado = await execute_order(
                        symbol=symbol_input.value,
                        action=tipo,
                        quantity=int(quantity_input.value),
                        mode='real'
                    )
                    status_label.set_text(f'✅ {resultado}')
                except Exception as e:
                    status_label.set_text(f'Error: {e}')
            return handler

        #ui.button('Comprar', on_click= enviar_orden('BUY'))
        #ui.button('Vender', on_click= enviar_orden('SELL'))

        ui.button('Comprar', on_click=lambda: asyncio.create_task(enviar_orden('BUY')()))
        ui.button('Vender', on_click=lambda: asyncio.create_task(enviar_orden('SELL')()))