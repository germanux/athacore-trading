import yfinance as yf
import pandas as pd

def get_price_data(symbol: str, start_date: str, end_date: str, bar_size: str = '15m') -> pd.DataFrame:
    df = yf.download(symbol, start=start_date, end=end_date, interval=bar_size).reset_index()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df
