import pandas as pd
import os
import re

from dotenv import load_dotenv
load_dotenv()

from athacore.core.strategy import strategy_list
from athacore.core.strategy.strategy_list import (
    EstrategiaBreakout, EstrategiaReversal, EstrategiaRango, EstrategiaDayTrading,
    EstrategiaNewsTrading, EstrategiaRSI, EstrategiaMACD, EstrategiaMediasSimples,
    EstrategiaMomentum, EstrategiaScalping, EstrategiaReversionMedia, EstrategiaTendencia,
    EstrategiaVolume, EstrategiaPriceAction, EstrategiaSwingTrading, EstrategiaPositionTrading,
    EstrategiaArbitrajeSimulado, EstrategiaPairTrading
)
from athacore.core.strategy.strategy_base import (load_local_csv, COLUMNAS)

from athacore.core.data.market_data_yhfinance import get_price_data as get_price_data_yhfinance
from athacore.core.data.market_data_alpha_vantage import get_price_data as get_price_data_alpha_vantage
from athacore.core.data.market_data_finnhub import get_price_data as get_price_data_finnhub
from athacore.core.data.market_data_twelvedata import get_price_data as get_price_data_twelve

# Reemplaza con tu propia API Key de Twelve Data
twelve_data_api_key = os.getenv("TWELVE_DATA_API_KEY", "TU_API_KEY_AQUI")

def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()

def mostrar_estrategias(config=None):
    estrategias = {}
    for nombre in dir(strategy_list):
        clase = getattr(strategy_list, nombre)
        if isinstance(clase, type) and nombre.startswith("Estrategia") and nombre != "EstrategiaBase":
            instancia = clase(config)
            estrategias[instancia.nombre_interno] = instancia
    return estrategias

def run_analysis(strategy_name: str, ticker: str, start: str, end: str, config=None) -> pd.DataFrame:
    estrategias = mostrar_estrategias(config)
    estrategia = estrategias.get(strategy_name)

    if not estrategia:
        raise NotImplementedError(
            f"Estrategia no implementada: {strategy_name}. "
            f"Estrategias disponibles: {list(estrategias.keys())}"
        )

    bar_size = estrategia.config.get("candle_size", "15min")
    print(f"[DEBUG] Intervalo solicitado: {bar_size}")

    try:
        df = get_price_data_twelve(ticker, start_date=start, end_date=end, bar_size=bar_size, api_key=twelve_data_api_key)
        if df.empty:
            raise ValueError("Twelve Data no devolvió datos.")
        print("[STRATEGY_ENGINE]: Datos tomados de Twelve Data")
    except Exception as e:
        print(f"[STRATEGY_ENGINE]: Error con Twelve Data: {e}")
        try:
            df = get_price_data_yhfinance(ticker, start_date=start, end_date=end, bar_size=bar_size)
            if df.empty:
                raise ValueError("Yahoo Finance falló o no devolvió datos.")
            print("[STRATEGY_ENGINE]: Datos tomados de YahooFinance")
        except Exception as e:
            print(f"[STRATEGY_ENGINE]: Error con Yahoo Finance: {e}")
            try:
                df = get_price_data_alpha_vantage(ticker, start_date=start, end_date=end)
                if df.empty:
                    raise ValueError("Alpha Vantage también falló.")
                print("[STRATEGY_ENGINE]: Datos tomados de Alpha Vantage")
            except Exception as e:
                print(f"[STRATEGY_ENGINE]: Error con Alpha Vantage: {e}")
                try:
                    df = get_price_data_finnhub(ticker, start_date=start, end_date=end)
                    if df.empty:
                        raise ValueError("Finnhub también falló.")
                    print("[STRATEGY_ENGINE]: Datos tomados de Finnhub")
                except Exception as final_e:
                    print(f"[STRATEGY_ENGINE]: Todas las fuentes fallaron: {final_e}")
                    print("🔁 Intentando cargar desde CSV local...")
                    df = load_local_csv(ticker, start, end)
                    print("📅 Rango de fechas tras carga y filtrado CSV:", df.index.min(), "→", df.index.max())
                    if df.empty:
                        return pd.DataFrame()

    if len(df) < estrategia.config.get("total_data_needed", 0):
        print("⚠️ Datos insuficientes para esta estrategia. Se necesitan al menos",
              estrategia.config["total_data_needed"])
        return pd.DataFrame(columns=COLUMNAS)

    print("✅ [STRATEGY_ENGINE]: Estrategia aplicada correctamente")
    return estrategia.aplicar(df)
