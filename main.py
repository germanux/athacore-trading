from nicegui import ui

# Importaciones de las vistas (pestañas)
from athacore.gui.tabs.dashboard import render_dashboard
from athacore.gui.tabs.data_view import render_data_view
from athacore.gui.tabs.graphics_view import render_graphics_view
from athacore.gui.tabs.strategy_view import render_strategy_view
from athacore.gui.tabs.execution_view import render_execution_view
from athacore.gui.tabs.backtesting_view import render_backtesting_view
from athacore.gui.tabs.logs_view import render_logs_view
from athacore.gui.tabs.settings_view import render_settings_view

# Configuración de pestañas
tabs_config = [
    ('Dashboard', render_dashboard),
    ('Datos de mercado', render_data_view),
    ('Gráficas', render_graphics_view),
    ('Estrategias', render_strategy_view),
    ('Ejecución', render_execution_view),
    ('Backtesting', render_backtesting_view),
    ('Logs', render_logs_view),
    ('Configuración', render_settings_view),
]

# Crear las pestañas en la interfaz
with ui.tabs().classes('w-full') as tabs:
    tab_headers = [ui.tab(nombre) for nombre, _ in tabs_config]

with ui.tab_panels(tabs, value=tab_headers[0]).classes('w-full'):
    for (nombre, render_func), tab in zip(tabs_config, tab_headers):
        with ui.tab_panel(tab):
            try:
                render_func()
            except Exception as e:
                ui.label(f"⚠️ Error al cargar la pestaña '{nombre}': {e}")

# Lanzar la app
ui.run()
