# strategy_recommend.py
#Parámetros recomendados por estrategia de trading

RECOMENDACIONES = {
    "estrategia_breakout": {
        "candle_size": "30min",  # Necesario para confirmar rupturas
        "lookback_period": 20,
        "total_data_needed": 100,
        "execution_frequency": "on_new_candle",
        "signal_delay": 1,
        "time_filter": {"start": "09:30", "end": "16:00"},
        "slippage_tolerance": 0.05,
    },
    "estrategia_reversal": {
        "candle_size": "15min",  # Detecta patrones de reversión más rápidos
        "lookback_period": 10,
        "total_data_needed": 60,
        "execution_frequency": "on_new_candle",
        "signal_delay": 1,
        "time_filter": {"start": "10:00", "end": "15:00"},
        "slippage_tolerance": 0.1,
    },
    "estrategia_rango": {
        "candle_size": "1h",  # Ideal para consolidaciones prolongadas
        "lookback_period": 14,
        "total_data_needed": 70,
        "execution_frequency": "on_close",
        "signal_delay": 1,
        "time_filter": {"start": "09:30", "end": "16:00"},
        "slippage_tolerance": 0.05,
    },
    "estrategia_day_trading": {
        "candle_size": "5min",  # Alta frecuencia para decisiones intradía
        "lookback_period": 5,
        "total_data_needed": 100,
        "execution_frequency": "on_new_candle",
        "signal_delay": 0,
        "time_filter": {"start": "09:30", "end": "16:00"},
        "slippage_tolerance": 0.1,
    },
    "estrategia_news_trading": {
        "candle_size": "1min",  # Reacciona a noticias en tiempo real
        "lookback_period": 3,
        "total_data_needed": 40,
        "execution_frequency": "on_event",
        "signal_delay": 1,
        "time_filter": {"start": "08:00", "end": "18:00"},
        "slippage_tolerance": 0.2,
    },
    "estrategia_rsi_simple": {
        "candle_size": "30min",  # Velas intermedias para RSI clásico
        "lookback_period": 14,
        "total_data_needed": 50,
        "execution_frequency": "on_close",
        "signal_delay": 1,
        "time_filter": {"start": "09:30", "end": "16:00"},
        "slippage_tolerance": 0.05,
    },
    "estrategia_macd_cruce": {
        "candle_size": "1h",  # MACD requiere contexto más amplio
        "lookback_period": 26,
        "total_data_needed": 80,
        "execution_frequency": "on_close",
        "signal_delay": 1,
        "time_filter": {"start": "09:30", "end": "16:00"},
        "slippage_tolerance": 0.05,
    },
    "estrategia_basica_medias": {
        "candle_size": "1h",  # Cruce de medias más confiable en 1h
        "lookback_period": 20,
        "total_data_needed": 60,
        "execution_frequency": "on_new_candle",
        "signal_delay": 1,
        "time_filter": {"start": "10:00", "end": "15:30"},
        "slippage_tolerance": 0.1,
    },
    "estrategia_momentum": {
        "candle_size": "15min",  # Mejor detectado en marcos rápidos
        "lookback_period": 20,
        "total_data_needed": 50,
        "execution_frequency": "on_close",
        "signal_delay": 1,
        "time_filter": {"start": "09:30", "end": "16:00"},
        "slippage_tolerance": 0.1,
    },
    "estrategia_scalping": {
        "candle_size": "1min",  # Requiere decisiones inmediatas
        "lookback_period": 14,
        "total_data_needed": 40,
        "execution_frequency": "on_tick",
        "signal_delay": 0,
        "time_filter": {"start": "09:30", "end": "12:00"},
        "slippage_tolerance": 0.3,
    },
    "estrategia_reversion_media": {
        "candle_size": "1h",  # Necesita tiempo para detectar sobreextensión
        "lookback_period": 20,
        "total_data_needed": 80,
        "execution_frequency": "on_close",
        "signal_delay": 1,
        "time_filter": {"start": "10:00", "end": "15:00"},
        "slippage_tolerance": 0.05,
    },
    "estrategia_seguimiento_tendencia": {
        "candle_size": "1d",  # Tendencias de largo plazo
        "lookback_period": 50,
        "total_data_needed": 100,
        "execution_frequency": "on_close",
        "signal_delay": 1,
        "time_filter": {"start": "09:30", "end": "16:00"},
        "slippage_tolerance": 0.1,
    },
    "estrategia_volume": {
        "candle_size": "15min",
        "lookback_period": 20,
        "total_data_needed": 30,
        "execution_frequency": "on_new_candle",
        "signal_delay": 1,
        "time_filter": {"start": "09:30", "end": "16:00"},
        "slippage_tolerance": 0.1,
    },
    "estrategia_price_action": {
        "candle_size": "5min",  # Ideal para patrones visuales rápidos
        "lookback_period": 1,
        "total_data_needed": 10,
        "execution_frequency": "on_new_candle",
        "signal_delay": 1,
        "time_filter": {"start": "09:30", "end": "16:00"},
        "slippage_tolerance": 0.05,
    },
    "estrategia_swing_trading": {
        "candle_size": "1d",
        "lookback_period": 30,
        "total_data_needed": 50,
        "execution_frequency": "on_close",
        "signal_delay": 1,
        "time_filter": {"start": "09:30", "end": "16:00"},
        "slippage_tolerance": 0.1,
    },
    "estrategia_position_trading": {
        "candle_size": "1d",
        "lookback_period": 100,
        "total_data_needed": 200,
        "execution_frequency": "on_close",
        "signal_delay": 1,
        "time_filter": {"start": "09:30", "end": "16:00"},
        "slippage_tolerance": 0.05,
    },
    "estrategia_arbitraje_simulado": {
        "candle_size": "15min",
        "lookback_period": 10,
        "total_data_needed": 30,
        "execution_frequency": "on_close",
        "signal_delay": 1,
        "time_filter": {"start": "09:30", "end": "16:00"},
        "slippage_tolerance": 0.05,
    },
    "estrategia_pair_trading": {
        "candle_size": "15min",
        "lookback_period": 15,
        "total_data_needed": 40,
        "execution_frequency": "on_close",
        "signal_delay": 1,
        "time_filter": {"start": "09:30", "end": "16:00"},
        "slippage_tolerance": 0.05,
    },
}
