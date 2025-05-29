import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Carga la clave API desde el archivo .env
load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def get_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Obtiene datos históricos diarios de acciones desde Finnhub.
    """
    from datetime import datetime
    from time import mktime

    def to_unix(date_str):
        return int(mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple()))

    url = "https://finnhub.io/api/v1/stock/candle"
    params = {
        "symbol": ticker,
        "resolution": "D",
        "from": to_unix(start_date),
        "to": to_unix(end_date),
        "token": FINNHUB_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("s") != "ok":
        print(f"Error fetching data for {ticker}: {data}")
        return pd.DataFrame()

    df = pd.DataFrame({
        "Date": pd.to_datetime(data["t"], unit="s"),
        "Open": data["o"],
        "High": data["h"],
        "Low": data["l"],
        "Close": data["c"],
        "Volume": data["v"]
    })

    df.set_index("Date", inplace=True)
    return df
