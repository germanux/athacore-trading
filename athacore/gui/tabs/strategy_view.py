from nicegui import ui
from athacore.core.strategy.strategy_engine import mostrar_estrategias, run_analysis
from athacore.core.execution.order_executor import execute_order
from athacore.core.strategy.strategy_recommend import RECOMENDACIONES
from datetime import date
import pandas as pd
import asyncio

# Lista global para guardar órdenes ejecutadas
ordenes_ejecutadas = []

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

                candle_size = ui.input("candle_size", placeholder="Ej: 15min")
                execution_frequency = ui.input("execution_frequency", placeholder="on_new_candle")
                signal_delay = ui.number("signal_delay")
                time_filter_start = ui.input("time_filter.start", placeholder="09:00")
                time_filter_end = ui.input("time_filter.end", placeholder="17:00")
                slippage_tolerance = ui.number("slippage_tolerance (%)")

                def aplicar_configuracion_recomendada():
                    selected = estrategia.value
                    config = RECOMENDACIONES.get(selected, {})
                    candle_size.value = config.get('candle_size', '')
                    execution_frequency.value = config.get('execution_frequency', '')
                    signal_delay.value = config.get('signal_delay', 0)
                    time_filter_start.value = config.get('time_filter', {}).get('start', '')
                    time_filter_end.value = config.get('time_filter', {}).get('end', '')
                    slippage_tolerance.value = config.get('slippage_tolerance', 0)

                estrategia.on("update:model-value", lambda e: aplicar_configuracion_recomendada())
                aplicar_configuracion_recomendada()

            output = ui.column().classes("w-2/3")

        # Contenedor para tabla de órdenes
        registro_div = ui.column().classes("mt-4")

        def actualizar_tabla_ordenes():
            registro_div.clear()
            if not ordenes_ejecutadas:
                with registro_div:
                    ui.label("📋 No hay órdenes ejecutadas aún.").classes("text-gray-500")
                return

            with registro_div:
                ui.label("📋 Registro de órdenes ejecutadas").classes("text-lg font-semibold mb-2")
                # Construir tabla con botón de cancelar
                rows = []
                for i, orden in enumerate(ordenes_ejecutadas):
                    row = dict(orden)  # copia el dict
                    row['id'] = i
                    rows.append(row)

                def cancelar_orden(id: int):
                    orden = ordenes_ejecutadas.pop(id)
                    ui.notify(f"❌ Orden cancelada: {orden['accion']} {orden['cantidad']} {orden['simbolo']}")
                    actualizar_tabla_ordenes()

                def cell_renderer_cancelar(row):
                    btn = ui.button("Cancelar", color="negative", size="small")
                    btn.on('click', lambda e: cancelar_orden(row['id']))
                    return btn

                ui.table(
                    columns=[
                        {'name': 'simbolo', 'label': 'Símbolo', 'field': 'simbolo'},
                        {'name': 'accion', 'label': 'Acción', 'field': 'accion'},
                        {'name': 'cantidad', 'label': 'Cantidad', 'field': 'cantidad'},
                        {'name': 'resultado', 'label': 'Resultado', 'field': 'resultado'},
                        {'name': 'cancelar', 'label': 'Cancelar', 'field': 'cancelar', 'sortable': False},
                    ],
                    rows=[{**r, 'cancelar': None} for r in rows],
                    row_key='id',
                    render_cell={'cancelar': cell_renderer_cancelar}
                )

        async def ejecutar_orden(tipo, volumen):
            try:
                cantidad = min(int(volumen), 1000)
            except (ValueError, TypeError):
                ui.notify("❌ Volumen inválido", type='negative')
                return

            accion = "BUY" if tipo == "compra" else "SELL"
            resultado = await execute_order(
                symbol=ticker.value.upper(),
                action=accion,
                quantity=cantidad,
                mode='real'
            )
            tipo_notif = 'success' if 'Orden ejecutada' in resultado else 'negative'
            ui.notify(resultado, type=tipo_notif)

            # Registrar orden ejecutada
            ordenes_ejecutadas.append({
                'simbolo': ticker.value.upper(),
                'accion': accion,
                'cantidad': cantidad,
                'resultado': resultado,
            })
            actualizar_tabla_ordenes()

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

                # Preparar tabla de señales
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

                    ultima_senal = señales_dicc[-1]
                    volumen_input = ui.number(label='Cantidad a operar', value=min(int(ultima_senal.get('volumen', 0)), 1000))

                    async def ejecutar_compra():
                        await ejecutar_orden("compra", volumen_input.value)

                    async def ejecutar_venta():
                        await ejecutar_orden("venta", volumen_input.value)

                    if ultima_senal.get('compra'):
                        with ui.row().classes('items-center gap-4'):
                            ui.label(f"📢 Recomendación final: 🟢 COMPRAR {ticker.value.upper()}").classes("text-green-600 font-bold")
                            ui.button('Ejecutar orden de COMPRA', on_click=ejecutar_compra).props('color=primary')
                    elif ultima_senal.get('venta'):
                        with ui.row().classes('items-center gap-4'):
                            ui.label(f"📢 Recomendación final: 🔴 VENDER {ticker.value.upper()}").classes("text-red-600 font-bold")
                            ui.button('Ejecutar orden de VENTA', on_click=ejecutar_venta).props('color=negative')
                    else:
                        with ui.row().classes('items-center gap-4'):
                            ui.label(f"📢 Recomendación final: 🟡 MANTENER posición en {ticker.value.upper()}")
            except Exception as e:
                output.clear()
                with output:
                    ui.label(f'❌ Error al ejecutar la estrategia: {e}').classes('text-red-600 font-bold')

        with inputs:
            ui.button('Ejecutar estrategia', on_click=ejecutar)
        
        # Mostrar tabla de órdenes ejecutadas
        actualizar_tabla_ordenes()
