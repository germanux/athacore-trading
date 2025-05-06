# Gráfica comparativa VC
import plotly.graph_objects as go
import pandas as pd

def build_volume_comparison_chart(df1: pd.DataFrame, df2: pd.DataFrame, symbol: str,
                                   start1: str, end1: str, start2: str, end2: str) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df1["Date"],
        y=df1["Volume"],
        mode='lines',
        name=f'Volumen {start1} a {end1}'
    ))

    fig.add_trace(go.Scatter(
        x=df2["Date"],
        y=df2["Volume"],
        mode='lines',
        name=f'Volumen {start2} a {end2}'
    ))

    fig.update_layout(
        title=f"Comparación de Volumen de {symbol}",
        xaxis_title="Fecha",
        yaxis_title="Volumen",
        xaxis=dict(tickformat="%Y-%m-%d", type="date")
    )

    return fig
