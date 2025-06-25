import pandas as pd
import requests
from datetime import datetime


def get_price_data(symbol: str, start_date: str, end_date: str, bar_size: str = "15min", api_key: str = None) -> pd.DataFrame:
    print(f"[TwelveData DEBUG] Intervalo recibido por función: {bar_size}")
    print(f"[TwelveData] Solicitando datos para {symbol} de {start_date} a {end_date} con intervalo {bar_size}")

    interval = bar_size.replace("min", "min")  # ya viene como "15min", etc.

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "start_date": start_date,
        "end_date": end_date,
        "apikey": api_key,
        "format": "JSON",
        "outputsize": 5000
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "values" not in data:
        raise ValueError(f"No se obtuvieron datos válidos para {symbol} desde Twelve Data.")

    df = pd.DataFrame(data["values"])

    # Conversión y renombre de columnas
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.rename(columns={
        "datetime": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    })
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    # Convertir todas las columnas numéricas de texto a float
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])
    df = df.sort_values("Date")
    df = df.reset_index(drop=True)

    print(f"[TwelveData] Datos recibidos: {len(df)} filas desde la API")

    return df
