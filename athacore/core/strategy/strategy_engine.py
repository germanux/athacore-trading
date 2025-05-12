from athacore.core.data.market_data import get_price_data
from athacore.core.indicators.indicators import sma, rsi, macd
import pandas as pd


def estrategia_basica_medias(df: pd.DataFrame) -> list:
    """Compra si cruce de SMA corto sobre SMA largo, vende si lo contrario."""
    df['SMA_short'] = sma(df, 5)
    df['SMA_long'] = sma(df, 20)

    señales = []
    for i in range(1, len(df)):
        if df['SMA_short'].iloc[i] > df['SMA_long'].iloc[i] and df['SMA_short'].iloc[i - 1] <= df['SMA_long'].iloc[i - 1]:
            señales.append((df.index[i], df["Date"][i], 'BUY'))
        elif df['SMA_short'].iloc[i] < df['SMA_long'].iloc[i] and df['SMA_short'].iloc[i - 1] >= df['SMA_long'].iloc[i - 1]:
            señales.append((df.index[i], df["Date"][i], 'SELL'))
    return señales


def estrategia_rsi_simple(df: pd.DataFrame) -> list:
    """Compra cuando RSI < 30, vende cuando RSI > 70."""
    df['RSI'] = rsi(df, window=14)

    señales = []
    for i in range(1, len(df)):
        if df['RSI'].iloc[i] < 30:
            señales.append((df.index[i], 'BUY'))
        elif df['RSI'].iloc[i] > 70:
            señales.append((df.index[i], 'SELL'))
    return señales


def estrategia_macd_cruce(df: pd.DataFrame) -> list:
    """Compra si línea MACD cruza por encima de la señal; vende si cruza por debajo."""
    macd_df = macd(df)
    df['macd_line'] = macd_df['macd_line']
    df['signal_line'] = macd_df['signal_line']

    señales = []
    for i in range(1, len(df)):
        if df['macd_line'].iloc[i] > df['signal_line'].iloc[i] and df['macd_line'].iloc[i - 1] <= df['signal_line'].iloc[i - 1]:
            señales.append((df.index[i], 'BUY'))
        elif df['macd_line'].iloc[i] < df['signal_line'].iloc[i] and df['macd_line'].iloc[i - 1] >= df['signal_line'].iloc[i - 1]:
            señales.append((df.index[i], 'SELL'))
    return señales


# Registro centralizado de estrategias

def mostrar_estrategias() -> dict:
    return {
        "estrategia_basica_medias": estrategia_basica_medias,
        "estrategia_rsi_simple": estrategia_rsi_simple,
        "estrategia_macd_cruce": estrategia_macd_cruce,
        "default": estrategia_basica_medias,
    }


def run_analysis(strategy_name: str, ticker: str, start: str, end: str) -> list:
    """
    Ejecuta el análisis completo: obtiene datos, aplica estrategia y retorna señales.
    """
    df = get_price_data(ticker, start_date=start, end_date=end)
    if df.empty:
        raise ValueError("No se pudieron obtener datos.")

    estrategia_fn = mostrar_estrategias().get(strategy_name)

    if not estrategia_fn:
        raise NotImplementedError(f"Estrategia no implementada: {strategy_name}")

    return estrategia_fn(df)
