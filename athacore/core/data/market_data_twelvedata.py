import pandas as pd
import requests
from datetime import datetime
import os

# Reemplaza con tu propia API Key de Twelve Data
twelve_data_api_key = os.getenv("TWELVE_DATA_API_KEY", "TU_API_KEY_AQUI")

def get_price_data(symbol: str, start_date: str, end_date: str,  config: dict=None, api_key: str = twelve_data_api_key) -> pd.DataFrame:
    candle_size = "15min"
    if config:
        candle_size = config["candle_size"]

    print(f"MARKET_DATA_TWELVEDATA]: Se pasaron los siguientes parametros. \n CandleSize: {candle_size}")

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": candle_size,
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
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.rename(columns={
        "datetime": "Date",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    })

    # Convertir columnas numéricas
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Eliminar filas con NaNs
    df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])

    # Asegurar tipo int64 para Volume
    df["Volume"] = df["Volume"].astype("int64")

    # Ordenar y reordenar columnas
    df = df.sort_values("Date").reset_index(drop=True)
    df = df[["Date", "Close", "High", "Low", "Open", "Volume"]]

    print(f"[MARKET_DATA_TWELVEDATA]: Datos descargados: \n{df.head()}")

    metadata = {
        "market_data":{
            "source": "TwelveData",
            "symbol": symbol,
            #"name": company_name,
            #"exchange": info.get('exchange', 'N/A'),
            #"currency": info.get('currency', 'USD'),
            #"secType": info.get('quoteType', 'stock'),
            "start_date": start_date,
            "end_date": end_date,
            #"config": config,
            "df_info": df.info()
        }}
    return df, metadata