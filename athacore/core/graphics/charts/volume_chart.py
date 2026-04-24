import plotly.graph_objects as go
import pandas as pd

# Gráfica de volumen

def build_volume_chart(df: pd.DataFrame, symbol: str, start: str, end: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Volume"],
        mode='lines',
        name='Volumen'
    ))
    
    fig.update_layout(
        title=f"Volumen de {symbol} entre {start} y {end}",
        xaxis_title="Fecha",
        yaxis_title="Volumen",
        xaxis=dict(tickformat="%Y-%m-%d", type="date")
    )

    return fig
