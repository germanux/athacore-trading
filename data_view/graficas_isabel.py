#Modularizacion
from nicegui import ui

import plotly.graph_objects as go
import yfinance as yf
import pandas as pd

def grafica_simple(fecha_inicio:str, activo:str):
        print(f"Datos pasados a la gráfica:\n- Fecha de inicio: {fecha_inicio}\n- Activo: {activo}")

        fecha_final = "2025-4-1" #Se podria implementar la libreria de datetime para poner la fecha actual
        
        # TOMAR DATOS
        data = yf.download(activo, fecha_inicio, fecha_final)
        data = data.reset_index()

        # Limpiar multinivel
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # CREAR GRÁFICA
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x = data["Date"],
            y = data["Volume"],
        ))
        
        fig.update_layout(
            title=f"Volumen de {activo} entre {fecha_inicio} y {fecha_final}",
            xaxis_title="Fecha",
            yaxis_title="Volumen",
            xaxis=dict(
                tickformat="%Y-%m-%d",
                type="date"
            )
        )
        
        return ui.plotly(fig).classes("w-full h-200")
        