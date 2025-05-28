# athacore/core/trading/order_executor.py

import pandas as pd
from ib_insync import IB, Stock, MarketOrder
from typing import Optional


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


# Instancia única
client = IBClient()
ib = client.get_ib()


async def execute_order(symbol: str, action: str, quantity: int, mode: str = "simulacion") -> str:
    """Ejecuta una orden simulada o real según el modo indicado."""
    if action not in ["BUY", "SELL"]:
        raise ValueError("Acción no válida. Usa 'BUY' o 'SELL'.")

    if mode == "simulacion":
        return simulate_order(symbol, action, quantity)
    elif mode == "real":
        return await send_order_to_ibkr(symbol, action, quantity)
    else:
        raise ValueError(f"Modo de ejecución no reconocido: {mode}")


def simulate_order(symbol: str, action: str, quantity: int) -> str:
    return f"🧪 Simulación: {action} {quantity} de {symbol}"


async def send_order_to_ibkr(symbol: str, action: str, quantity: int) -> str:
    """
    Envía una orden real a Interactive Brokers usando ib_insync.
    IMPORTANTE: requiere TWS o IB Gateway en ejecución.
    """
    try:
        if not ib.isConnected():
            await client.connect()

        contract = Stock(symbol, 'SMART', 'USD')
        order = MarketOrder(action, quantity)

        trade = ib.placeOrder(contract, order)
        ib.sleep(1)  # Esperar brevemente para actualizar el estado

        return f"🚀 Orden enviada: {action} {quantity} {symbol} — Estado: {trade.orderStatus.status}"
    except Exception as e:
        return f"❌ Error al ejecutar orden en IBKR: {e}"
    finally:
        await client.disconnect()
