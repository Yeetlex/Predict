# prediction_buffer.py

from collections import deque
import threading

class PredictionBuffer:
    """Almacena predicciones para comparación con precios reales"""
    
    def __init__(self, maxlen=100):
        self.buffer = deque(maxlen=maxlen)
        self.lock = threading.Lock()
        
    def add_prediction(self, timestamp, predicted_price, symbol):
        """Añade una nueva predicción"""
        with self.lock:
            self.buffer.append({
                'timestamp': timestamp,
                'predicted_price': predicted_price,
                'symbol': symbol,
                'actual_price': None
            })
            
    def match_actual_price(self, tick):
        """Empareja con predicciones en una ventana de ±30 segundos"""
        with self.lock:
            for prediction in self.buffer:
                if (prediction['symbol'] == tick['symbol'] and 
                    abs(prediction['timestamp'] - tick['timestamp']) < 30000 and
                    prediction['actual_price'] is None):
                    
                    prediction['actual_price'] = tick['price']
                    return prediction
        return None
        
    def get_predictions(self, symbol):
        """Obtiene todas las predicciones para un símbolo"""
        with self.lock:
            return [p for p in self.buffer if p['symbol'] == symbol]
            
    def clean_old_predictions(self, current_time_ms, max_age_ms=300000):
        """Elimina predicciones más viejas que max_age_ms"""
        with self.lock:
            self.buffer = deque(
                [p for p in self.buffer if current_time_ms - p['timestamp'] < max_age_ms],
                maxlen=self.buffer.maxlen
            )