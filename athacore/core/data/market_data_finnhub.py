import pandas as pd
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from time import mktime

# Carga la clave API desde el archivo .env
load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def get_price_data(symbol: str, start_date: str, end_date: str, config: dict=None) -> pd.DataFrame:
    """
    Obtiene datos históricos diarios de acciones desde Finnhub.
    """

    def to_unix(date_str):
        return int(mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple()))

    url = "https://finnhub.io/api/v1/stock/candle"
    params = {
        "symbol": symbol,
        "resolution": "D",
        "from": to_unix(start_date),
        "to": to_unix(end_date),
        "token": FINNHUB_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("s") != "ok":
        print(f"[MARKET_DATA_FINNHUB]: Error fetching data para {symbol}: {data}")
        return pd.DataFrame()

    df = pd.DataFrame({
    "Date": pd.to_datetime(data["t"], unit="s"),
    "Close": pd.to_numeric(data["c"], errors='coerce'),
    "High": pd.to_numeric(data["h"], errors='coerce'),
    "Low": pd.to_numeric(data["l"], errors='coerce'),
    "Open": pd.to_numeric(data["o"], errors='coerce'),
    "Volume": pd.to_numeric(data["v"], errors='coerce')
    })

    df.dropna(inplace=True)
    df["Volume"] = df["Volume"].astype("int64") #int64 no acepta nulls. Se limpia el df con dropna y se ajusta el tipo de dato

    print(f"[MARKET_DATA_FINNHUB]: Datos descargados: \n{df.head()}")

    metadata = {
        "market_data":{
            "source": "finnhub",
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
