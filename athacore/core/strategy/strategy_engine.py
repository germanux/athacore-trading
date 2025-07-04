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
            if getattr(instancia, "operativa", True):
                estrategias[instancia.nombre_interno] = instancia
    return estrategias

def run_analysis(strategy_name: str, ticker: str, start: str, end: str, config=None) -> pd.DataFrame:
    listado_estrategias = mostrar_estrategias(config)
    estrategia = listado_estrategias.get(strategy_name)

    if not estrategia:
        raise NotImplementedError(
            f"Estrategia no implementada: {strategy_name}. "
            f"Estrategias disponibles: {list(listado_estrategias.keys())}"
        )

    bar_size = estrategia.config.get("candle_size", "15min")
    print(f"[DEBUG] Intervalo solicitado: {bar_size}")

    data_sources = [
        ("Yahoo Finance", get_price_data_yhfinance, {"config": config}),
        #("Finnhub", get_price_data_finnhub, {}),
        #("Alpha Vantage", get_price_data_alpha_vantage, {}),
        #("Twelve Data", get_price_data_twelve, {"bar_size": bar_size, "api_key": twelve_data_api_key})
        
    ]

    # Bucle para probar las distintas fuentes de datos
    for data_source, market_data_function, extra_kwargs in data_sources:
        try:
            kwargs = {"symbol": ticker, "start_date": start, "end_date": end, **extra_kwargs}
            result = market_data_function(**kwargs)
            if isinstance(result, tuple):
                df, metadata = result
            elif isinstance(result, pd.DataFrame):
                df, metadata = result, None
            else:
                print(f"[MARKET_DATA]: Valor de retorno inesperado: {type(result)}")
                df, metadata = None, None

            print(f"[MARKET_DATA]: Tipos de variable: df: {type(df)}, metadata: {type(metadata)}")
            if isinstance(df, pd.DataFrame) and not df.empty:
                print(f"[STRATEGY_ENGINE]: Datos tomados de {data_source}")
                break
        except Exception as e:
            print(f"[STRATEGY_ENGINE]: Error con {data_source}: {e}")

    # Si no hay datos, intentamos cargar desde CSV local
    if df is None or df.empty:
        df = load_local_csv(ticker, start, end)
        if df is not None and not df.empty:
            print(f"Rango de fechas tras carga y filtrado CSV: {df.index.min()} → {df.index.max()}")

    if len(df) < estrategia.config.get("total_data_needed", 0):
        print("⚠️ Datos insuficientes para esta estrategia. Se necesitan al menos",
              estrategia.config["total_data_needed"])
    
    if df is not None and not df.empty:
        print("✅ [STRATEGY_ENGINE]: Se descargaróon los datos correctamente")
        dicc_señales = estrategia.aplicar(df, metadata)
        señales = dicc_señales["señales"]

        if señales is None or señales.empty:
            print("⚠️[STRATEGY_ENGINE]: No se creo ninguna señal de compra o venta")
        print(f"Señales creadas: \n{señales}")
        return dicc_señales
    else:
        print("❌ [STRATEGY_ENGINE]: No se pudieron descargar los datos")
        return pd.DataFrame(columns=COLUMNAS)
