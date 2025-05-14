from nicegui import ui
from datetime import date
from athacore.core.data.market_data import get_price_data
from athacore.core.graphics.charts.volume_chart import build_volume_chart
from athacore.core.graphics.charts.comparison_chart import build_volume_comparison_chart_multiple

ACTIVOS = ['AAPL', 'GOOGL', 'MSFT']
TIPOS_GRAFICAS = ['Volumen', 'Comparar Volumen']

def render_graphics_view():
    with ui.card().classes("w-full mt-6"):
        ui.label("Gráficas")
        metodo_grafica_seleccionada = ui.select(TIPOS_GRAFICAS, value=TIPOS_GRAFICAS[0])

        with ui.row().classes("w-full gap-0"):
            with ui.column().classes("w-1/3"):
                lista_inputs = ui.column().classes("mt-4")
                boton_generar = ui.row().classes("mt-2")
            contenedor_graficas = ui.column().classes("mt-6 w-2/3")  # Aquí se apilan las gráficas generadas

        # Lista para almacenar las gráficas generadas
        graficas_generadas = []

        def actualizar_inputs(event):
            lista_inputs.clear()
            boton_generar.clear()

            if event.value == "Volumen": 
                with lista_inputs:
                    ui.label("Activo")
                    activo_seleccionado = ui.select(ACTIVOS, value=ACTIVOS[0])
                    ui.label("Fecha de inicio")
                    fecha_1 = ui.date()

                def generar_volumen():
                    start = fecha_1.value
                    end = str(date.today())
                    df = get_price_data(activo_seleccionado.value, start, end)
                    fig = build_volume_chart(df, activo_seleccionado.value, start, end)

                    # Añadir la gráfica generada a la lista
                    graficas_generadas.insert(0, (f"Gráfica de Volumen: {activo_seleccionado.value} ({start} - {end})", fig))

                    # Limpiar contenedor de gráficas y volver a cargar en orden
                    contenedor_graficas.clear()
                    for titulo, grafico in graficas_generadas:
                        with contenedor_graficas:
                            with ui.card().classes("w-full mb-4"):
                                ui.label(titulo).classes("text-lg font-bold")
                                ui.plotly(grafico).classes("w-full h-[600px]")

                with boton_generar:
                    ui.button("Generar gráfica", on_click=generar_volumen).classes("mt-2")

            elif event.value == "Comparar Volumen":
                with lista_inputs:
                    ui.label("Activos")
                    activos_seleccionados = ui.select(ACTIVOS, value=[ACTIVOS[0]], multiple=True)
                    with ui.row():  # Colocamos ambos calendarios en la misma fila
                        with ui.column():
                            ui.label("Fecha de inicio")
                            fecha_inicio = ui.date().classes("W-1/2")
                        with ui.column():
                            ui.label("Fecha de fin")
                            fecha_fin = ui.date().classes("W-1/2")

                def generar_comparacion():
                    f_ini = fecha_inicio.value
                    f_fin = fecha_fin.value
                    activos = activos_seleccionados.value

                    if not f_ini or not f_fin or not activos:
                        ui.notify("Completa todas las fechas y selecciona activos", type="warning")
                        return
                    if f_ini >= f_fin:
                        ui.notify("La fecha de inicio debe ser menor a la de fin", type="warning")
                        return

                    activos_dfs = []
                    for activo in activos:
                        try:
                            df = get_price_data(activo, f_ini, f_fin)
                            if df is None or df.empty:
                                ui.notify(f"No hay datos para {activo} en ese rango", type="warning")
                                continue
                            df = df.reset_index()
                            activos_dfs.append((activo, df))
                        except Exception as e:
                            ui.notify(f"Error al obtener datos de {activo}: {e}", type="error")
                            return

                    if not activos_dfs:
                        ui.notify("No se pudieron cargar datos de ningún activo", type="error")
                        return

                    try:
                        fig = build_volume_comparison_chart_multiple(activos_dfs, f_ini, f_fin)

                        # Añadir la gráfica generada a la lista
                        activos_nombres = ', '.join(activos)
                        graficas_generadas.insert(0, (f"Comparación de Volumen: {activos_nombres} ({f_ini} - {f_fin})", fig))

                        # Limpiar contenedor de gráficas y volver a cargar en orden
                        contenedor_graficas.clear()
                        for titulo, grafico in graficas_generadas:
                            with contenedor_graficas:
                                with ui.card().classes("w-full mb-4"):
                                    ui.label(titulo).classes("text-lg font-bold")
                                    ui.plotly(grafico).classes("w-full h-[600px]")

                    except Exception as e:
                        ui.notify(f"Error al construir la gráfica: {e}", type="error")

                with boton_generar:
                    ui.button("Generar comparación", on_click=generar_comparacion).classes("mt-2")

        actualizar_inputs(metodo_grafica_seleccionada)
        metodo_grafica_seleccionada.on_value_change(actualizar_inputs)

