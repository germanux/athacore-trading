# Cambio de librería yahooFinance por Alpha_Vantage
from alpha_vantage.timeseries import TimeSeries
import pandas as pd

API_KEY = 'TGKRRFLLV1V6JBWN'  #API KEY PE4PD5KAIAK4VS72

def get_price_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    # Inicializar el object TimeSeries de Alpha Vantage 
    ts = TimeSeries(key=API_KEY, output_format='pandas')

    try:
        # Obtener datos (fetch) diarios de Alpha_Vantage
        data, meta_data = ts.get_daily(symbol=symbol, outputsize='full')

        # Convertir de index a datetime para filtar mediante fecha
        data.index = pd.to_datetime(data.index)

        # Filtrar los datos por un rango de fecha
        filtered_data = data[(data.index >= start_date) & (data.index <= end_date)]

        # Columnas de la gráfica
        filtered_data.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'Volume'
        }, inplace=True)

        return filtered_data.reset_index()

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

# Ejemplo de ejecución (visible sólo en la terminal)
df = get_price_data('AAPL', '2023-01-01', '2023-12-31')
print(df.head())
