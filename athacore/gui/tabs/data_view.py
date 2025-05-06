# gui/tabs/data_view.py

from nicegui import ui
from athacore.core.data.market_data import get_price_data


def render_data_view():
    with ui.column().classes('p-4'):
        ticker_input = ui.input('Símbolo (ej: AAPL)').props('outlined')
        status_label = ui.label()

        def mostrar_datos():
            try:
                df = get_price_data(ticker_input.value, '2020-01-01', '2025-02-01')
                cierre = df['Close'].iloc[-1]
                status_label.set_text(f'Último cierre de {ticker_input.value.upper()}: {cierre:.2f}')
            except Exception as e:
                status_label.set_text(f'Error: {e}')

        ui.button('Consultar', on_click=mostrar_datos)
