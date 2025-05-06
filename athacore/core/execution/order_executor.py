from ib_insync import IB, MarketOrder, Stock

ib = IB()


def execute_order(symbol: str, action: str, quantity: int, mode: str = "simulacion") -> str:
    """Ejecuta una orden simulada o real según el modo indicado."""
    if action not in ["BUY", "SELL"]:
        raise ValueError("Acción no válida. Usa 'BUY' o 'SELL'.")

    if mode == "simulacion":
        return simulate_order(symbol, action, quantity)
    elif mode == "real":
        return send_order_to_ibkr(symbol, action, quantity)
    else:
        raise ValueError(f"Modo de ejecución no reconocido: {mode}")


def simulate_order(symbol: str, action: str, quantity: int) -> str:
    return f"🧪 Simulación: {action} {quantity} de {symbol}"


def connect_ibkr(host='127.0.0.1', port=7497, client_id=1):
    """Conecta a TWS o IB Gateway."""
    try:
        ib.connect(host, port, clientId=client_id)
        return True
    except Exception as e:
        raise ConnectionError(f"❌ Error al conectar con IBKR: {e}")


def disconnect_ibkr():
    """Desconecta de IBKR."""
    if ib.isConnected():
        ib.disconnect()


def send_order_to_ibkr(symbol: str, action: str, quantity: int) -> str:
    """
    Envía una orden real a Interactive Brokers usando ib_insync.
    IMPORTANTE: requiere TWS o IB Gateway en ejecución.
    """
    try:
        if not ib.isConnected():
            connect_ibkr()

        contract = Stock(symbol, 'SMART', 'USD')
        order = MarketOrder(action, quantity)

        trade = ib.placeOrder(contract, order)
        ib.sleep(1)  # Esperar brevemente para registrar el estado inicial

        return f"🚀 Orden enviada: {action} {quantity} {symbol} — Estado: {trade.orderStatus.status}"
    except Exception as e:
        return f"❌ Error al ejecutar orden en IBKR: {e}"
    finally:
        disconnect_ibkr()