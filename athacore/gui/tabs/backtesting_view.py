from nicegui import ui
from athacore.core.strategy.strategy_engine import run_analysis
from athacore.core.backtesting.backtester import run_backtest
from athacore.core.strategy.strategy_engine import mostrar_estrategias, run_analysis

import plotly.graph_objects as go

ESTRATEGIAS = list(mostrar_estrategias().keys())

def ejecutar_backtest(estrategia, ticker, start, end, initial_cash, status_label):
        try:
            señales = run_analysis(
                strategy_name=estrategia.value,
                ticker=ticker.value,
                start=start.value,
                end=end.value
                )
            #print(señales)

            resultado, diccionario = run_backtest(señales, "compra", initial_cash.value)
            #print(resultado)

            with status_label:
                with ui.row():
                    for a, b in resultado.items():
                         ui.label(f"{a.upper()}: {b}")
                         
                columna_graficas = ui.column()

                with columna_graficas:
                    def dibujar_grafica():
                        columna_graficas.clear()

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=diccionario["fecha"],
                            y=diccionario["dinero"],
                            mode='lines',
                            name='Volumen'
                        ))
                        
                        fig.update_layout(
                            title=f"Crecimiento del dinero invertido",
                            xaxis_title="Fecha",
                            yaxis_title="Dinero",
                            xaxis=dict(tickformat="%Y-%m-%d", type="date")
                        )

                        ui.plotly(fig).classes("w-full h-[600px]")
                    dibujar_grafica()

        except Exception as e:
            with status_label:
                 ui.label(f'Error: {e}')


def render_backtesting_view():
    with ui.row().classes("w-full gap-0"):
            inputs = ui.column().classes("w-1/3")
            with inputs:
                estrategia = ui.select(
                    options=ESTRATEGIAS,
                    label='Selecciona una estrategia',
                    value=ESTRATEGIAS[0]
                )
                ticker = ui.input('Ticker (ej: AAPL)', value="AAPL").props('outlined')
                start = ui.input('Fecha inicio (YYYY-MM-DD)', value="2020-01-01").props('outlined')
                end = ui.input('Fecha fin (YYYY-MM-DD)', value="2024-01-01").props('outlined')
                initial_cash = ui.input('Dinero inicial', value="200").props('outlined')

            output = ui.column().classes("w-2/3")
            with output:
                status_label = ui.column()
            
            ui.button('Ejecutar Backtest', on_click=lambda:ejecutar_backtest(estrategia, ticker, start, end, initial_cash, status_label))
            