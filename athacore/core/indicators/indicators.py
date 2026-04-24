import pandas as pd


def sma(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Media móvil simple (Simple Moving Average)."""
    return df['Close'].rolling(window=window).mean()


def ema(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Media móvil exponencial (Exponential Moving Average)."""
    return df['Close'].ewm(span=window, adjust=False).mean()


def rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Índice de Fuerza Relativa (Relative Strength Index)."""
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def macd(df: pd.DataFrame, short_window: int = 12, long_window: int = 26, signal_window: int = 9) -> pd.DataFrame:
    """MACD: Moving Average Convergence Divergence."""
    ema_short = ema(df, short_window)
    ema_long = ema(df, long_window)
    macd_line = ema_short - ema_long
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()

    return pd.DataFrame({
        'macd_line': macd_line,
        'signal_line': signal_line,
        'histogram': macd_line - signal_line
    })
