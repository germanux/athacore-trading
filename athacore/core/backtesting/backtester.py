import pandas as pd


def run_backtest(data: pd.DataFrame, signal_column, initial_cash: float = 10000.0) -> dict:
    """Ejecuta un backtest simple sobre datos con señales de compra/venta."""

    if signal_column not in data.columns:
        raise ValueError(f"Falta la columna '{signal_column}' en los datos.")

    cash = float(initial_cash) 
    actions_cuantity = 0
    trades = []

    for i in range(1, len(data)):
        signal = data.iloc[i][signal_column]
        price = data.iloc[i]['cierre']

        # Comprar
        if signal and cash > 0:
            actions_cuantity = cash / price
            cash = 0
            trades.append([i, 'BUY', price, cash, data.iloc[i]["fecha"]])
            
        # Vender
        elif not signal and actions_cuantity > 0:
            cash = actions_cuantity * price
            actions_cuantity = 0
            trades.append([i, 'SELL', price, cash, data.iloc[i]["fecha"]])
            
    final_cash = cash + actions_cuantity * data['cierre'].iloc[-1]
    profit = final_cash - float(initial_cash)
    profit_percent = (profit/float(initial_cash))*100

    estadisticas = {
        'Dinero inicial': initial_cash,
        'Dinero ganado': round(final_cash, 2),
        'Resultado final': round(profit, 2),
        'Porcentaje rentabilidad': round(profit_percent, 2)
    }
    trades_df = pd.DataFrame(trades, columns=["indice", "compra", "price", "dinero", "fecha"])

    return estadisticas, trades_df