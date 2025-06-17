#=== Imports y Utilidades ===
import pandas as pd
import os
import matplotlib.pyplot as plt

from athacore.core.strategy.strategy_base import (EstrategiaBase, generar_senal, sma, rsi, macd, COLUMNAS)
#ESTRATEGIA BREAKOUT: compra si el precio supera la resistencia reciente
class EstrategiaBreakout(EstrategiaBase):
    nombre_interno = "estrategia_breakout"

    def aplicar(self, df):
        #Parámetros con valores por defecto
        ventana_breakout = self.config.get("ventana_breakout", 20)
        take_profit = self.config.get("take_profit", 0.03)
        stop_loss = self.config.get("stop_loss", 0.01)
        volumen_window = self.config.get("volumen_window", 20)
        duracion_maxima = self.config.get("duracion_maxima", 48)

        #Cálculo de indicadores
        df['max_n'] = df['Close'].rolling(window=ventana_breakout).max()
        df['min_n'] = df['Close'].rolling(window=ventana_breakout).min()
        df['SMA_200'] = sma(df, 200)
        df['Volumen_Medio'] = df['Volume'].rolling(window=volumen_window).mean()
        df = df.dropna(subset=['max_n', 'min_n', 'SMA_200', 'Volumen_Medio'])

        señales = []
        posicion_abierta = None
        precio_entrada = None
        entrada_index = None

        for i in range(200, len(df)):
            close = df['Close'].iloc[i]
            max_prev = df['max_n'].iloc[i - 1]
            min_prev = df['min_n'].iloc[i - 1]
            sma200 = df['SMA_200'].iloc[i]
            volumen = df['Volume'].iloc[i]
            volumen_medio = df['Volumen_Medio'].iloc[i]

            #Salida por TP/SL o duración máxima
            if posicion_abierta == "compra":
                if close >= precio_entrada * (1 + take_profit) or close <= precio_entrada * (1 - stop_loss) or i - entrada_index >= duracion_maxima:
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = None
                    precio_entrada = None
                    entrada_index = None
                    continue

            elif posicion_abierta == "venta":
                if close <= precio_entrada * (1 - take_profit) or close >= precio_entrada * (1 + stop_loss) or i - entrada_index >= duracion_maxima:
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = None
                    precio_entrada = None
                    entrada_index = None
                    continue

            #Entrada en compra si supera el máximo reciente y está por encima de la media
            if (
                close > max_prev and
                close > sma200 and
                volumen > volumen_medio and
                posicion_abierta != "compra"
            ):
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"
                precio_entrada = close
                entrada_index = i

            #Entrada en venta si cae por debajo del mínimo reciente y debajo de la media
            elif (
                close < min_prev and
                close < sma200 and
                volumen > volumen_medio and
                posicion_abierta != "venta"
            ):
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"
                precio_entrada = close
                entrada_index = i

        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA REVERSAL: compra si hay reversión tras caída
class EstrategiaReversal(EstrategiaBase):
    nombre_interno = "estrategia_reversal"

    def aplicar(self, df):
        df['RSI'] = rsi(df, window=self.config.get("lookback_period", 14))
        df['SMA_200'] = sma(df, 200)
        df = df.dropna(subset=['RSI', 'SMA_200'])

        señales = []
        posicion_abierta = None
        precio_entrada = None

        take_profit = self.config.get("take_profit", 0.015)
        stop_loss = self.config.get("stop_loss", 0.005)

        for i in range(2, len(df)):
            close = df['Close'].iloc[i]
            open_ = df['Open'].iloc[i]
            close_prev = df['Close'].iloc[i - 1]
            open_prev = df['Open'].iloc[i - 1]
            rsi_val = df['RSI'].iloc[i]
            sma200 = df['SMA_200'].iloc[i]

            #Cierre por TP o SL
            if posicion_abierta == "compra":
                if close >= precio_entrada * (1 + take_profit) or close <= precio_entrada * (1 - stop_loss):
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            elif posicion_abierta == "venta":
                if close <= precio_entrada * (1 - take_profit) or close >= precio_entrada * (1 + stop_loss):
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            #ENTRADA COMPRA 
            cuerpo_anterior = abs(close_prev - open_prev)
            cuerpo_actual = abs(close - open_)
            if (
                rsi_val < 30 and
                close > open_ and
                open_prev > close_prev and
                cuerpo_actual > cuerpo_anterior and
                close > sma200 and  #<- Solo si tendencia general es alcista
                posicion_abierta != "compra"
            ):
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"
                precio_entrada = close

            #ENTRADA VENTA 
            elif (
                rsi_val > 70 and
                close < open_ and
                open_prev < close_prev and
                cuerpo_actual > cuerpo_anterior and
                close < sma200 and  #<- Solo si tendencia general es bajista
                posicion_abierta != "venta"
            ):
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"
                precio_entrada = close

        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA RANGE TRADING
class EstrategiaRango(EstrategiaBase):
    nombre_interno = "estrategia_rango"

    def aplicar(self, df):
        df['min_10'] = df['Close'].rolling(window=10).min()
        df['max_10'] = df['Close'].rolling(window=10).max()
        df['SMA_200'] = sma(df, 200)
        df = df.dropna(subset=['min_10', 'max_10', 'SMA_200'])

        señales = []
        posicion_abierta = None
        precio_entrada = None

        take_profit = self.config.get("take_profit", 0.01)
        stop_loss = self.config.get("stop_loss", 0.005)

        for i in range(10, len(df)):
            close = df['Close'].iloc[i]
            sma200 = df['SMA_200'].iloc[i]

            if posicion_abierta == "compra":
                if close >= precio_entrada * (1 + take_profit) or close <= precio_entrada * (1 - stop_loss):
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            elif posicion_abierta == "venta":
                if close <= precio_entrada * (1 - take_profit) or close >= precio_entrada * (1 + stop_loss):
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            if df['Close'].iloc[i] <= df['min_10'].iloc[i] and close > sma200 and posicion_abierta != "compra":
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"
                precio_entrada = close
            elif df['Close'].iloc[i] >= df['max_10'].iloc[i] and close < sma200 and posicion_abierta != "venta":
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"
                precio_entrada = close

        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA DAY TRADING: entradas rápidas, busca variaciones intradía
class EstrategiaDayTrading(EstrategiaBase):
    nombre_interno = "estrategia_day_trading"

    def aplicar(self, df):
        lookback = self.config.get("lookback_period", 4)
        if lookback < 3:
            print(f"⚠️ [DayTrading] El parámetro 'lookback_period' ({lookback}) es muy bajo. Usando valor mínimo recomendado: 3.")
            lookback = 3
            self.config["lookback_period"] = 3

        sma_largo = lookback * 4
        volumen_window = 20
        total_minimo = sma_largo + volumen_window

        if len(df) < total_minimo:
            print(f"❌ [DayTrading] Datos insuficientes: se requieren al menos {total_minimo} filas. Actualmente hay: {len(df)}")
            return pd.DataFrame(columns=COLUMNAS)

        df['SMA_corta'] = sma(df, lookback)
        df['SMA_larga'] = sma(df, sma_largo)
        df['Volumen_Medio'] = df['Volume'].rolling(window=volumen_window).mean()
        df['Hora'] = df.index.strftime('%H:%M')
        df = df.dropna(subset=['SMA_corta', 'SMA_larga', 'Volumen_Medio'])

        take_profit = self.config.get("take_profit", 0.02)
        stop_loss = self.config.get("stop_loss", 0.005)
        hora_inicio = self.config.get("hora_inicio", "09:30")
        hora_fin = self.config.get("hora_fin", "16:00")

        señales = []
        posicion_abierta = None
        precio_entrada = None
        entrada_index = None

        for i in range(sma_largo, len(df)):
            hora_actual = df['Hora'].iloc[i]
            close = df['Close'].iloc[i]

            #Salida por TP/SL o duración máxima
            if posicion_abierta == "compra":
                if (close >= precio_entrada * (1 + take_profit) or
                    close <= precio_entrada * (1 - stop_loss) or
                    i - entrada_index >= 36):
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = None
                    precio_entrada = None
                    entrada_index = None
                    continue

            elif posicion_abierta == "venta":
                if (close <= precio_entrada * (1 - take_profit) or
                    close >= precio_entrada * (1 + stop_loss) or
                    i - entrada_index >= 36):
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = None
                    precio_entrada = None
                    entrada_index = None
                    continue

            if not (hora_inicio <= hora_actual <= hora_fin):
                continue

            sma_corta = df['SMA_corta'].iloc[i]
            sma_larga = df['SMA_larga'].iloc[i]
            volumen = df['Volume'].iloc[i]
            volumen_medio = df['Volumen_Medio'].iloc[i]

            if (sma_corta > sma_larga * 0.99 and
                close > sma_corta * 0.99 and
                volumen > volumen_medio * 0.9 and
                posicion_abierta != "compra"):
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"
                precio_entrada = close
                entrada_index = i

            elif (close < sma_corta * 0.995 and
                  posicion_abierta != "venta"):
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"
                precio_entrada = close
                entrada_index = i

        if not señales:
            print("🔎 [DayTrading] No se generaron señales en el período evaluado.")

        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA NEWS TRADING (SIMULADA): reacción a velas con gran volumen y rango
class EstrategiaNewsTrading(EstrategiaBase):
    nombre_interno = "estrategia_news_trading"

    def aplicar(self, df):
        df['rango'] = df['Close'].pct_change().abs()
        df['volumen_relativo'] = df['Volume'] / df['Volume'].rolling(20).mean()
        df['SMA_10'] = sma(df, 10)
        df = df.dropna(subset=['rango', 'volumen_relativo', 'SMA_10'])

        señales = []
        posicion_abierta = None
        precio_entrada = None

        take_profit = self.config.get("take_profit", 0.01)
        stop_loss = self.config.get("stop_loss", 0.005)

        for i in range(20, len(df)):
            close = df['Close'].iloc[i]
            sma10 = df['SMA_10'].iloc[i]
            rango = df['rango'].iloc[i]
            vol_rel = df['volumen_relativo'].iloc[i]

            #Cierre por TP o SL
            if posicion_abierta == "compra":
                if close >= precio_entrada * (1 + take_profit) or close <= precio_entrada * (1 - stop_loss):
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            elif posicion_abierta == "venta":
                if close <= precio_entrada * (1 - take_profit) or close >= precio_entrada * (1 + stop_loss):
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            #Entrada (compra): evento + fuerza + tendencia alcista
            if rango > 0.03 and vol_rel > 2 and close > sma10 and posicion_abierta != "compra":
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"
                precio_entrada = close

            #Entrada (venta): calma + debilidad + tendencia bajista
            elif rango < 0.01 and vol_rel < 1 and close < sma10 and posicion_abierta != "venta":
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"
                precio_entrada = close

        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA RSI SIMPLE: puntos de sobrecompra y sobreventa.
class EstrategiaRSI(EstrategiaBase):
    nombre_interno = "estrategia_rsi_simple"

    def aplicar(self, df):
        df['RSI'] = rsi(df, window=self.config.get("lookback_period", 14))
        df['SMA_200'] = sma(df, 200)
        df['Volumen_Medio'] = df['Volume'].rolling(window=20).mean()
        df = df.dropna(subset=['RSI', 'SMA_200', 'Volumen_Medio'])

        señales = []
        posicion_abierta = None
        precio_entrada = None

        take_profit = self.config.get("take_profit", 0.015)
        stop_loss = self.config.get("stop_loss", 0.005)

        for i in range(1, len(df)):
            close = df['Close'].iloc[i]
            rsi_val = df['RSI'].iloc[i]
            sma200 = df['SMA_200'].iloc[i]
            volumen = df['Volume'].iloc[i]
            volumen_medio = df['Volumen_Medio'].iloc[i]

            #Cierre por TP o SL
            if posicion_abierta == "compra":
                if close >= precio_entrada * (1 + take_profit) or close <= precio_entrada * (1 - stop_loss):
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            elif posicion_abierta == "venta":
                if close <= precio_entrada * (1 - take_profit) or close >= precio_entrada * (1 + stop_loss):
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            #Compra solo si RSI < 25, volumen alto y tendencia positiva
            if (
                rsi_val < 25 and close > sma200 and volumen > volumen_medio
                and posicion_abierta != "compra"
            ):
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"
                precio_entrada = close

            #Venta solo si RSI > 75, volumen alto y tendencia negativa
            elif (
                rsi_val > 75 and close < sma200 and volumen > volumen_medio
                and posicion_abierta != "venta"
            ):
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"
                precio_entrada = close

        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA MACD: cruce de líneas MACD y señal.
class EstrategiaMACD(EstrategiaBase):
    nombre_interno = "estrategia_macd_cruce"
    def aplicar(self, df):
        macd_df = macd(df)
        df['macd_line'] = macd_df['macd_line']
        df['signal_line'] = macd_df['signal_line']
        señales = []
        for i in range(1, len(df)):
            if df['macd_line'].iloc[i] > df['signal_line'].iloc[i] and df['macd_line'].iloc[i - 1] <= df['signal_line'].iloc[i - 1]:
                señales.append(generar_senal(df, i, True))
            elif df['macd_line'].iloc[i] < df['signal_line'].iloc[i] and df['macd_line'].iloc[i - 1] >= df['signal_line'].iloc[i - 1]:
                señales.append(generar_senal(df, i, False))
        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA BÁSICA DE MEDIAS: cruce de medias móviles simples.
class EstrategiaMediasSimples(EstrategiaBase):
    nombre_interno = "estrategia_basica_medias"

    def aplicar(self, df):
        df['SMA_short'] = sma(df, 5)
        df['SMA_long'] = sma(df, 20)
        df['Volumen_Prom'] = df['Volume'].rolling(10).mean()
        df = df.dropna(subset=['SMA_short', 'SMA_long', 'Volumen_Prom'])

        señales = []
        posicion_abierta = None
        precio_entrada = None

        take_profit = self.config.get("take_profit", 0.02)
        stop_loss = self.config.get("stop_loss", 0.01)

        for i in range(1, len(df)):
            sma_short = df['SMA_short'].iloc[i]
            sma_long = df['SMA_long'].iloc[i]
            sma_short_prev = df['SMA_short'].iloc[i - 1]
            sma_long_prev = df['SMA_long'].iloc[i - 1]
            close = df['Close'].iloc[i]
            volumen_actual = df['Volume'].iloc[i]
            volumen_prom = df['Volumen_Prom'].iloc[i]

            #Filtro de volumen
            if volumen_actual < volumen_prom:
                continue

            #Filtro de pendiente de SMA larga (tendencia)
            if sma_long < df['SMA_long'].iloc[i - 5]:
                continue

            #Cierre por TP / SL
            if posicion_abierta == "compra":
                if close >= precio_entrada * (1 + take_profit) or close <= precio_entrada * (1 - stop_loss):
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            elif posicion_abierta == "venta":
                if close <= precio_entrada * (1 - take_profit) or close >= precio_entrada * (1 + stop_loss):
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            #Entrada por cruce
            cruzó_al_alza = sma_short > sma_long and sma_short_prev <= sma_long_prev
            cruzó_a_la_baja = sma_short < sma_long and sma_short_prev >= sma_long_prev

            if cruzó_al_alza and posicion_abierta != "compra":
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"
                precio_entrada = close

            elif cruzó_a_la_baja and posicion_abierta != "venta":
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"
                precio_entrada = close

        return pd.DataFrame(señales, columns=COLUMNAS)

#MOMENTUM: fuerza de precio y volumen como señales de entrada y salida.
class EstrategiaMomentum(EstrategiaBase):
    nombre_interno = "estrategia_momentum"

    def aplicar(self, df):
        df['SMA_20'] = sma(df, 20)
        df['SMA_50'] = sma(df, 50)
        df['SMA_200'] = sma(df, 200)
        df['RSI'] = rsi(df, window=self.config.get("lookback_period", 14))
        df['Volumen_Medio'] = df['Volume'].rolling(window=20).mean()

        df = df.dropna(subset=['SMA_20', 'SMA_50', 'SMA_200', 'RSI', 'Volumen_Medio'])

        señales = []
        posicion_abierta = None
        precio_entrada = None

        take_profit = self.config.get("take_profit", 0.01)
        stop_loss = self.config.get("stop_loss", 0.005)

        for i in range(1, len(df)):
            close = df['Close'].iloc[i]
            sma20 = df['SMA_20'].iloc[i]
            sma50 = df['SMA_50'].iloc[i]
            sma200 = df['SMA_200'].iloc[i]
            rsi_val = df['RSI'].iloc[i]
            volumen = df['Volume'].iloc[i]
            volumen_medio = df['Volumen_Medio'].iloc[i]

            if posicion_abierta == "compra":
                if close >= precio_entrada * (1 + take_profit) or close <= precio_entrada * (1 - stop_loss):
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            elif posicion_abierta == "venta":
                if close <= precio_entrada * (1 - take_profit) or close >= precio_entrada * (1 + stop_loss):
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = None
                    precio_entrada = None
                    continue
            if (
                close > sma20 and close > sma50 and sma50 > sma200 and rsi_val > 55 and volumen > volumen_medio
                and posicion_abierta != "compra"
            ):
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"
                precio_entrada = close

            elif (
                close < sma20 and close < sma50 and sma50 < sma200 and rsi_val < 45
                and posicion_abierta != "venta"
            ):
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"
                precio_entrada = close

        return pd.DataFrame(señales, columns=COLUMNAS)

#SCALPING: entradas y salidas rápidas basadas en cruce de media muy corta.
class EstrategiaScalping(EstrategiaBase):
    nombre_interno = "estrategia_scalping"

    def aplicar(self, df):
        df['SMA_5'] = sma(df, 5)
        df['RSI'] = rsi(df, window=self.config.get("lookback_period", 14))
        df['Volumen_Medio'] = df['Volume'].rolling(window=20).mean()
        df = df.dropna(subset=['SMA_5', 'RSI', 'Volumen_Medio'])

        señales = []
        posicion_abierta = None
        precio_entrada = None

        #Parámetros de TP/SL como porcentaje
        take_profit = self.config.get("take_profit", 0.01)  
        stop_loss = self.config.get("stop_loss", 0.005)      

        for i in range(1, len(df)):
            close = df['Close'].iloc[i]
            close_prev = df['Close'].iloc[i - 1]
            sma5 = df['SMA_5'].iloc[i]
            sma5_prev = df['SMA_5'].iloc[i - 1]
            rsi_val = df['RSI'].iloc[i]
            volumen = df['Volume'].iloc[i]
            volumen_medio = df['Volumen_Medio'].iloc[i]

            #Control de cierre por TP o SL
            if posicion_abierta == "compra":
                if close >= precio_entrada * (1 + take_profit) or close <= precio_entrada * (1 - stop_loss):
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            elif posicion_abierta == "venta":
                if close <= precio_entrada * (1 - take_profit) or close >= precio_entrada * (1 + stop_loss):
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            #Señal de entrada (compra)
            if (close > sma5 and close_prev <= sma5_prev and rsi_val < 30 and
                    volumen > volumen_medio and posicion_abierta != "compra"):
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"
                precio_entrada = close

            #Señal de entrada (venta)
            elif (close < sma5 and close_prev >= sma5_prev and rsi_val > 70 and
                    volumen > volumen_medio and posicion_abierta != "venta"):
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"
                precio_entrada = close

        return pd.DataFrame(señales, columns=COLUMNAS)

#MEAN REVERSION: se basa en que el precio vuelve a su media tras alejarse.
class EstrategiaReversionMedia(EstrategiaBase):
    nombre_interno = "estrategia_reversion_media"

    def aplicar(self, df):
        df['SMA_20'] = sma(df, 20)
        df['RSI'] = rsi(df, window=self.config.get("lookback_period", 14))
        df = df.dropna(subset=['SMA_20', 'RSI'])

        señales = []
        posicion_abierta = None
        precio_entrada = None

        #Configuración
        take_profit = self.config.get("take_profit", 0.01)
        stop_loss = self.config.get("stop_loss", 0.005)  

        for i in range(1, len(df)):
            close = df['Close'].iloc[i]
            sma = df['SMA_20'].iloc[i]
            rsi_val = df['RSI'].iloc[i]

            #Cierre de posición por TP o SL
            if posicion_abierta == "compra":
                if close >= precio_entrada * (1 + take_profit) or close <= precio_entrada * (1 - stop_loss):
                    señales.append(generar_senal(df, i, False))  #<- Vender para cerrar compra
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            elif posicion_abierta == "venta":
                if close <= precio_entrada * (1 - take_profit) or close >= precio_entrada * (1 + stop_loss):
                    señales.append(generar_senal(df, i, True))  #<- Comprar para cerrar venta
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            #Señales de entrada 
            #COMPRA: muy por debajo de la media y en sobreventa
            if (close < sma * 0.97 and rsi_val < 30 and posicion_abierta != "compra"):
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"
                precio_entrada = close

            #VENTA: muy por encima de la media y en sobrecompra
            elif (close > sma * 1.03 and rsi_val > 70 and posicion_abierta != "venta"):
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"
                precio_entrada = close

        return pd.DataFrame(señales, columns=COLUMNAS)

#TREND FOLLOWING: detecta tendencias sostenidas basadas en medias de 50 y 200.
class EstrategiaTendencia(EstrategiaBase):
    nombre_interno = "estrategia_seguimiento_tendencia"

    def aplicar(self, df):
        df['SMA_50'] = sma(df, 50)
        df['SMA_200'] = sma(df, 200)
        señales = []
        posicion_abierta = None

        for i in range(1, len(df)):
            close = df['Close'].iloc[i]
            sma50 = df['SMA_50'].iloc[i]
            sma200 = df['SMA_200'].iloc[i]

            if close > sma50 and close > sma200:
                if posicion_abierta != "compra":
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = "compra"

            elif close < sma50 and close < sma200:
                if posicion_abierta != "venta":
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = "venta"

        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA VOLUME: Detecta aumentos inusuales de volumen
class EstrategiaVolume(EstrategiaBase):
    nombre_interno = "estrategia_volume"

    def aplicar(self, df):
        df['Volumen_Medio'] = df['Volume'].rolling(window=20).mean()
        df = df.dropna(subset=['Volumen_Medio'])
        señales = []
        posicion_abierta = None

        for i in range(1, len(df)):
            volumen_actual = df['Volume'].iloc[i]
            volumen_medio = df['Volumen_Medio'].iloc[i]

            if volumen_actual > 1.5 * volumen_medio and posicion_abierta != "compra":
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"

            elif volumen_actual < 0.5 * volumen_medio and posicion_abierta != "venta":
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"

        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA PRICE ACTION: Simulación simple basada en velas alcistas/bajistas
class EstrategiaPriceAction(EstrategiaBase):
    nombre_interno = "estrategia_price_action"

    def aplicar(self, df):
        df['RSI'] = rsi(df, window=self.config.get("lookback_period", 14))
        df['SMA_50'] = sma(df, 50)
        df['SMA_200'] = sma(df, 200)
        df = df.dropna(subset=['RSI', 'SMA_50', 'SMA_200'])

        señales = []
        posicion_abierta = None
        precio_entrada = None

        #Configuración de TP/SL
        take_profit = self.config.get("take_profit", 0.015)
        stop_loss = self.config.get("stop_loss", 0.005)

        for i in range(1, len(df)):
            close = df['Close'].iloc[i]
            open_ = df['Open'].iloc[i]
            close_prev = df['Close'].iloc[i - 1]
            open_prev = df['Open'].iloc[i - 1]
            rsi_val = df['RSI'].iloc[i]
            sma50 = df['SMA_50'].iloc[i]
            sma200 = df['SMA_200'].iloc[i]

            #Cierre de posición por TP o SL
            if posicion_abierta == "compra":
                if close >= precio_entrada * (1 + take_profit) or close <= precio_entrada * (1 - stop_loss):
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            elif posicion_abierta == "venta":
                if close <= precio_entrada * (1 - take_profit) or close >= precio_entrada * (1 + stop_loss):
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            #Vela alcista tras bajista + tendencia alcista + RSI bajo
            if (close > open_ and close_prev < open_prev and
                close > sma50 > sma200 and rsi_val < 30 and
                posicion_abierta != "compra"):
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"
                precio_entrada = close

            #Vela bajista tras alcista + tendencia bajista + RSI alto
            elif (close < open_ and close_prev > open_prev and
                  close < sma50 < sma200 and rsi_val > 70 and
                  posicion_abierta != "venta"):
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"
                precio_entrada = close

        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA SWING TRADING: Mantener posición de pocos días hasta semanas
class EstrategiaSwingTrading(EstrategiaBase):
    nombre_interno = "estrategia_swing_trading"

    def aplicar(self, df):
        df['SMA_10'] = sma(df, 10)
        df['SMA_30'] = sma(df, 30)
        df = df.dropna(subset=['SMA_10', 'SMA_30'])

        señales = []
        posicion_abierta = None

        for i in range(1, len(df)):
            sma10_actual = df['SMA_10'].iloc[i]
            sma30_actual = df['SMA_30'].iloc[i]
            sma10_prev = df['SMA_10'].iloc[i - 1]
            sma30_prev = df['SMA_30'].iloc[i - 1]

            cruzó_al_alza = sma10_actual > sma30_actual and sma10_prev <= sma30_prev
            cruzó_a_la_baja = sma10_actual < sma30_actual and sma10_prev >= sma30_prev

            if cruzó_al_alza and posicion_abierta != "compra":
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"

            elif cruzó_a_la_baja and posicion_abierta != "venta":
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"

        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA POSITION TRADING: Mantener largos periodos si hay confirmación técnica
class EstrategiaPositionTrading(EstrategiaBase):
    nombre_interno = "estrategia_position_trading"

    def aplicar(self, df):
        df['SMA_100'] = sma(df, 100)
        df['SMA_200'] = sma(df, 200)
        df = df.dropna(subset=['SMA_100', 'SMA_200'])

        señales = []
        posicion_abierta = None
        precio_entrada = None

        take_profit = self.config.get("take_profit", 0.05)
        stop_loss = self.config.get("stop_loss", 0.03)

        for i in range(1, len(df)):
            close = df['Close'].iloc[i]
            sma100 = df['SMA_100'].iloc[i]
            sma200 = df['SMA_200'].iloc[i]

            #Cierre por TP o SL
            if posicion_abierta == "compra":
                if close >= precio_entrada * (1 + take_profit) or close <= precio_entrada * (1 - stop_loss):
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = None
                    precio_entrada = None
                    continue
            elif posicion_abierta == "venta":
                if close <= precio_entrada * (1 - take_profit) or close >= precio_entrada * (1 + stop_loss):
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = None
                    precio_entrada = None
                    continue

            #Entrada en compra
            if close > sma100 and close > sma200 and posicion_abierta != "compra":
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"
                precio_entrada = close

            #Entrada en venta
            elif close < sma100 and close < sma200 and posicion_abierta != "venta":
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"
                precio_entrada = close

        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA ARBITRAGE(SIMULADA): Detecta diferencia de precios entre dos activos
class EstrategiaArbitrajeSimulado(EstrategiaBase):
    nombre_interno = "estrategia_arbitraje_simulado"

    def aplicar(self, df):
        # Simular la columna 'Close_B' si no existe
        if 'Close_B' not in df.columns:
            print("⚠️ Simulando columna 'Close_B' para pruebas.")
            df['Close_B'] = df['Close'].shift(1) * (1 + 0.001)  #<-Cambio pequeño

        # Calcular diferencia y estadísticas
        df['diff'] = df['Close'] - df['Close_B']
        df['media'] = df['diff'].rolling(10).mean()
        df['std'] = df['diff'].rolling(10).std()
        df = df.dropna(subset=['media', 'std'])

        señales = []
        posicion_abierta = None
        entrada_index = None
        precio_entrada = None

        take_profit = self.config.get("take_profit", 0.01)
        stop_loss = self.config.get("stop_loss", 0.005)

        for i in range(10, len(df)):
            diff = df['diff'].iloc[i]
            media = df['media'].iloc[i]
            std = df['std'].iloc[i]
            close = df['Close'].iloc[i]

            # Cierre por take profit o stop loss
            if posicion_abierta == "compra":
                if close >= precio_entrada * (1 + take_profit) or close <= precio_entrada * (1 - stop_loss):
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = None
                    entrada_index = None
                    precio_entrada = None
                    continue

            # Entrada por arbitraje simulado
            if posicion_abierta is None:
                if diff < media - std:
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = "compra"
                    entrada_index = i
                    precio_entrada = close
                elif diff > media + std:
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = "venta"
                    entrada_index = i
                    precio_entrada = close

        return pd.DataFrame(señales, columns=COLUMNAS)

#ESTRATEGIA PAIR TRADING(SIMULADA): Largo en un activo, corto en otro correlacionado
class EstrategiaPairTradingSimulada(EstrategiaBase):
    nombre_interno = "estrategia_pair_trading"

    def aplicar(self, df):
        if 'Close_B' not in df.columns:
            print("⚠️ Pair Trading requiere columna 'Close_B'. Simulando con Close desplazado.")
            df['Close_B'] = df['Close'].shift(1) * (1 + 0.001)

        df['spread'] = df['Close'] - df['Close_B']
        df['media'] = df['spread'].rolling(15).mean()
        df['std'] = df['spread'].rolling(15).std()
        df = df.dropna(subset=['media', 'std'])

        take_profit = self.config.get("take_profit", 0.015)
        stop_loss = self.config.get("stop_loss", 0.007)

        señales = []
        posicion_abierta = None
        precio_entrada = None
        entrada_index = None

        for i in range(15, len(df)):
            spread = df['spread'].iloc[i]
            media = df['media'].iloc[i]
            std = df['std'].iloc[i]
            close = df['Close'].iloc[i]

            # Salida
            if posicion_abierta == "compra":
                if close >= precio_entrada * (1 + take_profit) or close <= precio_entrada * (1 - stop_loss):
                    señales.append(generar_senal(df, i, False))
                    posicion_abierta = None
                    precio_entrada = None
                    entrada_index = None
                    continue

            elif posicion_abierta == "venta":
                if close <= precio_entrada * (1 - take_profit) or close >= precio_entrada * (1 + stop_loss):
                    señales.append(generar_senal(df, i, True))
                    posicion_abierta = None
                    precio_entrada = None
                    entrada_index = None
                    continue

            # Entrada
            if spread < media - 1.5 * std and posicion_abierta != "compra":
                señales.append(generar_senal(df, i, True))
                posicion_abierta = "compra"
                precio_entrada = close
                entrada_index = i

            elif spread > media + 1.5 * std and posicion_abierta != "venta":
                señales.append(generar_senal(df, i, False))
                posicion_abierta = "venta"
                precio_entrada = close
                entrada_index = i

        return pd.DataFrame(señales, columns=COLUMNAS)