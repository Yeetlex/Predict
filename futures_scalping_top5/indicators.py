# indicators.py

import numpy as np

def calculate_rsi(prices, period=14):
    """
    Calcula el RSI (Relative Strength Index) para una lista o array de precios.
    """
    prices = np.array(prices)
    if len(prices) < period + 1:
        return np.nan
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    
    # Calcular EMA para ganancias y pérdidas
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    # Suavizado exponencial
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss < 1e-10:  # Evitar división por cero
        return 100.0 if avg_gain > 0 else 50.0

    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))

def calculate_bollinger_bands(prices, window=20, num_std=2):
    """
    Calcula las bandas de Bollinger para una lista o array de precios.
    """
    prices = np.array(prices)
    if len(prices) < window:
        return (np.nan, np.nan, np.nan)
    
    # Usar ventana móvil
    moving_avg = np.mean(prices[-window:])
    std_dev = np.std(prices[-window:])
    
    return (
        moving_avg - num_std * std_dev,
        moving_avg,
        moving_avg + num_std * std_dev
    )