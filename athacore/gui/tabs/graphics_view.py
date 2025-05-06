from nicegui import ui
from datetime import date
from athacore.core.data.market_data import get_price_data
from athacore.core.graphics.charts.volume_chart import build_volume_chart
from athacore.core.graphics.charts.comparison_chart import build_volume_comparison_chart

ACTIVOS = ['AAPL', 'GOOGL', 'MSFT']
TIPOS_GRAFICAS = ['Volumen', 'Comparar Volumen']

def render_graphics_view():
    with ui.card().classes("w-full mt-6"):
        ui.label("Gráficas")
        metodo_grafica_seleccionada = ui.select(TIPOS_GRAFICAS, value=TIPOS_GRAFICAS[0])
        lista_inputs = ui.row()
        contenedor_graficas = ui.row()

        def actualizar_inputs(event):
            lista_inputs.clear()
            contenedor_graficas.clear()

            if event.value == "Volumen":
                with lista_inputs:
                    fecha_1 = ui.date("Fecha de inicio")
                    activo_seleccionado = ui.select(ACTIVOS, value=ACTIVOS[0])

                def generar():
                    start = fecha_1.value
                    end = str(date.today())
                    df = get_price_data(activo_seleccionado.value, start, end)
                    fig = build_volume_chart(df, activo_seleccionado.value, start, end)
                    contenedor_graficas.clear()
                    with contenedor_graficas:
                        ui.plotly(fig).classes("w-full h-[600px]")

                ui.button("Generar gráfica", on_click=generar)

            elif event.value == "Comparar Volumen":
                with lista_inputs:
                    fecha_1_inicio = ui.date("Inicio del primer periodo")
                    fecha_1_fin = ui.date("Fin del primer periodo")
                    fecha_2_inicio = ui.date("Inicio del segundo periodo")
                    fecha_2_fin = ui.date("Fin del segundo periodo")
                    activo_seleccionado = ui.select(ACTIVOS, value=ACTIVOS[0])

                def generar_comparacion():
                    f1_ini = fecha_1_inicio.value
                    f1_fin = fecha_1_fin.value
                    f2_ini = fecha_2_inicio.value
                    f2_fin = fecha_2_fin.value
                    activo = activo_seleccionado.value

                    if not all([f1_ini, f1_fin, f2_ini, f2_fin]):
                        ui.notify("Completa todas las fechas", type="warning")
                        return

                    if f1_ini >= f1_fin or f2_ini >= f2_fin:
                        ui.notify("Las fechas de inicio deben ser menores a las de fin", type="warning")
                        return

                    try:
                        df1 = get_price_data(activo, f1_ini, f1_fin).reset_index()
                        df2 = get_price_data(activo, f2_ini, f2_fin).reset_index()

                        fig = build_volume_comparison_chart(df1, df2, activo, f1_ini, f1_fin, f2_ini, f2_fin)
                        contenedor_graficas.clear()
                        with contenedor_graficas:
                            ui.plotly(fig).classes("w-full h-[600px]")

                    except Exception as e:
                        ui.notify(f"Error al obtener los datos: {e}", type="error")

                ui.button("Generar comparación", on_click=generar_comparacion)

        actualizar_inputs(metodo_grafica_seleccionada)
        metodo_grafica_seleccionada.on_value_change(actualizar_inputs)

