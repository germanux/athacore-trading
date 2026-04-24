# Gráfica anualizada
# Cambio de librería yahooFinance por Alpha_Vantage
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import plotly.graph_objects as go

API_KEY = 'PE4PD5KAIAK4VS72'  # API Key obtenida por subscribirse en "Alpha Vantage"

def build_annual_candlestick(ticker, year):
    try:
        # Obtener datos (fetch) de Alpha Vantage
        ts = TimeSeries(key=API_KEY, output_format='pandas')
        data, meta_data = ts.get_daily(symbol=ticker, outputsize='full')

        # Filtrar datos por el año específicado
        data.index = pd.to_datetime(data.index)
        data = data[(data.index.year == int(year))]

        if data.empty:
            print(f"No data available for {ticker} in {year}.")
            return None

        # Mostrar el gráfico de velas (candlesticks)
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['1. open'],
            high=data['2. high'],
            low=data['3. low'],
            close=data['4. close'],
            increasing_line_color='green',
            decreasing_line_color='red',
        )])

        # Añadir la línea de la media móvil de 20 días (MA)
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['4. close'].rolling(window=20).mean(),
            line=dict(color='blue', width=1.5),
            name='20-Day MA'
        ))

        # Actualizar layout
        fig.update_layout(
            title=f'{ticker} Annual Candlestick ({year})',
            yaxis_title='Price (USD)',
            xaxis_rangeslider_visible=True,
            plot_bgcolor='lightgray',
            paper_bgcolor='white',
            hovermode="x unified",
        )
        
        return fig.to_dict()

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

"""
# Ejemplo en terminal
chart = build_annual_candlestick('AAPL', '2023')
if chart:
    print("Chart generated successfully!")
"""