# athacore/gui/tabs/data_view.py
from nicegui import ui
from athacore.core.data.market_data import get_price_data  # Asegúrate que este sea el basado en yfinance

def render_data_view():
    with ui.card().classes('p-6 w-full max-w-2xl mx-auto'):
        ui.label('Consulta de datos históricos de acciones').classes('text-xl font-bold mb-4')

        # Inputs
        ticker_input = ui.input('Símbolo (ej: AAPL)').props('outlined dense').classes('w-full')
        status_label = ui.label().classes('text-sm mt-2 text-red-500')
        resultado_label = ui.label().classes('text-lg font-medium text-green-700 mt-2')
        table_container = ui.column().classes('mt-4 w-full')

        async def mostrar_datos():
            status_label.set_text('')
            resultado_label.set_text('')
            table_container.clear()

            symbol = ticker_input.value.strip().upper()
            if not symbol:
                status_label.set_text('⚠️ Debes ingresar un símbolo.')
                return

            try:
                result = await get_price_data(symbol, source='yfinance')  # 👈 usamos yfinance explícitamente
                df = result["data"]
                info = result["info"]

                # Muestra info general
                resultado_label.set_text(
                    f"📊 {info['name']} ({info['symbol']})\n"
                    f"💱 Tipo: {info['secType']} | Bolsa: {info['exchange']} | Moneda: {info['currency']}"
                )

                # Muestra los últimos datos históricos en tabla
                with table_container:
                    ui.table(
                        columns=[{'name': c, 'label': c.capitalize(), 'field': c} for c in df.columns],
                        rows=df.tail(10).to_dict('records'),
                        pagination=10
                    ).classes('w-full')

            except Exception as e:
                status_label.set_text(f'❌ Error: {e}')

        # Botón para consultar
        ui.button('Consultar', on_click=mostrar_datos).props('color=primary').classes('mt-2')





