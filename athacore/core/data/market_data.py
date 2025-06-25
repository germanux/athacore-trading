# athacore/core/data/market_data.py
import pandas as pd
import yfinance as yf
from typing import Literal

async def get_price_data(symbol: str, duration: str = '1d', bar_size: str = '5m', source: Literal['yfinance'] = 'yfinance') -> dict:
    """
    Obtiene datos históricos desde yfinance.
    :param symbol: Símbolo del activo (ej. 'AAPL').
    :param duration: Duración de los datos históricos (ej. '1d', '5d', '1mo').
    :param bar_size: Intervalo de los datos (ej. '1m', '5m', '1h', '1d').
    :param source: Fuente de datos, debe ser 'yfinance'.
    :return: Diccionario con datos históricos y detalles del activo.
    """
    if source != 'yfinance':
        raise ValueError("Solo se admite 'yfinance' como fuente de datos en esta versión.")

    return _get_yfinance_data(symbol, duration, bar_size)

async def _get_yfinance_data(symbol: str, duration: str = '1d', bar_size: str = '5m') -> dict:
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=duration, interval=bar_size)

    if df.empty:
        raise ValueError(f"No se obtuvieron datos históricos para {symbol}")

    df.reset_index(inplace=True)
    df['date'] = df['Datetime' if 'Datetime' in df else 'Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

    info = ticker.info
    company_name = info.get('longName') or info.get('shortName') or symbol

    return {
        "data": df[['date', 'Open', 'High', 'Low', 'Close', 'Volume']].rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }),
        "info": {
            "symbol": symbol,
            "name": company_name,
            "exchange": info.get('exchange', 'N/A'),
            "currency": info.get('currency', 'USD'),
            "secType": info.get('quoteType', 'stock'),
        }
    }
