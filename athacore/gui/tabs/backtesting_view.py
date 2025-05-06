from nicegui import ui
from athacore.core.strategy.strategy_engine import run_analysis
from athacore.core.backtesting.backtester import run_backtest


def render_backtesting_view():
    with ui.column().classes('p-4'):
        ticker_input = ui.input('Símbolo (ej: AAPL)').props('outlined')
        estrategia_select = ui.select(
            options=['estrategia_basica_medias', 'estrategia_rsi_simple', 'estrategia_macd_cruce'],
            label='Estrategia',
        )
        status_label = ui.label()

        def ejecutar_backtest():
            try:
                señales = run_analysis(
                    strategy_name=estrategia_select.value,
                    ticker=ticker_input.value,
                    start="2023-01-01",
                    end="2023-12-31"
                )
                resultado = run_backtest(señales)

                resumen = f"""
                💼 Valor inicial: {resultado['initial_cash']:.2f} €
                📊 Valor final: {resultado['final_value']:.2f} €
                📈 Ganancia total: {resultado['profit']:.2f} €
                🔁 Nº de operaciones: {len(resultado['trades'])}
                """
                status_label.set_text(resumen.strip())
            except Exception as e:
                status_label.set_text(f'Error: {e}')

        ui.button('Ejecutar Backtest', on_click=ejecutar_backtest)
