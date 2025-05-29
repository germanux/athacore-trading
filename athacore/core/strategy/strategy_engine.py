try:
    from athacore.core.data.market_data_yhfinance import get_price_data  # Yahoo Finance como fuente primaria
except ImportError:
    from athacore.core.data.market_data_alpha_vantage import get_price_data  # Alpha Vantage como respaldo
from athacore.core.indicators.indicators import sma, rsi, macd  # Importa indicadores técnicos SMA, RSI y MACD
import pandas as pd

# Estándares para la creación de señales
COLUMNAS = ["indice", "fecha", "volumen", "cierre", "compra"]
def add_signal(df, i, señal):
    return df.index[i], df.iloc[i]["Date"],df.iloc[i]["Volume"], df.iloc[i]["Close"], señal

# === ESTRATEGIAS DE TRADING ===

# ESTRATEGIA BÁSICA DE MEDIAS: cruce de medias móviles simples.
def estrategia_basica_medias(df: pd.DataFrame) -> pd.DataFrame:
    df.index = pd.to_datetime(df.index)
    df['SMA_short'] = sma(df, 5)
    df['SMA_long'] = sma(df, 20)

    señales = []
    for i in range(1, len(df)):
        if df['SMA_short'].iloc[i] > df['SMA_long'].iloc[i] and df['SMA_short'].iloc[i - 1] <= df['SMA_long'].iloc[i - 1]:
            señales.append(add_signal(df, i, True))
        elif df['SMA_short'].iloc[i] < df['SMA_long'].iloc[i] and df['SMA_short'].iloc[i - 1] >= df['SMA_long'].iloc[i - 1]:
            señales.append(add_signal(df, i, False))

    return pd.DataFrame(señales, columns=COLUMNAS)

# ESTRATEGIA RSI SIMPLE: puntos de sobrecompra y sobreventa.
def estrategia_rsi_simple(df: pd.DataFrame) -> pd.DataFrame:
    df.index = pd.to_datetime(df.index)
    df['RSI'] = rsi(df, window=14)

    señales = []
    for i in range(1, len(df)):
        if df['RSI'].iloc[i] < 30:
            señales.append(add_signal(df, i, True))
        elif df['RSI'].iloc[i] > 70:
            señales.append(add_signal(df, i, False))

    return pd.DataFrame(señales, columns=COLUMNAS)


# ESTRATEGIA MACD: cruce de líneas MACD y señal.
def estrategia_macd_cruce(df: pd.DataFrame) -> pd.DataFrame:
    df.index = pd.to_datetime(df.index)
    macd_df = macd(df)
    df['macd_line'] = macd_df['macd_line']
    df['signal_line'] = macd_df['signal_line']

    señales = []
    for i in range(1, len(df)):
        if df['macd_line'].iloc[i] > df['signal_line'].iloc[i] and df['macd_line'].iloc[i - 1] <= df['signal_line'].iloc[i - 1]:
            señales.append(add_signal(df, i, True))
        elif df['macd_line'].iloc[i] < df['signal_line'].iloc[i] and df['macd_line'].iloc[i - 1] >= df['signal_line'].iloc[i - 1]:
            señales.append(add_signal(df, i, False))

    return pd.DataFrame(señales, columns=COLUMNAS)



# DAY TRADING: señales rápidas como RSI y CCI para operar intradía.
def estrategia_day_trading(df: pd.DataFrame) -> pd.DataFrame:
    df.index = pd.to_datetime(df.index)
    df['RSI'] = rsi(df, window=14)
    df['CCI'] = sma(df, 14)

    señales = []
    for i in range(1, len(df)):
        if df['RSI'].iloc[i] < 35 and df['CCI'].iloc[i] < -100:
            señales.append(add_signal(df, i, True))
        elif df['RSI'].iloc[i] > 65 and df['CCI'].iloc[i] > 100:
            señales.append(add_signal(df, i, False))

    return pd.DataFrame(señales, columns=COLUMNAS)


# MOMENTUM: fuerza de precio y volumen como señales de entrada y salida.
def estrategia_momentum(df: pd.DataFrame) -> pd.DataFrame:
    df.index = pd.to_datetime(df.index)
    df['SMA_20'] = sma(df, 20)
    df['Volumen_Medio'] = df['Volume'].rolling(window=20).mean()

    señales = []
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['SMA_20'].iloc[i] and df['Volume'].iloc[i] > df['Volumen_Medio'].iloc[i]:
            señales.append(add_signal(df, i, True))
        elif df['Close'].iloc[i] < df['SMA_20'].iloc[i]:
            señales.append(add_signal(df, i, False))

    return pd.DataFrame(señales, columns=COLUMNAS)

# SCALPING: entradas y salidas rápidas basadas en cruce de media muy corta.
def estrategia_scalping(df: pd.DataFrame) -> pd.DataFrame:
    df.index = pd.to_datetime(df.index)
    df['SMA_5'] = sma(df, 5)

    señales = []
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['SMA_5'].iloc[i] and df['Close'].iloc[i - 1] <= df['SMA_5'].iloc[i - 1]:
            señales.append(add_signal(df, i, True))
        elif df['Close'].iloc[i] < df['SMA_5'].iloc[i] and df['Close'].iloc[i - 1] >= df['SMA_5'].iloc[i - 1]:
            señales.append(add_signal(df, i, False))

    return pd.DataFrame(señales, columns=COLUMNAS)


# TREND FOLLOWING: detecta tendencias sostenidas basadas en medias de 50 y 200.
def estrategia_seguimiento_tendencia(df: pd.DataFrame) -> pd.DataFrame:
    df.index = pd.to_datetime(df.index)
    df['SMA_50'] = sma(df, 50)
    df['SMA_200'] = sma(df, 200)

    señales = []
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['SMA_200'].iloc[i] and df['Close'].iloc[i] > df['SMA_50'].iloc[i]:
            señales.append(add_signal(df, i, True))
        elif df['Close'].iloc[i] < df['SMA_200'].iloc[i] and df['Close'].iloc[i] < df['SMA_50'].iloc[i]:
            señales.append(add_signal(df, i, False))

    return pd.DataFrame(señales, columns=COLUMNAS)


# MEAN REVERSION: se basa en que el precio vuelve a su media tras alejarse.
def estrategia_reversion_media(df: pd.DataFrame) -> pd.DataFrame:
    df.index = pd.to_datetime(df.index)
    df['SMA_20'] = sma(df, 20)

    señales = []
    for i in range(1, len(df)):
        if df['Close'].iloc[i] < df['SMA_20'].iloc[i] * 0.97:
            señales.append(add_signal(df, i, True))
        elif df['Close'].iloc[i] > df['SMA_20'].iloc[i] * 1.03:
            señales.append(add_signal(df, i, False))

    return pd.DataFrame(señales, columns=COLUMNAS)


# === REGISTRO CENTRALIZADO ===
def mostrar_estrategias() -> dict:
    return {
        "estrategia_basica_medias": estrategia_basica_medias,
        "estrategia_rsi_simple": estrategia_rsi_simple,
        "estrategia_macd_cruce": estrategia_macd_cruce,
        "estrategia_day_trading": estrategia_day_trading,
        "estrategia_momentum": estrategia_momentum,
        "estrategia_scalping": estrategia_scalping,
        "estrategia_seguimiento_tendencia": estrategia_seguimiento_tendencia,
        "estrategia_reversion_media": estrategia_reversion_media,
        "default": estrategia_basica_medias,
    }


# === EJECUCIÓN ===
def run_analysis(strategy_name: str, ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Ejecuta el análisis completo: obtiene datos, aplica estrategia y retorna señales.
    Intenta con Yahoo Finance, luego Alpha Vantage, y finalmente Finnhub si es necesario.
    """
    try:
        df = get_price_data(ticker, start_date=start, end_date=end)
        if df.empty:
            raise ValueError("Yahoo Finance falló o no devolvió datos.")
    except Exception as e:
        try:
            from athacore.core.data.market_data_alpha_vantage import get_price_data as get_price_data_alt
            df = get_price_data_alt(ticker, start_date=start, end_date=end)
            if df.empty:
                raise ValueError("Alpha Vantage también falló.")
        except Exception:
            try:
                from athacore.core.data.market_data_finnhub import get_price_data as get_price_data_finnhub
                df = get_price_data_finnhub(ticker, start_date=start, end_date=end)
                if df.empty:
                    raise ValueError("Finnhub también falló.")
            except Exception as final_e:
                print(f"Error recuperando datos: {final_e}")
                return pd.DataFrame()

    estrategia_fn = mostrar_estrategias().get(strategy_name)
    if not estrategia_fn:
        raise NotImplementedError(f"Estrategia no implementada: {strategy_name}")
    else:
        print(["STRATEGY_ENGINE: Estrategia aplicada correctamente"])
    return estrategia_fn(df)