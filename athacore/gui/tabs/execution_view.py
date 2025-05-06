from nicegui import ui
from athacore.core.execution.order_executor import execute_order


def render_execution_view():
    with ui.column().classes('p-4'):
        symbol_input = ui.input('Símbolo').props('outlined')
        quantity_input = ui.number('Cantidad', value=10).props('outlined')
        status_label = ui.label()

        def enviar_orden(tipo):
            try:
                resultado = execute_order(symbol_input.value, tipo, int(quantity_input.value))
                status_label.set_text(f'✅ {resultado}')
            except Exception as e:
                status_label.set_text(f'Error: {e}')

        ui.button('Comprar', on_click=lambda: enviar_orden('BUY'))
        ui.button('Vender', on_click=lambda: enviar_orden('SELL'))
