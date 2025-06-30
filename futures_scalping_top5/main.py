# main.py

import threading
import time
import streamlit as st
from ws_client import BinanceWSClient
from rest_api import run_api
from visualizations import plot_price_and_prediction
from prediction_buffer import PredictionBuffer
from predictor import predict_future_price
from data_buffer import data_buffer, buffer_lock
from historical_data import fetch_historical_trades
try:
    from config import TOP_SYMBOLS, PREDICTION_WINDOW_SECONDS, UPDATE_INTERVAL, PLOT_HISTORY_SECONDS, PREDICTION_INTERVAL, PREDICTION_HORIZON, DEBUG, HISTORICAL_MINUTES
except ImportError as e:
    st.error(f"Error importing configuration: {e}")
    # Valores por defecto
    TOP_SYMBOLS = ["ETHUSDT", "BTCUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]
    PREDICTION_WINDOW_SECONDS = 60
    UPDATE_INTERVAL = 1.0
    PLOT_HISTORY_SECONDS = 600
    PREDICTION_INTERVAL = 10
    PREDICTION_HORIZON = 60
    DEBUG = True
    HISTORICAL_MINUTES = 5  # Valor por defecto para datos históricos

# UI de Streamlit
st.title("💰 Crypto Live Price & 1-Minute Prediction")
symbol = st.selectbox("Select Pair", [s.lower() for s in TOP_SYMBOLS])
window_sec = st.slider("Prediction Window (seconds)", 10, 300, PREDICTION_WINDOW_SECONDS, 10)

# Contenedores para actualización
chart_placeholder = st.empty()
status_placeholder = st.container()
alerts_placeholder = st.container()
loading_placeholder = st.empty()

# Iniciar servicios solo una vez
if 'services_started' not in st.session_state:
    loading_placeholder.info("Loading historical data and starting services...")
    
    try:
        # Descargar y cargar datos históricos para el símbolo seleccionado
        symbol_key = symbol.upper()
        historical_ticks = fetch_historical_trades(symbol_key, minutes=HISTORICAL_MINUTES)
        
        if historical_ticks:
            with buffer_lock:
                data_buffer.load_historical_data(symbol_key, historical_ticks)
        else:
            loading_placeholder.warning("Could not load historical data. Starting with empty buffer.")
        
        # Iniciar WebSocket client
        ws_client = BinanceWSClient()
        ws_client.start()
        
        # Iniciar API server
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        
        st.session_state.services_started = True
        loading_placeholder.empty()
    except Exception as e:
        loading_placeholder.error(f"Failed to start services: {e}")

# Crear buffer de predicciones
if 'prediction_buffer' not in st.session_state:
    st.session_state.prediction_buffer = PredictionBuffer(maxlen=200)

prediction_buffer = st.session_state.prediction_buffer

# Bucle principal
last_update = 0
last_prediction_time = 0
symbol_upper = symbol.upper()

while True:
    try:
        current_time = time.time()
        
        # Obtener datos actuales
        with buffer_lock:
            ticks = data_buffer.get_buffer(symbol_upper)
            has_min_data = data_buffer.has_minimum_data(symbol_upper)
        
        # Si no hay datos mínimos, mostrar mensaje
        if not has_min_data and not ticks:
            with status_placeholder:
                st.warning("Waiting for initial data...")
            time.sleep(1)
            continue
        
        if ticks:
            last_tick = ticks[-1]
            current_time_ms = last_tick['timestamp']
            
            # Hacer predicción periódica
            if current_time - last_prediction_time >= PREDICTION_INTERVAL:
                future_price = predict_future_price(ticks, PREDICTION_HORIZON)
                if future_price is not None:
                    prediction_time = current_time_ms + PREDICTION_HORIZON * 1000
                    prediction_buffer.add_prediction(
                        prediction_time,
                        future_price,
                        symbol_upper
                    )
                    if DEBUG:
                        st.sidebar.write(f"Prediction added: {future_price:.4f} in {PREDICTION_HORIZON} seconds")
                    last_prediction_time = current_time
            
            # Emparejar predicciones con datos reales
            matched = prediction_buffer.match_actual_price({
                'symbol': symbol_upper,
                'timestamp': current_time_ms,
                'price': last_tick['price']
            })
            
            # Limpiar predicciones antiguas
            prediction_buffer.clean_old_predictions(current_time_ms, max_age_ms=300000)
        
        # Actualizar UI
        if current_time - last_update >= UPDATE_INTERVAL:
            predictions = prediction_buffer.get_predictions(symbol_upper)
            
            # Actualizar gráfico
            fig = plot_price_and_prediction(ticks, predictions, window_sec)
            chart_placeholder.plotly_chart(fig, use_container_width=True)
            
            # Mostrar métricas
            with status_placeholder:
                st.subheader("Market Status")
                
                if ticks:
                    last_price = ticks[-1]['price']
                    st.metric("Current Price", f"${last_price:.4f}")
                    
                    if predictions:
                        latest_prediction = predictions[-1]
                        st.metric("Latest Prediction", 
                                f"${latest_prediction['predicted_price']:.4f} in {PREDICTION_HORIZON}s")
                    
                    # Mostrar estadísticas de validación
                    with buffer_lock:
                        if hasattr(data_buffer, 'price_stats') and symbol_upper in data_buffer.price_stats:
                            prices = list(data_buffer.price_stats[symbol_upper])
                            if prices:
                                avg_price = sum(prices) / len(prices)
                                st.caption(f"Validation - Avg: ${avg_price:.4f}, Range: ${avg_price * MIN_PRICE_RATIO:.4f} to ${avg_price * MAX_PRICE_RATIO:.4f}")
                else:
                    st.warning("Waiting for real-time data...")
            
            last_update = current_time
        
        time.sleep(0.05)
    except Exception as e:
        if DEBUG:
            st.sidebar.error(f"Error in main loop: {e}")
        time.sleep(1)