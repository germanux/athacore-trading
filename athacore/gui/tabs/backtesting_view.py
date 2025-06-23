from nicegui import ui
import plotly.graph_objects as go
from athacore.core.backtesting.backtester import run_backtest
from athacore.core.strategy.strategy_engine import mostrar_estrategias, run_analysis
from athacore.core.strategy.strategy_recommend import RECOMENDACIONES

ESTRATEGIAS = list(mostrar_estrategias().keys())

#Listas credas para cada menú de selección. A espera de un estándar
CANDLE_SIZE_OPTIONS=["1min", "5min", "15min", "30min", "1h", "1d", "1w", "1m"]                                   #Estandarizado según strategy_recommend
EXECUTION_FRECUENCY_OPTIONS=["on_new_candle", "on_close", "on_event", "on_tick"]                           #Estandarizado según strategy_recommend
SYMBOLS_SUPPORTED_OPTIONS = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "AMD", "SPY", "QQQ"] # Aún no implementado

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
                    columna_graficas.clear()
                    def dibujar_grafica():
                        fig = go.Figure()
                        fig.add_hline(y=initial_cash, line=dict(color="orange", width=1))
                        fig.add_trace(go.Scatter(
                            x=diccionario["fecha"],
                            y=diccionario["dinero"],
                            mode='lines',
                            name='Volumen'
                        ))
                        fig.update_layout(
                            title=f"Grafica de rendimiento al invertir en {ticker} entre el {start} y {end}",
                            xaxis_title="Fecha",
                            yaxis_title="Dinero",
                            xaxis=dict(tickformat="%Y-%m-%d", type="date")
                        )

                        ui.plotly(fig).classes("w-full h-[600px]")
                    dibujar_grafica()

        except Exception as e:
            ui.notification(f"Error: {e}", type="negative")
            print(f"[BACKTESTING_VIEW]: Error al ejecutar backtest: {e}")

def print_default_config(estrategiaObj, container):
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

def set_default_values(strategy,
                candle_size,
                lookback_period,
                total_data_needed,
                execution_frequency,
                signal_delay,
                time_filter_start,
                time_filter_end,
                symbols_supported,
                slippage_tolerance):
    
    if strategy in RECOMENDACIONES:
        dicc_config = RECOMENDACIONES[strategy]

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
        time_filter_start.value = dicc_config["time_filter"]["start"]
        time_filter_end.value = dicc_config["time_filter"]["end"]
        slippage_tolerance.value = dicc_config["slippage_tolerance"]
        
        #Pendiente de revisión
        try:   
            symbols_supported.options = dicc_config["symbols_supported"]
            print(f"[BACKTESTING_VIEW]: Simbolos soportados por la estrategia: {dicc_config['symbols_supported']}")
            print(f"[BACKTESTING_VIEW]: Simpolos del input: {symbols_supported.options}")
        except Exception as e:
            print(f"[BACKTESTING_VIEW]: Error al cargar los simbolos soportados: {e}")

    else:
        ui.notify("No hay configuración recomendada para la estrategia indicada", type="warning")

def ticker_support(ticker, ticker_state):
    if SYMBOLS_SUPPORTED_OPTIONS:
        if ticker in SYMBOLS_SUPPORTED_OPTIONS:
            ticker_state.text = "✅ Símbolo soportado"
        else:
            ticker_state.text = "❌ Símbolo no soportado"
    else:
        ticker_state.text = "No hay información sobre símbolos soportados"
        
def input_type_change(value, container_date, container_candle):
    container_date.visible = False
    container_candle.visible = False

    if value == "Por fecha":
        container_date.visible = True
    elif value == "Por velas":
        container_candle.visible = True

def render_backtesting_view():
    with ui.card().classes('p-4 w-full'):
        ui.label('🧠 Backtesting')
        with ui.row().classes("w-full  gap-3"):
            inputs = ui.column().classes("width: 15em items-stretch")
            with inputs:
                ui.label("Opciones básicas").classes("font-bold mt-2")
                estrategia = ui.select(
                    options=ESTRATEGIAS,
                    label='Selecciona una estrategia',
                    value=ESTRATEGIAS[0])
                
                ticker = ui.select(
                    options=SYMBOLS_SUPPORTED_OPTIONS,
                    label="Selecciona un ticker",
                    with_input=True
                )
                ticker_state = ui.label("Esperando entrada de un ticker...")

                initial_cash = ui.input('Dinero inicial')
                percentage_cash = ui.number('Porcentaje por inversión', min=0, max=100)
                candle_size = ui.select(
                        options=CANDLE_SIZE_OPTIONS,
                        label="Tamaño de velas (candle_size)",
                        value=CANDLE_SIZE_OPTIONS[0],
                        with_input=True)

                ui.label("Tipo de backtesting").classes("font-bold mt-2")
                
                input_type=ui.select(
                    options=["Por fecha", "Por velas"],
                    label='Selecciona un tipo de entrada',
                    value="Por fecha",
                ).on_value_change(lambda _:input_type_change(input_type.value, inputs_by_date, inputs_by_candles))
                
                inputs_by_date = ui.column().classes("items-stretch")
                inputs_by_candles = ui.column().classes("items-stretch")
                
                with inputs_by_date:
                    start = ui.input('Fecha inicio (YYYY-MM-DD)')

                with inputs_by_candles:
                        # Inputs que solo son informativos por ahora
                    lookback_period = ui.input("Periodo de análisis por velas (lookback_period)").classes("bg-gray-100")
                    total_data_needed = ui.input("Total de datos necesarios").classes("bg-gray-100")
                    
                end = ui.input('Fecha fin (YYYY-MM-DD)')

                ui.label("Opciones extra").classes("font-bold mt-2")
                
                execution_frequency = ui.select(
                    options=EXECUTION_FRECUENCY_OPTIONS,
                    label="Frecuencia de ejecución",
                    value=EXECUTION_FRECUENCY_OPTIONS[0]
                )
                signal_delay = ui.number("Retraso de señal (signal delay)", value=1)
                ui.label("Horario permitido:")
                with ui.row():
                    time_filter_start = ui.input("Hora de inicio", value="09:00")  # Se puede cambiar por ui.time()
                    time_filter_end= ui.input("Hora de fin", value="17:00")
                slippage_tolerance = ui.number("Tolerancia al deslizamiento (%)", min=0, max=100)
         
                ui.button('Ejecutar Backtest', on_click=lambda:ejecutar_backtest(estrategia.value, ticker.value, start.value, end.value, initial_cash.value, int(percentage_cash.value), output))

            output = ui.column().classes("items-center")
            strategy_data = ui.column().classes('bg-gray-100 p-2 rounded')


            # === LÓGICA ESTRATEGIAS === #
            print_default_config(mostrar_estrategias().get(estrategia.value), strategy_data)
            input_type_change(input_type.value, inputs_by_date, inputs_by_candles)
            set_default_values(estrategia.value, candle_size, lookback_period,total_data_needed, execution_frequency, signal_delay, time_filter_start, time_filter_end, ticker, slippage_tolerance)

            #Event listeners
            estrategia.on_value_change(lambda _: print_default_config(mostrar_estrategias().get(estrategia.value), strategy_data))
            estrategia.on_value_change(lambda _: set_default_values(estrategia.value, candle_size, lookback_period,total_data_needed, execution_frequency, signal_delay, time_filter_start, time_filter_end, ticker, slippage_tolerance))
            ticker.on_value_change(lambda _: ticker_support(ticker.value, ticker_state))
