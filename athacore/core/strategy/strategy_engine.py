# === IMPORTS Y UTILIDADES ===
import pandas as pd
import os

# Intenta importar desde Yahoo Finance; si falla, usa Alpha Vantage
try:
    from athacore.core.data.market_data_yhfinance import get_price_data
except ImportError:
    from athacore.core.data.market_data_alpha_vantage import get_price_data

from athacore.core.indicators.indicators import sma, rsi, macd

RECOMENDACIONES = {
    "estrategia_breakout": {"lookback_period": 5, "total_data_needed": 20},
    "estrategia_reversal": {"lookback_period": 2, "total_data_needed": 20},
    "estrategia_rango": {"lookback_period": 10, "total_data_needed": 30},
    "estrategia_day_trading": {"lookback_period": 10, "total_data_needed": 50},
    "estrategia_news_trading": {"lookback_period": 20, "total_data_needed": 40},
    "estrategia_rsi_simple": {"lookback_period": 14, "total_data_needed": 30},
    "estrategia_macd_cruce": {"lookback_period": 26, "total_data_needed": 35},
    "estrategia_basica_medias": {"lookback_period": 20, "total_data_needed": 30},
    "estrategia_momentum": {"lookback_period": 20, "total_data_needed": 40},
    "estrategia_scalping": {"lookback_period": 14, "total_data_needed": 30},
    "estrategia_reversion_media": {"lookback_period": 20, "total_data_needed": 40},
    "estrategia_seguimiento_tendencia": {"lookback_period": 50, "total_data_needed": 100},
    "estrategia_volume": {"lookback_period": 20, "total_data_needed": 30},
    "estrategia_price_action": {"lookback_period": 1, "total_data_needed": 10},
    "estrategia_swing_trading": {"lookback_period": 30, "total_data_needed": 50},
    "estrategia_position_trading": {"lookback_period": 100, "total_data_needed": 200},
    "estrategia_arbitraje_simulado": {"lookback_period": 10, "total_data_needed": 30},
    "estrategia_pair_trading": {"lookback_period": 15, "total_data_needed": 40}
}

COLUMNAS = ["indice", "fecha", "volumen", "cierre", "compra"]

def generar_senal(df, i, señal):
    return df.index[i], df.index[i], df.iloc[i]["Volume"], df.iloc[i]["Close"], señal

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
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")
            df.set_index("Date", inplace=True)
            if start and end:
                df = df[(df.index >= pd.to_datetime(start)) & (df.index <= pd.to_datetime(end))]

        return df.dropna(subset=["Close", "Volume"])

    except Exception as e:
        print(f"❌ Error al cargar el archivo local para {ticker}: {e}")
        return pd.DataFrame()

# === BASE DE ESTRATEGIA ===
class EstrategiaBase:
    def __init__(self, config=None):
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

#ESTRATEGIA BREAKOUT: compra si el precio supera la resistencia reciente
class EstrategiaBreakout(EstrategiaBase):
    nombre_interno = "estrategia_breakout"
    def aplicar(self, df):
        df['max_5'] = df['Close'].rolling(window=5).max()
        señales = []
        for i in range(5, len(df)):
            if df['Close'].iloc[i] > df['max_5'].iloc[i - 1]:
                señales.append(generar_senal(df, i, True))
            elif df['Close'].iloc[i] < df['max_5'].iloc[i - 1] * 0.98:
                señales.append(generar_senal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA REVERSAL: compra si hay reversión tras caída
class EstrategiaReversal(EstrategiaBase):
    nombre_interno = "estrategia_reversal"
    def aplicar(self, df):
        df['return'] = df['Close'].pct_change()
        señales = []
        for i in range(2, len(df)):
            if df['return'].iloc[i - 1] < -0.02 and df['return'].iloc[i] > 0.01:
                señales.append(generar_senal(df, i, True))
            elif df['return'].iloc[i - 1] > 0.02 and df['return'].iloc[i] < -0.01:
                señales.append(generar_senal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA RANGE TRADING
class EstrategiaRango(EstrategiaBase):
    nombre_interno = "estrategia_rango"
    def aplicar(self, df):
        df['min_10'] = df['Close'].rolling(window=10).min()
        df['max_10'] = df['Close'].rolling(window=10).max()
        señales = []
        for i in range(10, len(df)):
            if df['Close'].iloc[i] <= df['min_10'].iloc[i]:
                señales.append(generar_senal(df, i, True))
            elif df['Close'].iloc[i] >= df['max_10'].iloc[i]:
                señales.append(generar_senal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)
    
class EstrategiaDayTrading(EstrategiaBase):
    nombre_interno = "estrategia_day_trading"

    def aplicar(self, df):
        if not self.tiene_datos_suficientes(df):
            print("❌ No hay suficientes datos para aplicar estrategia_day_trading.")
            return pd.DataFrame(columns=COLUMNAS)

        lookback = self.config["lookback_period"]
        sma_largo = lookback * 5

        df['SMA_corta'] = sma(df, lookback)
        df['SMA_larga'] = sma(df, sma_largo)
        df['Volumen_Medio'] = df['Volume'].rolling(window=20).mean()

        señales = []
        for i in range(sma_largo, len(df)):
            if (
                df['SMA_corta'].iloc[i] > df['SMA_larga'].iloc[i]
                and df['Close'].iloc[i] > df['SMA_corta'].iloc[i]
                and df['Volume'].iloc[i] > df['Volumen_Medio'].iloc[i]
            ):
                señales.append(generar_senal(df, i, True))
            elif df['Close'].iloc[i] < df['SMA_corta'].iloc[i] * 0.995:
                señales.append(generar_senal(df, i, False))

        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA NEWS TRADING (SIMULADA): reacción a velas con gran volumen y rango
class EstrategiaNewsTrading(EstrategiaBase):
    nombre_interno = "estrategia_news_trading"
    def aplicar(self, df):
        df['rango'] = df['Close'].pct_change().abs()
        df['volumen_relativo'] = df['Volume'] / df['Volume'].rolling(20).mean()
        señales = []
        for i in range(20, len(df)):
            if df['rango'].iloc[i] > 0.03 and df['volumen_relativo'].iloc[i] > 2:
                señales.append(generar_senal(df, i, True))
            elif df['rango'].iloc[i] < 0.01 and df['volumen_relativo'].iloc[i] < 1:
                señales.append(generar_senal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA RSI SIMPLE: puntos de sobrecompra y sobreventa.
class EstrategiaRSI(EstrategiaBase):
    nombre_interno = "estrategia_rsi_simple"
    def aplicar(self, df):
        df['RSI'] = rsi(df, window=self.config["lookback_period"])
        señales = []
        for i in range(1, len(df)):
            if df['RSI'].iloc[i] < 30:
                señales.append(generar_senal(df, i, True))
            elif df['RSI'].iloc[i] > 70:
                señales.append(generar_senal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA MACD: cruce de líneas MACD y señal.
class EstrategiaMACD(EstrategiaBase):
    nombre_interno = "estrategia_macd_cruce"
    def aplicar(self, df):
        macd_df = macd(df)
        df['macd_line'] = macd_df['macd_line']
        df['signal_line'] = macd_df['signal_line']
        señales = []
        for i in range(1, len(df)):
            if df['macd_line'].iloc[i] > df['signal_line'].iloc[i] and df['macd_line'].iloc[i - 1] <= df['signal_line'].iloc[i - 1]:
                señales.append(generar_senal(df, i, True))
            elif df['macd_line'].iloc[i] < df['signal_line'].iloc[i] and df['macd_line'].iloc[i - 1] >= df['signal_line'].iloc[i - 1]:
                señales.append(generar_senal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA BÁSICA DE MEDIAS: cruce de medias móviles simples.
class EstrategiaMediasSimples(EstrategiaBase):
    nombre_interno = "estrategia_basica_medias"
    def aplicar(self, df):
        df['SMA_short'] = sma(df, 5)
        df['SMA_long'] = sma(df, 20)
        señales = []
        for i in range(1, len(df)):
            if df['SMA_short'].iloc[i] > df['SMA_long'].iloc[i] and df['SMA_short'].iloc[i - 1] <= df['SMA_long'].iloc[i - 1]:
                señales.append(generar_senal(df, i, True))
            elif df['SMA_short'].iloc[i] < df['SMA_long'].iloc[i] and df['SMA_short'].iloc[i - 1] >= df['SMA_long'].iloc[i - 1]:
                señales.append(generar_senal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

#MOMENTUM: fuerza de precio y volumen como señales de entrada y salida.
class EstrategiaMomentum(EstrategiaBase):
    nombre_interno = "estrategia_momentum"
    def aplicar(self, df):
        df['SMA_20'] = sma(df, 20)
        df['Volumen_Medio'] = df['Volume'].rolling(window=20).mean()
        señales = []
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > df['SMA_20'].iloc[i] and df['Volume'].iloc[i] > df['Volumen_Medio'].iloc[i]:
                señales.append(generar_senal(df, i, True))
            elif df['Close'].iloc[i] < df['SMA_20'].iloc[i]:
                señales.append(generar_senal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

#SCALPING: entradas y salidas rápidas basadas en cruce de media muy corta.
class EstrategiaScalping(EstrategiaBase):
    nombre_interno = "estrategia_scalping"
    def aplicar(self, df):
        df['SMA_5'] = sma(df, 5)
        df['RSI'] = rsi(df, window=self.config["lookback_period"])
        df['Volumen_Medio'] = df['Volume'].rolling(window=20).mean()

        señales = []
        for i in range(20, len(df)):
            if (
                df['Close'].iloc[i] > df['SMA_5'].iloc[i] and
                df['Close'].iloc[i - 1] <= df['SMA_5'].iloc[i - 1] and
                df['RSI'].iloc[i] < 70 and
                df['Volume'].iloc[i] > df['Volumen_Medio'].iloc[i]
            ):
                señales.append(generar_senal(df, i, True))
            elif (
                df['Close'].iloc[i] < df['SMA_5'].iloc[i] and
                df['Close'].iloc[i - 1] >= df['SMA_5'].iloc[i - 1] and
                df['RSI'].iloc[i] > 30 and
                df['Volume'].iloc[i] > df['Volumen_Medio'].iloc[i]
            ):
                señales.append(generar_senal(df, i, False))

        return pd.DataFrame(señales, columns=COLUMNAS)

#MEAN REVERSION: se basa en que el precio vuelve a su media tras alejarse.
class EstrategiaReversionMedia(EstrategiaBase):
    nombre_interno = "estrategia_reversion_media"
    def aplicar(self, df):
        df['SMA_20'] = sma(df, 20)
        señales = []
        for i in range(1, len(df)):
            if df['Close'].iloc[i] < df['SMA_20'].iloc[i] * 0.97:
                señales.append(generar_senal(df, i, True))
            elif df['Close'].iloc[i] > df['SMA_20'].iloc[i] * 1.03:
                señales.append(generar_senal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

#TREND FOLLOWING: detecta tendencias sostenidas basadas en medias de 50 y 200.
class EstrategiaTendencia(EstrategiaBase):
    nombre_interno = "estrategia_seguimiento_tendencia"
    def aplicar(self, df):
        df['SMA_50'] = sma(df, 50)
        df['SMA_200'] = sma(df, 200)
        señales = []
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > df['SMA_200'].iloc[i] and df['Close'].iloc[i] > df['SMA_50'].iloc[i]:
                señales.append(generar_senal(df, i, True))
            elif df['Close'].iloc[i] < df['SMA_200'].iloc[i] and df['Close'].iloc[i] < df['SMA_50'].iloc[i]:
                señales.append(generar_senal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA VOLUME: Detecta aumentos inusuales de volumen
class EstrategiaVolume(EstrategiaBase):
    nombre_interno = "estrategia_volume"
    def aplicar(self, df):
        df['Volumen_Medio'] = df['Volume'].rolling(window=20).mean()
        señales = []
        for i in range(20, len(df)):
            if df['Volume'].iloc[i] > 1.5 * df['Volumen_Medio'].iloc[i]:
                señales.append(generar_senal(df, i, True))
            elif df['Volume'].iloc[i] < 0.5 * df['Volumen_Medio'].iloc[i]:
                señales.append(generar_senal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA PRICE ACTION: Simulación simple basada en velas alcistas/bajistas
class EstrategiaPriceAction(EstrategiaBase):
    nombre_interno = "estrategia_price_action"
    def aplicar(self, df):
        señales = []
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > df['Open'].iloc[i] and df['Close'].iloc[i - 1] < df['Open'].iloc[i - 1]:
                señales.append(generar_senal(df, i, True))  # vela alcista tras bajista
            elif df['Close'].iloc[i] < df['Open'].iloc[i] and df['Close'].iloc[i - 1] > df['Open'].iloc[i - 1]:
                señales.append(generar_senal(df, i, False))  # vela bajista tras alcista
        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA SWING TRADING: Mantener posición de pocos días hasta semanas
class EstrategiaSwingTrading(EstrategiaBase):
    nombre_interno = "estrategia_swing_trading"
    def aplicar(self, df):
        df['SMA_10'] = sma(df, 10)
        df['SMA_30'] = sma(df, 30)
        return pd.DataFrame([
            generar_senal(df, i, True) if df['SMA_10'].iloc[i] > df['SMA_30'].iloc[i] and df['SMA_10'].iloc[i - 1] <= df['SMA_30'].iloc[i - 1]
            else generar_senal(df, i, False) if df['SMA_10'].iloc[i] < df['SMA_30'].iloc[i] and df['SMA_10'].iloc[i - 1] >= df['SMA_30'].iloc[i - 1]
            else None
            for i in range(1, len(df)) if generar_senal(df, i, True)
        ], columns=COLUMNAS)

#ESTRATEGIA POSITION TRADING: Mantener largos periodos si hay confirmación técnica
class EstrategiaPositionTrading(EstrategiaBase):
    nombre_interno = "estrategia_position_trading"
    def aplicar(self, df):
        df['SMA_100'] = sma(df, 100)
        df['SMA_200'] = sma(df, 200)
        return pd.DataFrame([
            generar_senal(df, i, True) if df['Close'].iloc[i] > df['SMA_100'].iloc[i] and df['Close'].iloc[i] > df['SMA_200'].iloc[i]
            else generar_senal(df, i, False) if df['Close'].iloc[i] < df['SMA_100'].iloc[i] and df['Close'].iloc[i] < df['SMA_200'].iloc[i]
            else None
            for i in range(200, len(df)) if generar_senal(df, i, True)
        ], columns=COLUMNAS)

#ESTRATEGIA ARBITRAGE(SIMULADA): Detecta diferencia de precios entre dos activos
class EstrategiaArbitrajeSimulado(EstrategiaBase):
    nombre_interno = "estrategia_arbitraje_simulado"
    def aplicar(self, df):
        if 'Close_B' not in df.columns:
            print("⚠️ Arbitraje requiere una segunda columna 'Close_B'")
            return pd.DataFrame()
        df['diff'] = df['Close'] - df['Close_B']
        media = df['diff'].rolling(10).mean()
        std = df['diff'].rolling(10).std()
        return pd.DataFrame([
            generar_senal(df, i, True) if df['diff'].iloc[i] < media.iloc[i] - std.iloc[i]
            else generar_senal(df, i, False) if df['diff'].iloc[i] > media.iloc[i] + std.iloc[i]
            else None
            for i in range(10, len(df)) if generar_senal(df, i, True)
        ], columns=COLUMNAS)

#ESTRATEGIA PAIR TRADING(SIMULADA): Largo en un activo, corto en otro correlacionado
class EstrategiaPairTradingSimulada(EstrategiaBase):
    nombre_interno = "estrategia_pair_trading"
    def aplicar(self, df):
        if 'Close_B' not in df.columns:
            print("⚠️ Pair Trading requiere columna 'Close_B'")
            return pd.DataFrame()
        df['spread'] = df['Close'] - df['Close_B']
        media = df['spread'].rolling(15).mean()
        std = df['spread'].rolling(15).std()
        return pd.DataFrame([
            generar_senal(df, i, True) if df['spread'].iloc[i] < media.iloc[i] - 1.5 * std.iloc[i]
            else generar_senal(df, i, False) if df['spread'].iloc[i] > media.iloc[i] + 1.5 * std.iloc[i]
            else None
            for i in range(15, len(df)) if generar_senal(df, i, True)
        ], columns=COLUMNAS)
def mostrar_estrategias(config=None):
    return {
        "estrategia_breakout": EstrategiaBreakout(config),
        "estrategia_reversal": EstrategiaReversal(config),
        "estrategia_rango": EstrategiaRango(config),
        "estrategia_day_trading": EstrategiaDayTrading(config),
        "estrategia_news_trading": EstrategiaNewsTrading(config),
        "estrategia_rsi_simple": EstrategiaRSI(config),
        "estrategia_macd_cruce": EstrategiaMACD(config),
        "estrategia_basica_medias": EstrategiaMediasSimples(config),
        "estrategia_momentum": EstrategiaMomentum(config),
        "estrategia_scalping": EstrategiaScalping(config),
        "estrategia_reversion_media": EstrategiaReversionMedia(config),
        "estrategia_seguimiento_tendencia": EstrategiaTendencia(config),
        "estrategia_volume": EstrategiaVolume(config),
        "estrategia_price_action": EstrategiaPriceAction(config),
        "estrategia_swing_trading": EstrategiaSwingTrading(config),
        "estrategia_position_trading": EstrategiaPositionTrading(config),
        "estrategia_arbitraje_simulado": EstrategiaArbitrajeSimulado(config),
        "estrategia_pair_trading": EstrategiaPairTradingSimulada(config)
    }

# === FUNCIONALIDAD DE ANÁLISIS ===
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
                print("🔁 Intentando cargar desde CSV local...")
                df = load_local_csv(ticker, start, end)
                if df.empty:
                    return pd.DataFrame()

    estrategias = mostrar_estrategias(config)
    estrategia = estrategias.get(strategy_name)
    if not estrategia:
        raise NotImplementedError(f"Estrategia no implementada: {strategy_name}")
    
    if len(df) < estrategia.config.get("total_data_needed", 0):
        print("⚠️ Datos insuficientes para esta estrategia. Se necesitan al menos", estrategia.config["total_data_needed"])
        return pd.DataFrame(columns=COLUMNAS)
    
    print(["STRATEGY_ENGINE: Estrategia aplicada correctamente"])
    return estrategia.aplicar(df)
