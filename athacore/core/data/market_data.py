# athacore/core/data/market_data.py
# market_data.py
import pandas as pd
from ib_insync import IB, Stock
from typing import Literal

class IBClient:
    _instance = None

    def __new__(cls, host='127.0.0.1', port=7497, client_id=1):
        if cls._instance is None:
            cls._instance = super(IBClient, cls).__new__(cls)
            cls._instance._ib = IB()
            cls._instance._host = host
            cls._instance._port = port
            cls._instance._client_id = client_id
            cls._instance._connected = False
        return cls._instance

    async def connect(self):
        if not self._connected:
            try:
                await self._ib.connectAsync(self._host, self._port, clientId=self._client_id, timeout=5)
                self._connected = True
                print("✅ Conexión exitosa a Interactive Brokers")
            except Exception as e:
                print(f"❌ Error al conectar con IB: {type(e).__name__} - {e}")
                self._connected = False
        return self._ib

    async def disconnect(self):
        if self._connected:
            await self._ib.disconnectAsync()
            self._connected = False
            print("🔌 Desconectado de Interactive Brokers")

    def get_ib(self):
        return self._ib

# Crear instancia única de conexión
client = IBClient()
ib = client.get_ib()

async def get_price_data(symbol: str, duration: str = '1 D', bar_size: str = '5 mins', source: Literal['ib'] = 'ib') -> dict:
    """
    Obtiene datos históricos de IB y datos generales de la acción.
    :param symbol: Símbolo del activo (ej. 'AAPL').
    :param duration: Duración de los datos históricos.
    :param bar_size: Tamaño de la barra.
    :param source: Fuente de datos (solo 'ib' por ahora).
    :return: Diccionario con datos históricos y detalles del activo.
    """
    if source != 'ib':
        raise ValueError("Solo se admite 'ib' como fuente de datos en esta versión.")

    return await _get_ib_data(symbol, duration, bar_size)

async def _get_ib_data(symbol: str, duration: str = '1 D', bar_size: str = '5 mins') -> dict:
    if not ib.isConnected():
        await client.connect()

    contract = Stock(symbol, 'NASDAQ', 'USD')
    details = await ib.reqContractDetailsAsync(contract)
    if not details:
        raise ValueError(f"Contrato inválido o no disponible para: {symbol}")
    
    # Accediendo a los atributos correctos de ContractDetails
    contract_details = details[0].contract  # Accedemos directamente al contrato
    company_name = details[0].longName or symbol

    bars = await ib.reqHistoricalDataAsync(
        contract,
        endDateTime='',
        durationStr=duration,
        barSizeSetting=bar_size,
        whatToShow='TRADES',
        useRTH=False,
        formatDate=1
    )

    if not bars:
        raise ValueError(f"No se obtuvieron datos históricos para {symbol}")

    df = pd.DataFrame([bar.__dict__ for bar in bars])

    # Convertir la columna 'date' a formato string para evitar problemas con JSON serializable
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')

    return {
        "data": df[['date', 'open', 'high', 'low', 'close', 'volume']],
        "info": {
            "symbol": contract_details.symbol,
            "name": company_name,
            "exchange": contract_details.exchange,
            "currency": contract_details.currency,
            "secType": contract_details.secType,
        }
    }







