# config.py

# Parámetros Binance y datos
TOP_SYMBOLS = ["ETHUSDT", "BTCUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]
BUFFER_MAXLEN = 1000
WS_RECONNECT_INTERVAL = 5
API_PORT = 8000

# Predicción
PREDICTION_WINDOW_SECONDS = 60
PREDICTION_MIN_TICKS = 100
PREDICTION_THRESHOLD = 0.001

# Predicción continua
PREDICTION_INTERVAL = 10    # Segundos entre predicciones
PREDICTION_HORIZON = 60     # 60 segundos = 1 minuto para predecir
PREDICTION_HISTORY = 300    # Mantener predicciones por 5 minutos

# Visualización
PLOT_HISTORY_SECONDS = 600  # 10 minutos de historial
PLOT_FUTURE_SECONDS = 120   # 2 minutos de predicción
UPDATE_INTERVAL = 1.0       # Segundos entre actualizaciones UI

# Alertas
ALERT_PRICE_CHANGE_THRESHOLD = 0.005  # 0.5%
ALERT_RSI_OVERBOUGHT = 70
ALERT_RSI_OVERSOLD = 30

# Validación de datos
MIN_PRICE_RATIO = 0.01  # 1% del precio promedio
MAX_PRICE_RATIO = 10.0  # 1000% del precio promedio
PRICE_VALIDATION_WINDOW = 20  # Ticks para calcular precio promedio

# Rendimiento
MAX_TICKS_PER_SECOND = 100  # Ahora no se usa para saltar, pero se mantiene

# Depuración
DEBUG = True

# Paths
DATA_DIR = "./data"
MODELS_DIR = "./models"