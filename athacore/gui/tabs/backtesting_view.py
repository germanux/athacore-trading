from nicegui import ui
import plotly.graph_objects as go
from athacore.core.backtesting.backtester import run_backtest
from athacore.core.strategy.strategy_engine import mostrar_estrategias, run_analysis

ESTRATEGIAS = list(mostrar_estrategias().keys())

#Listas credas para cada menú de selección. A espera de un estándar
CANDLE_SIZE_OPTIONS = ["1 minuto", "5 minutos", "15 minutos", "30 minutos", "1 día", "1 semana", "1 mes"] #   1 mes sirve sobretodo para analizar mercado o inversiones a largo plazo
EXECUTION_FRECUENCY_OPTIONS =["Con nuevas velas", "Por frecuencia", "Por horario", "Con cambios de mercado", "Manual"]
SYMBOLS_SUPPORTED_OPTIONS = ["AAPL", "IONQ"]

visibilidad = False

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
    except Exception as e:
        print (f"Error al imprimir la configuracion: {e}")

def set_values(estrategiaObj,
                candle_size,
                lookback_period,
                total_data_needed,
                execution_frequency,
                signal_delay,
                time_filter_start,
                time_filter_end,
                symbols_supported,
                slippage_tolerance):
    
    dicc_config = estrategiaObj.get_default_config()
    """
    REFERENCIA DE CONFIGURACIÓN DE ESTRATEGIAS
    candle_size": "15min",
    "lookback_period": 14,
    "total_data_needed": 30,
    "execution_frequency": "on_new_candle",
    "signal_delay": 1,
    "time_filter": {"start": "09:00", "end": "17:00"},
    "symbols_supported": [],
    "slippage_tolerance": 0.1
    """

    # Esperando estándares para menús desplegables. Se debe dar un valor de un array, por lo que requieren lógica extra.
    candle_size.value = dicc_config["candle_size"]
    lookback_period.value = dicc_config["lookback_period"]
    total_data_needed.value = dicc_config["total_data_needed"]
    execution_frequency.value = dicc_config["execution_frequency"]
    signal_delay.value = dicc_config["signal_delay"]
    time_filter_start.value = dicc_config["time_filter"]["start"] # <--- Este formato impide hacer directamente el bucle
    time_filter_end.value = dicc_config["time_filter"]["end"]
    symbols_supported.value = dicc_config["symbols_supported"]
    slippage_tolerance.value = dicc_config["slippage_tolerance"]

def cambiar_visibilidad(container):
    global visibilidad
    if visibilidad:
        visibilidad = False
    else:
        visibilidad = True
    container.visible = visibilidad

def render_backtesting_view():
    with ui.card().classes('p-4 w-full'):
        ui.label('🧠 Backtesting')
        with ui.row().classes("w-full  gap-3"):
            inputs = ui.column().classes("width: 15em items-stretch")
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



                opciones_avanzadas = ui.column().classes("items-stretch justify-between")
                opciones_avanzadas.visible = visibilidad
                with opciones_avanzadas:
                    ui.label("Opciones avanzadas")
                    candle_size = ui.select(
                        options=CANDLE_SIZE_OPTIONS,
                        label="Tamaño de velas (candle_size)",
                        value=CANDLE_SIZE_OPTIONS[4])
                    lookback_period = ui.input("Periodo de análisis por velas (lookback_period)")
                    total_data_needed = ui.input("Total de datos necesarios")
                    execution_frequency = ui.select(
                        options=EXECUTION_FRECUENCY_OPTIONS,
                        label="Frecuencia de ejecución",
                        value=EXECUTION_FRECUENCY_OPTIONS[2]
                    )
                    signal_delay = ui.number("Retraso de señal (signal delay)", value=1)
                    ui.label("Horario permitido:")
                    with ui.row():
                        time_filter_start = ui.input("Hora de inicio", value="09:00")  # Se puede cambiar por ui.time()
                        time_filter_end= ui.input("Hora de fin", value="17:00")
                    if SYMBOLS_SUPPORTED_OPTIONS:                                      # Cuando se tengan listas oficiales en vez de una seleccion se podria hacer una comprobación con el de arriba
                        symbols_supported =ui.select(
                            options=SYMBOLS_SUPPORTED_OPTIONS,
                            label="Tickers soportados",
                            value=SYMBOLS_SUPPORTED_OPTIONS[0]
                        )
                    slippage_tolerance = ui.number("Tolerancia al deslizamiento (%)", min=0, max=100)
         
                ui.button("Opciones avanzadas", on_click=lambda:cambiar_visibilidad(opciones_avanzadas))
                ui.button('Ejecutar Backtest', on_click=lambda:ejecutar_backtest(estrategia.value, ticker.value, start.value, end.value, initial_cash.value, int(percentage_cash.value), output))

            output = ui.column().classes("items-center")
            strategy_data = ui.column()


            # === LÓGICA ESTRATEGIAS === #
            estrategiaObj = mostrar_estrategias().get(estrategia.value) # Tomar el objeto estrategia equivalente al de la lista de opciones
            

            #Event listeners
            estrategia.on_value_change(lambda _: print_config(mostrar_estrategias().get(estrategia.value), strategy_data))
            estrategia.on_value_change(lambda _: set_values(estrategiaObj, 
                                                        candle_size,
                                                        lookback_period,
                                                        total_data_needed,
                                                        execution_frequency,
                                                        signal_delay,
                                                        time_filter_start,
                                                        time_filter_end,
                                                        symbols_supported,
                                                        slippage_tolerance))
