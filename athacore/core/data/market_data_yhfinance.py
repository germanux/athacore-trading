import yfinance as yf
import pandas as pd

def get_price_data(symbol: str, start_date: str, end_date: str, config: dict=None) -> pd.DataFrame:
    if config is None:
        df = yf.download(symbol, start=start_date, end=end_date).reset_index()
        #Pensar en usar **kwargs si se complican los parametros de config
    else:
        candle_size=format_map[config["candle_size"]]
        df = yf.download(symbol, start=start_date, end=end_date, interval=candle_size).reset_index()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.rename(columns={'Datetime': 'Date'}, inplace=True)
    print(f"[MARKET_DATA_YHFINANCE]: Datos descargados: \n{df.head()}")
    return df

# Mapeo de los valores que pasamos desde la interfaz a los aceptados por yh finance
format_map = {
    "1min": "1m",
    "5min": "5m",
    "15min": "15m",
    "30min": "30m",
    "1h": "1h",
    "1d": "1d",
    "1w": "1wk",
    "1m": "1mo"
}