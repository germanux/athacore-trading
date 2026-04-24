from ib_insync import IB, Stock, MarketOrder

ib = IB()

def connect_ib():
    if not ib.isConnected():
        ib.connect('127.0.0.1', 4002, clientId=1234)

async def execute_order(symbol: str, action: str, quantity: int, mode: str = "real", cancelar_previas: bool = True) -> str:
    try:
        connect_ib()

        contract = Stock(symbol, 'SMART', 'USD')

        if action.upper() not in ['BUY', 'SELL']:
            return f"❌ Acción inválida: {action}"

        order = MarketOrder(action.upper(), quantity)
        print(f"{'📈' if action.upper() == 'BUY' else '📉'} Ejecutando orden de {action.upper()} para {symbol}")

        if cancelar_previas:
            open_trades = ib.trades()
            canceladas = 0
            for trade in open_trades:
                if trade.contract.symbol == symbol and not trade.isDone():
                    ib.cancelOrder(trade.order)
                    canceladas += 1
            if canceladas:
                print(f"🔄 {canceladas} órdenes previas canceladas para {symbol}")

        trade = ib.placeOrder(contract, order)

        while not trade.isDone():
            ib.sleep(1)

        estado = trade.orderStatus.status
        print(f"✅ Orden completada: {estado}")

        return f"✅ Orden ejecutada en IBKR: {action} {quantity} {symbol} — Estado: {estado}"

    except Exception as e:
        return f"❌ Error al ejecutar orden: {e}"
