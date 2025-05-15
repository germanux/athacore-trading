# Gráfica anualizada
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

def build_annual_candlestick(ticker, year):
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    data = yf.Ticker(ticker).history(start=start_date, end=end_date)
    data.index = data.index.strftime('%Y-%m-%d')
    
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        increasing_line_color='green',
        decreasing_line_color='red',
    )])
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'].rolling(window=20).mean(),
        line=dict(color='blue', width=1.5),
        name='20-Day MA'
    ))
    fig.update_layout(
        title=f'{ticker} Volumen Anual ({year})',
        yaxis_title='Precio (USD)',
        xaxis_rangeslider_visible=True,
        plot_bgcolor='lightgray',
        paper_bgcolor='white',
        hovermode="x unified",
    )
    return fig.to_dict()