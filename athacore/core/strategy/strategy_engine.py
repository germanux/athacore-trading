# === IMPORTS Y UTILIDADES ===
import pandas as pd
import os
import re

#Importaciñon de estrategias de "strategy_list"
from athacore.core.strategy import strategy_list
from athacore.core.strategy.strategy_list import (
    EstrategiaBreakout, EstrategiaReversal, EstrategiaRango, EstrategiaDayTrading, EstrategiaNewsTrading, EstrategiaRSI, EstrategiaMACD, EstrategiaMediasSimples, EstrategiaMomentum, EstrategiaScalping, EstrategiaReversionMedia, EstrategiaTendencia, EstrategiaVolume, EstrategiaPriceAction, EstrategiaSwingTrading, EstrategiaPositionTrading, EstrategiaArbitrajeSimulado, EstrategiaPairTrading,
)
from athacore.core.strategy.strategy_base import (load_local_csv, COLUMNAS)

# Intenta importar desde Yahoo Finance; si falla, usa Alpha Vantage
try:
    from athacore.core.data.market_data_yhfinance import get_price_data
except ImportError:
    from athacore.core.data.market_data_alpha_vantage import get_price_data

#== Mostrar estrategias en el output ==
def camel_to_snake(name):
    # Convierte "MACDSignal" en "macd_signal", no "m_a_c_d_signal"
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
                print("📅 Rango de fechas tras carga y filtrado CSV:", df.index.min(), "→", df.index.max())
                if df.empty:
                    return pd.DataFrame()

    estrategias = mostrar_estrategias(config)
    estrategia = estrategias.get(strategy_name)
    if not estrategia:
        raise NotImplementedError(f"Estrategia no implementada: {strategy_name}. " f"Estrategias disponibles: {list(estrategias.keys())}")
    
    if len(df) < estrategia.config.get("total_data_needed", 0):
        print("⚠️ Datos insuficientes para esta estrategia. Se necesitan al menos", estrategia.config["total_data_needed"])
        return pd.DataFrame(columns=COLUMNAS)
    
    print(["STRATEGY_ENGINE: Estrategia aplicada correctamente"])
    return estrategia.aplicar(df)
