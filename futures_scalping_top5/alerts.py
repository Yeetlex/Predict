# alerts.py

from indicators import calculate_rsi, calculate_bollinger_bands
from config import (
    ALERT_RSI_OVERBOUGHT, 
    ALERT_RSI_OVERSOLD,
    ALERT_PRICE_CHANGE_THRESHOLD,
    DEBUG
)

def check_alerts(symbol, price_series, prediction_direction):
    alerts = []
    
    if len(price_series) < 20:
        return alerts
    
    try:
        # Calcular indicadores
        rsi = calculate_rsi(price_series)
        lower_band, _, upper_band = calculate_bollinger_bands(price_series)
        
        # Análisis de precios
        last_price = price_series[-1]
        prev_price = price_series[-2]
        price_change = (last_price - prev_price) / prev_price
        
        # Alertas RSI
        if rsi > ALERT_RSI_OVERBOUGHT:
            alerts.append(f"⚠️ {symbol}: OVERBOUGHT (RSI {rsi:.1f})")
        elif rsi < ALERT_RSI_OVERSOLD:
            alerts.append(f"⚠️ {symbol}: OVERSOLD (RSI {rsi:.1f})")
        
        # Alertas Bollinger Bands
        if last_price >= upper_band:
            alerts.append(f"⚠️ {symbol}: UPPER BOLLINGER BAND ({last_price:.4f})")
        elif last_price <= lower_band:
            alerts.append(f"⚠️ {symbol}: LOWER BOLLINGER BAND ({last_price:.4f})")
        
        # Alertas de divergencia
        if prediction_direction == "up" and price_change < -ALERT_PRICE_CHANGE_THRESHOLD:
            alerts.append(f"‼️ {symbol}: SHARP DROP (-{abs(price_change)*100:.2f}%) DURING BULLISH PREDICTION")
        elif prediction_direction == "down" and price_change > ALERT_PRICE_CHANGE_THRESHOLD:
            alerts.append(f"‼️ {symbol}: SHARP SPIKE (+{price_change*100:.2f}%) DURING BEARISH PREDICTION")
            
    except Exception as e:
        if DEBUG:
            print(f"Error generating alerts: {e}")
    
    return alerts