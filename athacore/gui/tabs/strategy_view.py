from nicegui import ui
from athacore.core.strategy.strategy_engine import mostrar_estrategias, run_analysis
from athacore.core.execution.order_executor import execute_order
from datetime import date, datetime, timedelta
import pandas as pd
import asyncio
import pytz
import uuid

# Variable global para controlar órdenes activas y ejecutadas
ordenes_registro = []

def esta_en_horario_valido():
    madrid = pytz.timezone('Europe/Madrid')
    ahora = datetime.now(madrid).time()
    hora_inicio = datetime.strptime("15:30", "%H:%M").time()
    hora_fin = datetime.strptime("22:00", "%H:%M").time()
    return hora_inicio <= ahora <= hora_fin

def render_strategy_view():
    with ui.card().classes('p-4 w-full'):
        ui.label('📈 Estrategias de Trading y Ejecución en IB Gateway').classes('text-2xl font-bold')

        ESTRATEGIAS = list(mostrar_estrategias().keys())
        estrategia_objs = mostrar_estrategias()

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

                config_area = ui.column().classes('bg-gray-100 p-2 rounded w-full')

                with ui.expansion("⚙️ Opciones avanzadas", icon="tune") as advanced:
                    candle_size = ui.input("candle_size", placeholder="Ej: 15min")
                    lookback_period = ui.number("lookback_period")
                    total_data_needed = ui.number("total_data_needed")
                    execution_frequency = ui.input("execution_frequency", placeholder="on_new_candle")
                    signal_delay = ui.number("signal_delay")
                    time_filter_start = ui.input("time_filter.start", placeholder="09:00")
                    time_filter_end = ui.input("time_filter.end", placeholder="17:00")
                    symbols_supported = ui.input("Símbolos soportados (coma separados)", placeholder="AAPL,TSLA")
                    slippage_tolerance = ui.number("slippage_tolerance (%)")

                def aplicar_configuracion_recomendada():
                    selected = estrategia.value
                    obj = estrategia_objs[selected]
                    config = obj.get_default_config()

                    config_area.clear()
                    with config_area:
                        ui.label("✅ PARÁMETROS FUNDAMENTALES (Altamente recomendados)").classes("font-bold")
                        ui.label(f"candle_size: {config.get('candle_size')}")
                        ui.label(f"lookback_period: {config.get('lookback_period')}")
                        ui.label(f"total_data_needed: {config.get('total_data_needed')}")

                        ui.label("\n🧩 PARÁMETROS ADICIONALES ÚTILES").classes("font-bold mt-4")
                        ui.label(f"execution_frequency: {config.get('execution_frequency')}")
                        ui.label(f"signal_delay: {config.get('signal_delay')}")
                        tf = config.get("time_filter", {})
                        ui.label(f"time_filter: {tf.get('start')} - {tf.get('end')}")
                        ui.label(f"symbols_supported: {', '.join(config.get('symbols_supported', []))}")
                        ui.label(f"slippage_tolerance: {config.get('slippage_tolerance')}")

                    candle_size.value = config.get('candle_size', '')
                    lookback_period.value = config.get('lookback_period', 0)
                    total_data_needed.value = config.get('total_data_needed', 0)
                    execution_frequency.value = config.get('execution_frequency', '')
                    signal_delay.value = config.get('signal_delay', 0)
                    time_filter_start.value = config.get('time_filter', {}).get('start', '')
                    time_filter_end.value = config.get('time_filter', {}).get('end', '')
                    symbols_supported.value = ','.join(config.get('symbols_supported', []))
                    slippage_tolerance.value = config.get('slippage_tolerance', 0)

                estrategia.on("update:model-value", lambda e: aplicar_configuracion_recomendada())
                aplicar_configuracion_recomendada()

            output = ui.column().classes("w-2/3")

        ordenes_area = ui.column().classes('mt-6')

        def actualizar_registro_ordenes():
            ordenes_area.clear()
            with ordenes_area:
                ui.label('📝 Registro de órdenes ejecutadas y en proceso').classes('text-xl font-bold mb-2')

                if not ordenes_registro:
                    ui.label('No hay órdenes registradas aún.')
                    return

                for idx, orden in enumerate(ordenes_registro):
                    estado = orden['estado']
                    symbol = orden['symbol']
                    cantidad = orden['quantity']
                    accion = orden['action']
                    uid = orden['id']

                    with ui.card().classes('mb-2 p-2 flex justify-between items-center'):
                        ui.label(f"{idx+1}. {accion} {cantidad} {symbol} - Estado: {estado}")

                        if estado == 'en proceso':
                            with ui.row().classes('gap-2'):
                                def crear_handler_cancelar(oid=uid):
                                    async def cancelar():
                                        for o in ordenes_registro:
                                            if o['id'] == oid:
                                                o['estado'] = 'cancelada'
                                        ui.notify(f"Orden {oid} cancelada.")
                                        actualizar_registro_ordenes()
                                    return cancelar

                                def crear_handler_pausar(oid=uid):
                                    async def pausar():
                                        for o in ordenes_registro:
                                            if o['id'] == oid:
                                                o['estado'] = 'pausada'
                                        ui.notify(f"Orden {oid} pausada.")
                                        actualizar_registro_ordenes()
                                    return pausar

                                ui.button('Cancelar', on_click=crear_handler_cancelar()).props('color=negative')
                                ui.button('Pausar', on_click=crear_handler_pausar()).props('color=warning')

        def registrar_orden(symbol, action, quantity):
            uid = str(uuid.uuid4())[:8]
            orden = {
                'id': uid,
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'estado': 'en proceso',
            }
            ordenes_registro.append(orden)
            actualizar_registro_ordenes()
            return uid

        def crear_handler_compra(s):
            async def handler():
                if not esta_en_horario_valido():
                    ui.notify("⛔ Fuera del horario permitido (15:30 - 22:00 hora española)", type='warning')
                    return

                cantidad = min(int(s.get('volumen', 0)), 1000)
                uid = registrar_orden(ticker.value.upper(), "BUY", cantidad)

                try:
                    resultado = await asyncio.wait_for(
                        execute_order(
                            symbol=ticker.value.upper(),
                            action="BUY",
                            quantity=cantidad,
                            mode='real'
                        ),
                        timeout=5.0
                    )
                    for o in ordenes_registro:
                        if o['id'] == uid:
                            o['estado'] = 'ejecutada' if 'Orden' in resultado else 'error'
                    ui.notify(resultado, type='success' if 'Orden' in resultado else 'negative')
                except asyncio.TimeoutError:
                    for o in ordenes_registro:
                        if o['id'] == uid:
                            o['estado'] = 'cancelada'
                    ui.notify("❌ La orden fue cancelada por tiempo de espera (5 segundos sin respuesta).", type='warning')

                actualizar_registro_ordenes()
            return handler

        def crear_handler_venta(s):
            async def handler():
                if not esta_en_horario_valido():
                    ui.notify("⛔ Fuera del horario permitido (15:30 - 22:00 hora española)", type='warning')
                    return

                cantidad = min(int(s.get('volumen', 0)), 1000)
                uid = registrar_orden(ticker.value.upper(), "SELL", cantidad)

                try:
                    resultado = await asyncio.wait_for(
                        execute_order(
                            symbol=ticker.value.upper(),
                            action="SELL",
                            quantity=cantidad,
                            mode='real'
                        ),
                        timeout=5.0
                    )
                    for o in ordenes_registro:
                        if o['id'] == uid:
                            o['estado'] = 'ejecutada' if 'Orden' in resultado else 'error'
                    ui.notify(resultado, type='success' if 'Orden' in resultado else 'negative')
                except asyncio.TimeoutError:
                    for o in ordenes_registro:
                        if o['id'] == uid:
                            o['estado'] = 'cancelada'
                    ui.notify("❌ La orden fue cancelada por tiempo de espera (5 segundos sin respuesta).", type='warning')

                actualizar_registro_ordenes()
            return handler

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

                    # Mostrar solo la última señal
                    ultima_senal = señales_dicc[-1]
                    volumen_input = ui.number(label='Cantidad a operar', value=min(int(ultima_senal.get('volumen', 0)), 1000))

                    if ultima_senal.get('compra'):
                        with ui.row().classes('items-center gap-4'):
                            ui.label(f"📢 Recomendación final: ✅ COMPRAR {ticker.value.upper()}")
                            ui.button('Ejecutar orden de COMPRA', on_click=lambda: crear_handler_compra({
                                **ultima_senal,
                                'volumen': volumen_input.value
                            })()).props('color=primary')

                    elif ultima_senal.get('venta'):
                        with ui.row().classes('items-center gap-4'):
                            ui.label(f"📢 Recomendación final: 🔻 VENDER {ticker.value.upper()}")
                            ui.button('Ejecutar orden de VENTA', on_click=lambda: crear_handler_venta({
                                **ultima_senal,
                                'volumen': volumen_input.value
                            })()).props('color=negative')

                    else:
                        with ui.row().classes('items-center gap-4'):
                            ui.label(f"📢 Recomendación final: 🟡 MANTENER posición en {ticker.value.upper()}")


            except Exception as e:
                output.clear()
                with output:
                    ui.label(f'❌ Error al ejecutar la estrategia: {e}').classes('text-red-600 font-bold')

        with inputs:
            ui.button('Ejecutar estrategia', on_click=ejecutar).props('color=secondary')

        actualizar_registro_ordenes()
