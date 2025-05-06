import pandas as pd


def run_backtest(data: pd.DataFrame, signal_column: str = 'position', initial_cash: float = 10000.0) -> dict:
    """Ejecuta un backtest simple sobre datos con señales de compra/venta."""

    if signal_column not in data.columns:
        raise ValueError(f"Falta la columna '{signal_column}' en los datos.")

    cash = initial_cash
    position = 0
    trades = []

    for i in range(1, len(data)):
        signal = data.iloc[i][signal_column]
        price = data.iloc[i]['Close']

        if signal == 1 and cash > 0:  # Comprar
            position = cash / price
            cash = 0
            trades.append(('BUY', price, data.index[i]))

        elif signal == -1 and position > 0:  # Vender
            cash = position * price
            position = 0
            trades.append(('SELL', price, data.index[i]))

    final_value = cash + position * data['Close'].iloc[-1]
    profit = final_value - initial_cash

    return {
        'initial_cash': initial_cash,
        'final_value': round(final_value, 2),
        'profit': round(profit, 2),
        'trades': trades
    }
