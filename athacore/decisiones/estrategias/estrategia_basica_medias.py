def estrategia_basica_medias(df):
    señales = []
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()

    for i in range(1, len(df)):
        if df['MA20'].iloc[i] > df['MA50'].iloc[i] and df['MA20'].iloc[i-1] <= df['MA50'].iloc[i-1]:
            señales.append((df.index[i], 'BUY'))
        elif df['MA20'].iloc[i] < df['MA50'].iloc[i] and df['MA20'].iloc[i-1] >= df['MA50'].iloc[i-1]:
            señales.append((df.index[i], 'SELL'))
    return señales
