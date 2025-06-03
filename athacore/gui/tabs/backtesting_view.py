from nicegui import ui
import plotly.graph_objects as go
from athacore.core.backtesting.backtester import run_backtest
from athacore.core.strategy.strategy_engine import mostrar_estrategias, run_analysis

ESTRATEGIAS = list(mostrar_estrategias().keys())

def ejecutar_backtest(estrategia, ticker, start, end, initial_cash, percentage_cash, status_label):
        try:
            señales = run_analysis(estrategia, ticker, start, end)

            resultado, diccionario = run_backtest(señales, "compra", initial_cash, percentage_cash)

            #Renderizado
            status_label.clear()

            with status_label:                        
                ui.table(
                    columns=[{'name': key, 'label': key.upper(), 'field': key} for key in resultado],
                    rows=[resultado]
                )
                         
                columna_graficas = ui.column()

                with columna_graficas:
                    def dibujar_grafica():
                        columna_graficas.clear()

                        fig = go.Figure()
                        fig.add_hline(y=initial_cash, line=dict(color="orange", width=1))
                        fig.add_trace(go.Scatter(
                            x=diccionario["fecha"],
                            y=diccionario["dinero"],
                            mode='lines',
                            name='Volumen'
                        ))
                        fig.update_layout(
                            title=f"Gráfica de {ticker} entre {start} y {end}",
                            xaxis_title="Fecha",
                            yaxis_title="Dinero",
                            xaxis=dict(tickformat="%Y-%m-%d", type="date")
                        )

                        ui.plotly(fig).classes("w-full h-[600px]")
                    dibujar_grafica()

        except Exception as e:
            with status_label:
                 ui.label(f'Error: {e}')

def print_config(estrategiaObj, container):
    try:
        # ui.label(f"Configuracion de f{self.name}")
        container.clear()
        with container:
            ui.label(f"Configuracion de la estrategia seleccionada").classes("font-bold")
            with ui.list().props('dense separator'):
                for parametro, valor in estrategiaObj.get_default_config().items(): #A la espera de configuraciones para cada estrategia
                    if valor:
                        ui.item(f"{parametro.upper()}: {valor}")
    except:
        pass

def render_backtesting_view():
    with ui.card().classes('p-4 w-full'):
        ui.label('🧠 Backtesting')
        with ui.row().classes("w-full  gap-3"):
            inputs = ui.column().classes("width: 15em")
            with inputs:
                estrategia = ui.select(
                    options=ESTRATEGIAS,
                    label='Selecciona una estrategia',
                    value=ESTRATEGIAS[0]
                )
                ticker = ui.input('Ticker (ej: AAPL)').props('outlined')
                start = ui.input('Fecha inicio (YYYY-MM-DD)').props('outlined')
                end = ui.input('Fecha fin (YYYY-MM-DD)').props('outlined')
                initial_cash = ui.input('Dinero inicial').props('outlined')
                percentage_cash = ui.input('Porcentaje por inversión').props('outlined')

                ui.button('Ejecutar Backtest', on_click=lambda:ejecutar_backtest(estrategia.value, ticker.value, start.value, end.value, initial_cash.value, int(percentage_cash.value), output))

            output = ui.column().classes("items-center")

            strategy_data = ui.column()
            estrategiaObj = mostrar_estrategias().get(estrategia.value)
            print_config(estrategiaObj, strategy_data)
            estrategia.on('change', lambda:print_config(estrategiaObj, strategy_data))