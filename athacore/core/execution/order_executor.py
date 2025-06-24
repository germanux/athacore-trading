from ib_insync import IB, Stock, MarketOrder
import asyncio

ib = IB()

async def connect_ib():
    if not ib.isConnected():
        print("🔌 Intentando conectar con IB Gateway...")
        await ib.connectAsync('127.0.0.1', 4002, clientId=1)
        print("✅ Conectado a IB Gateway")

async def execute_order(symbol: str, action: str, quantity: int, mode: str = "real") -> str:
    try:
        await connect_ib()

        contract = Stock(symbol, 'SMART', 'USD')

        if action.upper() == "BUY":
            order = MarketOrder('BUY', quantity)
            print(f"📈 Ejecutando orden de COMPRA para {symbol}")
        elif action.upper() == "SELL":
            order = MarketOrder('SELL', quantity)
            print(f"📉 Ejecutando orden de VENTA para {symbol}")
        else:
            return f"❌ Acción inválida: {action}"

        # Usa .placeOrder dentro del hilo principal de asyncio
        trade = ib.placeOrder(contract, order)

        # Espera sin bloquear el loop principal
        while not trade.isDone():
            await asyncio.sleep(1)

        estado = trade.orderStatus.status
        print(f"✅ Orden completada: {estado}")
        return f"✅ Orden ejecutada en IBKR: {action} {quantity} {symbol} — Estado: {estado}"

    except Exception as e:
        return f"❌ Error al ejecutar orden: {e}"
