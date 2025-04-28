import yfinance as yf
import pandas as pd

def obtener_datos(ticker: str, inicio: str, fin: str) -> pd.DataFrame:
    try:
        df = yf.download(ticker, start=inicio, end=fin)
        if df.empty:
            print(f"⚠️ No se encontraron datos para {ticker}")
        return df
    except Exception as e:
        print(f"❌ Error al obtener datos de {ticker}: {e}")
        return pd.DataFrame()
