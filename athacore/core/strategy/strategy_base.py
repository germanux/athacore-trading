# === Imports y Utilidades ===
import pandas as pd
import os
from athacore.core.strategy.strategy_recommend import RECOMENDACIONES

COLUMNAS = ["indice", "fecha", "volumen", "cierre", "compra"]

def generar_senal(df, i, señal):
    return df.index[i], df.iloc[i]["Date"], df.iloc[i]["Volume"], df.iloc[i]["Close"], señal

def load_local_csv(ticker, start=None, end=None):
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(base_dir, "data")
        path = os.path.join(data_dir, f"{ticker}.csv")

        print(f"📄 Cargando archivo: {path}")
        df = pd.read_csv(path, thousands=",")

        rename_map = {"Vol.": "Volume", "Price": "Close"}
        df.rename(columns=rename_map, inplace=True)

        if "Volume" in df.columns:
            df["Volume"] = df["Volume"].str.replace("M", "", regex=False)
            df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce") * 1_000_000

        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date"])
            df = df.sort_values("Date")
            df.set_index("Date", inplace=True)
            if start and end:
                print("⏱️ Fechas recibidas:", start, "→", end)
                df = df[(df.index >= pd.to_datetime(start)) & (df.index <= pd.to_datetime(end))]

        return df.dropna(subset=["Close", "Volume"])

    except Exception as e:
        print(f"❌ Error al cargar el archivo local para {ticker}: {e}")
        return pd.DataFrame()

# === BASE DE ESTRATEGIA ===
class EstrategiaBase:
    def __init__(self, config=None):
        if not hasattr(self, "nombre_interno"):
            self.nombre_interno = self.__class__.__name__.lower() # <- Asignación automática
        self.nombre_interno = getattr(self, "nombre_interno", None)
        self.config = self.get_default_config()
        if config:
            self.config.update(config)
    
    def tiene_datos_suficientes(self, df):
        return len(df) >= self.config.get("total_data_needed", 0)

    def get_default_config(self):
        claves = {
            "candle_size": "15min",
            "lookback_period": 0,
            "total_data_needed": 0,
            "execution_frequency": "on_new_candle",
            "signal_delay": 1,
            "time_filter": {"start": "09:00", "end": "17:00"},
            "symbols_supported": [],
            "slippage_tolerance": 0.1,
        }

        if self.nombre_interno and self.nombre_interno in RECOMENDACIONES:
            claves.update(RECOMENDACIONES[self.nombre_interno])

        return claves
    
#INDICADORES (sma, rsi, macd)
def sma(df, window):
    return df['Close'].rolling(window=window).mean()

def rsi(df, window):
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def macd(df, short_window=12, long_window=26, signal_window=9):
    short_ema = df['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = df['Close'].ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    return pd.DataFrame({'macd_line': macd_line, 'signal_line': signal_line})