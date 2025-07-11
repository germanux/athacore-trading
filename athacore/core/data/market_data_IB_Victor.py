from ib_insync import *
import pandas as pd
from datetime import datetime

async def get_price_data(
    symbol: str,
    exchange: str = 'SMART',
    currency: str = 'USD',
    end_datetime: str = '',
    duration_str: str = '1 M',
    bar_size: str = '1 day',
    what_to_show: str = 'TRADES',
    use_rth: bool = True,
    host: str = '127.0.0.1',
    port: int = 7497,
    client_id: int = 1
) -> pd.DataFrame:
    """
    Obtiene datos históricos desde Interactive Brokers usando ib_insync.
    """
    ib = IB()
    try:
        await ib.connectAsync(host, port, clientId=client_id)

        contract = Stock(symbol, exchange, currency)

        bars = await ib.reqHistoricalDataAsync(
            contract,
            endDateTime=end_datetime,
            durationStr=duration_str,
            barSizeSetting=bar_size,
            whatToShow=what_to_show,
            useRTH=use_rth,
            formatDate=1
        )

        if not bars:
            print(f"[IB DATA]: No se obtuvieron datos para {symbol}")
            return pd.DataFrame()

        df = util.df(bars)
        df.set_index('date', inplace=True)
        metadata = {
        "market_data":{
            "source": "Alphavantage",
            "symbol": symbol,
            #"name": company_name,
            #"exchange": info.get('exchange', 'N/A'),
            #"currency": info.get('currency', 'USD'),
            #"secType": info.get('quoteType', 'stock'),
            "df_info": df.info()
        }}
        print (df)
        return df, metadata

    finally:
        ib.disconnect()