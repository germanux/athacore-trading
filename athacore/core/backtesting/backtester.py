import pandas as pd


def run_backtest(data: pd.DataFrame, signal_column, initial_cash: float = 10000.0) -> dict:
    """Ejecuta un backtest simple sobre datos con señales de compra/venta."""

    if signal_column not in data.columns:
        raise ValueError(f"Falta la columna '{signal_column}' en los datos.")

    cash = float(initial_cash) 
    actions_cuantity = 0
    trades = []

    #data["fecha"]=data["fecha"].astype(str)
    #data.to_dict(orient="records")

    #print("DATA", data)
    for i in range(1, len(data)):
        signal = data.iloc[i][signal_column]
        price = data.iloc[i]['cierre']

        #print(signal, price)
        """
        Se compra y vende todo
        - Se puede comprar menos de uno?
        - Máximo de cuanto comprar a la vez quizás?
        """
        # Comprar
        if signal and cash > 0:
            #print("Compra")
            actions_cuantity = cash / price
            cash = 0
            trades.append([i, 'BUY', price, cash, data.iloc[i]["fecha"]])
            
        # Vender
        elif not signal and actions_cuantity > 0:
            #print("Venta")
            cash = actions_cuantity * price
            actions_cuantity = 0
            trades.append([i, 'SELL', price, cash, data.iloc[i]["fecha"]])
            
    #print(type(data['cierre'].iloc[-1]), type(actions_cuantity), type(cash))

    final_cash = cash + actions_cuantity * data['cierre'].iloc[-1]
    profit = final_cash - float(initial_cash)

    trades_dicc =[{"indice": a, "compra": b, "price": c, "dinero": d, "fecha": e} for a, b, c, d, e in trades]
    trades_df = pd.DataFrame(trades, columns=["indice", "compra", "price", "dinero", "fecha"])

    #print(trades)

    #return [initial_cash, final_cash, profit, trades]

    estadisticas = {
        'Dinero inicial': initial_cash,
        'Dinero ganado': round(final_cash, 2),
        'Ganancias': round(profit, 2),
    }

    return estadisticas, trades_df