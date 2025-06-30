# data_buffer.py

from collections import deque
import threading
import time
from config import BUFFER_MAXLEN, DEBUG, MIN_PRICE_RATIO, MAX_PRICE_RATIO, PRICE_VALIDATION_WINDOW

class DataBuffer:
    """Buffer circular con validación de precios y carga histórica"""
    
    def __init__(self, maxlen=BUFFER_MAXLEN):
        self.buffers = {}
        self.maxlen = maxlen
        self.lock = threading.Lock()
        self.price_stats = {}
        self.historical_loaded = {}
        
    def is_valid_price(self, symbol, price):
        symbol_key = symbol.upper()
        
        if symbol_key not in self.price_stats or len(self.price_stats[symbol_key]) < 5:
            return price > 0
        
        prices = self.price_stats[symbol_key]
        avg_price = sum(prices) / len(prices)
        min_valid = avg_price * MIN_PRICE_RATIO
        max_valid = avg_price * MAX_PRICE_RATIO
        
        return min_valid <= price <= max_valid
    
    def update_price_stats(self, symbol, price):
        symbol_key = symbol.upper()
        if symbol_key not in self.price_stats:
            self.price_stats[symbol_key] = deque(maxlen=PRICE_VALIDATION_WINDOW)
        self.price_stats[symbol_key].append(price)
    
    def add_tick(self, symbol, tick):
        with self.lock:
            symbol_key = symbol.upper()
            price = tick['price']
            
            if not self.is_valid_price(symbol_key, price):
                if DEBUG:
                    print(f"Invalid price for {symbol_key}: {price}. Skipping.")
                return False
                
            self.update_price_stats(symbol_key, price)
            
            if symbol_key not in self.buffers:
                self.buffers[symbol_key] = deque(maxlen=self.maxlen)
            self.buffers[symbol_key].append(tick)
            return True

    def load_historical_data(self, symbol, historical_ticks):
        """Carga datos históricos en el buffer"""
        with self.lock:
            symbol_key = symbol.upper()
            if symbol_key not in self.buffers:
                self.buffers[symbol_key] = deque(maxlen=self.maxlen)
            
            # Añadir datos históricos manteniendo el orden cronológico
            for tick in historical_ticks:
                if self.is_valid_price(symbol_key, tick['price']):
                    self.buffers[symbol_key].append(tick)
                    self.update_price_stats(symbol_key, tick['price'])
            
            self.historical_loaded[symbol_key] = True
            if DEBUG:
                print(f"Loaded {len(historical_ticks)} historical ticks for {symbol_key}")

    def get_buffer(self, symbol, max_ticks=None):
        with self.lock:
            symbol_key = symbol.upper()
            if symbol_key not in self.buffers or not self.buffers[symbol_key]:
                return []
                
            buffer = self.buffers[symbol_key]
            if max_ticks and len(buffer) > max_ticks:
                return list(buffer)[-max_ticks:]
            return list(buffer)
    
    def has_minimum_data(self, symbol):
        """Verifica si hay datos mínimos para mostrar"""
        with self.lock:
            symbol_key = symbol.upper()
            return symbol_key in self.historical_loaded

# Crea la instancia global
data_buffer = DataBuffer()
buffer_lock = threading.Lock()