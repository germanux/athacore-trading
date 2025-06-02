# === FUENTE DE DATOS ===
# Usa Yahoo Finance como fuente principal; si falla, usa Alpha Vantage como respaldo.
try:
    from athacore.core.data.market_data_yhfinance import get_price_data
except ImportError:
    from athacore.core.data.market_data_alpha_vantage import get_price_data
# Importa indicadores técnicos SMA, RSI y MACD
from athacore.core.indicators.indicators import sma, rsi, macd  
import pandas as pd

# Estándares para la creación de señales
COLUMNAS = ["indice", "fecha", "volumen", "cierre", "compra"]

def add_signal(df, i, señal):
    return df.index[i], df.iloc[i]["Date"], df.iloc[i]["Volume"], df.iloc[i]["Close"], señal

# === BASE CONFIGURABLE ===
class EstrategiaBase:
    def __init__(self, config=None):
        self.config = self.get_default_config()
        if config:
            self.config.update(config)

    def get_default_config(self):
        return {
            "candle_size": "15min",
            "lookback_period": 14,
            "total_data_needed": 30,
            "execution_frequency": "on_new_candle",
            "signal_delay": 1,
            "time_filter": {"start": "09:00", "end": "17:00"},
            "symbols_supported": [],
            "slippage_tolerance": 0.1,
        }

# === ESTRATEGIAS ===
# ESTRATEGIA RSI SIMPLE: puntos de sobrecompra y sobreventa.
class EstrategiaRSI(EstrategiaBase):
    def aplicar(self, df):
        df.index = pd.to_datetime(df.index)
        df['RSI'] = rsi(df, window=self.config["lookback_period"])
        señales = []
        for i in range(1, len(df)):
            if df['RSI'].iloc[i] < 30:
                señales.append(add_signal(df, i, True))
            elif df['RSI'].iloc[i] > 70:
                señales.append(add_signal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

# ESTRATEGIA MACD: cruce de líneas MACD y señal.
class EstrategiaMACD(EstrategiaBase):
    def aplicar(self, df):
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

# ESTRATEGIA BÁSICA DE MEDIAS: cruce de medias móviles simples.
class EstrategiaMediasSimples(EstrategiaBase):
    def aplicar(self, df):
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

# MOMENTUM: fuerza de precio y volumen como señales de entrada y salida.
class EstrategiaMomentum(EstrategiaBase):
    def aplicar(self, df):
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
class EstrategiaScalping(EstrategiaBase):
    def aplicar(self, df):
        df.index = pd.to_datetime(df.index)
        df['SMA_5'] = sma(df, 5)
        señales = []
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > df['SMA_5'].iloc[i] and df['Close'].iloc[i - 1] <= df['SMA_5'].iloc[i - 1]:
                señales.append(add_signal(df, i, True))
            elif df['Close'].iloc[i] < df['SMA_5'].iloc[i] and df['Close'].iloc[i - 1] >= df['SMA_5'].iloc[i - 1]:
                señales.append(add_signal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

# MEAN REVERSION: se basa en que el precio vuelve a su media tras alejarse.
class EstrategiaReversionMedia(EstrategiaBase):
    def aplicar(self, df):
        df.index = pd.to_datetime(df.index)
        df['SMA_20'] = sma(df, 20)
        señales = []
        for i in range(1, len(df)):
            if df['Close'].iloc[i] < df['SMA_20'].iloc[i] * 0.97:
                señales.append(add_signal(df, i, True))
            elif df['Close'].iloc[i] > df['SMA_20'].iloc[i] * 1.03:
                señales.append(add_signal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

# TREND FOLLOWING: detecta tendencias sostenidas basadas en medias de 50 y 200.
class EstrategiaTendencia(EstrategiaBase):
    def aplicar(self, df):
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

# === REGISTRO DE ESTRATEGIAS ===
def mostrar_estrategias(config=None):
    return {
        "estrategia_rsi_simple": EstrategiaRSI(config),
        "estrategia_macd_cruce": EstrategiaMACD(config),
        "estrategia_basica_medias": EstrategiaMediasSimples(config),
        "estrategia_momentum": EstrategiaMomentum(config),
        "estrategia_scalping": EstrategiaScalping(config),
        "estrategia_reversion_media": EstrategiaReversionMedia(config),
        "estrategia_seguimiento_tendencia": EstrategiaTendencia(config),
    }

# === EJECUCIÓN ===
# Ejecuta el análisis completo: obtiene datos, aplica estrategia y retorna señales.
# Intenta con Yahoo Finance, luego Alpha Vantage, y finalmente Finnhub si es necesario.
def run_analysis(strategy_name: str, ticker: str, start: str, end: str, config=None) -> pd.DataFrame:
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

    estrategias = mostrar_estrategias(config)
    estrategia = estrategias.get(strategy_name)
    if not estrategia:
        raise NotImplementedError(f"Estrategia no implementada: {strategy_name}")

    print(["STRATEGY_ENGINE: Estrategia aplicada correctamente"])
    return estrategia.aplicar(df)
