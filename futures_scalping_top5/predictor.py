# predictor.py

import numpy as np
from scipy.signal import savgol_filter
from config import PREDICTION_MIN_TICKS

def predict_future_price(ticks, future_seconds=60):
    """Predice el precio en X segundos en el futuro usando datos suavizados"""
    if not ticks or len(ticks) < PREDICTION_MIN_TICKS:
        return None
        
    window_size = min(200, len(ticks))
    recent_ticks = ticks[-window_size:]
    
    timestamps = np.array([t['timestamp'] for t in recent_ticks])
    prices = np.array([t['price'] for t in recent_ticks])
    
    # Suavizar los precios para reducir el ruido
    if len(prices) > 10:
        window_length = min(51, len(prices))  # Longitud impar
        polyorder = 2
        prices_smoothed = savgol_filter(prices, window_length, polyorder)
    else:
        prices_smoothed = prices
    
    # Tiempo relativo en segundos
    time_sec = (timestamps - timestamps[0]) / 1000.0
    
    # Regresión lineal con ponderación exponencial
    weights = np.exp(np.linspace(-1, 0, len(time_sec)))
    A = np.vstack([time_sec * weights, weights]).T
    slope, intercept = np.linalg.lstsq(A, prices_smoothed * weights, rcond=None)[0]
    
    # Predecir precio en X segundos
    last_timestamp = timestamps[-1]
    prediction_time = (last_timestamp - timestamps[0]) / 1000.0 + future_seconds
    return slope * prediction_time + intercept