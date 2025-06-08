# utils.py
import pandas as pd

def format_percent(df: pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy()
    df[col] = df[col].map(lambda x: f"{x:.2f}%")
    return df

def add_rolling(df: pd.DataFrame, col="current_price", window=5) -> pd.DataFrame:
    df = df.sort_values("timestamp")
    out = df.copy()
    out[f"{col}_rolling_{window}"] = out[col].rolling(window).mean()
    return out

def compute_rsi(df: pd.DataFrame, col="price", window=14) -> pd.DataFrame:
    df = df.copy()
    delta = df[col].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window, adjust=False).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))
    return df

def compute_macd(df: pd.DataFrame, col="price", fast=12, slow=26, signal=9) -> pd.DataFrame:
    df = df.copy()
    ema_fast = df[col].ewm(span=fast, adjust=False).mean()
    ema_slow = df[col].ewm(span=slow, adjust=False).mean()
    df["macd"] = ema_fast - ema_slow
    df["macd_signal"] = df["macd"].ewm(span=signal, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    return df
