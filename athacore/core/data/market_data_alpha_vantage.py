# Cambio de librería yahooFinance por Alpha_Vantage
from alpha_vantage.timeseries import TimeSeries
import pandas as pd

API_KEY = 'TGKRRFLLV1V6JBWN'  #API KEY PE4PD5KAIAK4VS72

"""
Falta implementar candle_size
"""
def get_price_data(symbol: str, start_date: str, end_date: str, config:dict = None) -> pd.DataFrame:
    # Inicializar el object TimeSeries de Alpha Vantage 
    ts = TimeSeries(key=API_KEY, output_format='pandas')

    try:
        # Obtener datos (fetch) diarios de Alpha_Vantage
        data, meta_data = ts.get_daily(symbol=symbol, outputsize='full')

        # Convertir fecha a índice para filtrar
        data.index = pd.to_datetime(data.index)
        df = data[(data.index >= start_date) & (data.index <= end_date)]

        #Procesado del df
        df = df.reset_index()
        df.rename(columns={
            "date": "Date",
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'Volume'
        }, inplace=True)
        df.drop("index", axis=1, inplace=True)
        df = df[['Date', 'Close', 'High', 'Low', 'Open', 'Volume']]

        # Asegurar tipos correctos
        df['Date'] = pd.to_datetime(df['Date'])
        df['Volume'] = df['Volume'].astype('int64')

        print(f"[MARKET_DATA_ALPHAVANTAGE]: Datos descargados: \n{df.head()}")

        metadata = {
        "market_data":{
            "source": "Alphavantage",
            "symbol": symbol,
            #"name": company_name,
            #"exchange": info.get('exchange', 'N/A'),
            #"currency": info.get('currency', 'USD'),
            #"secType": info.get('quoteType', 'stock'),
            "start_date": start_date,
            "end_date": end_date,
            "config": config,
            "df_info": df.info()
        }}

        return df, metadata

    except Exception as e:
        print(f"[MARKET_DATA_ALPHAVANTAGE]: Error fetching datos for {symbol}: {e}")
        return pd.DataFrame()

"""
# Ejemplo de ejecución (visible sólo en la terminal)
df = get_price_data('AAPL', '2023-01-01', '2023-12-31')
print(df.head())
"""
