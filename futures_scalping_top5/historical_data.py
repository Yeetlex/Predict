# historical_data.py

import requests
import time
from datetime import datetime, timedelta
import json

try:
    from config import HISTORICAL_MINUTES, BINANCE_REST_URL, DEBUG
except ImportError:
    # Valores por defecto si no están en config.py
    HISTORICAL_MINUTES = 5
    BINANCE_REST_URL = "https://api.binance.com/api/v3/"
    DEBUG = True

def fetch_historical_trades(symbol, minutes=HISTORICAL_MINUTES):
    """Obtiene datos históricos de Binance para un símbolo"""
    end_time = int(time.time() * 1000)
    start_time = end_time - minutes * 60 * 1000
    
    params = {
        'symbol': symbol.upper(),
        'limit': 1000,
        'startTime': start_time,
        'endTime': end_time
    }
    
    try:
        response = requests.get(f"{BINANCE_REST_URL}aggTrades", params=params)
        response.raise_for_status()
        trades = response.json()
        
        historical_ticks = []
        for trade in trades:
            historical_ticks.append({
                'price': float(trade['p']),
                'timestamp': trade['T']
            })
        
        if DEBUG:
            print(f"Fetched {len(historical_ticks)} historical trades for {symbol}")
        
        return historical_ticks
    
    except Exception as e:
        if DEBUG:
            print(f"Error fetching historical data for {symbol}: {e}")
        return []