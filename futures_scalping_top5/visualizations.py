# visualizations.py

from datetime import datetime, timedelta
import plotly.graph_objs as go
from utils import ms_to_datetime

try:
    from config import PLOT_HISTORY_SECONDS, PLOT_FUTURE_SECONDS
except ImportError:
    PLOT_HISTORY_SECONDS = 600
    PLOT_FUTURE_SECONDS = 120

def plot_price_and_prediction(ticks, predictions, window_seconds=60):
    fig = go.Figure()
    
    # Manejar caso sin datos
    if not ticks:
        # Crear un gráfico vacío con rango de tiempo razonable
        now = datetime.now()
        empty_times = [now - timedelta(seconds=PLOT_HISTORY_SECONDS), now]
        fig.add_trace(go.Scatter(
            x=empty_times,
            y=[0, 0],
            mode='lines',
            name='Waiting for data...',
            line=dict(color='gray', dash='dot'))
        )
        fig.update_layout(
            title='Waiting for data...',
            xaxis_title='Time',
            yaxis_title='Price (USD)',
            template='plotly_dark'
        )
        return fig
    
    # Procesar datos históricos
    now_ms = ticks[-1]['timestamp']
    history_ms = PLOT_HISTORY_SECONDS * 1000
    relevant_ticks = [t for t in ticks if now_ms - t['timestamp'] <= history_ms]
    
    if relevant_ticks:
        times = [ms_to_datetime(t['timestamp']) for t in relevant_ticks]
        prices = [t['price'] for t in relevant_ticks]
        
        fig.add_trace(go.Scatter(
            x=times,
            y=prices,
            mode='lines',
            name='Actual Price',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='%{y:.4f}<extra></extra>'
        ))
    
    # Procesar predicciones
    if predictions:
        now_ms = ticks[-1]['timestamp']
        max_future_ms = now_ms + PLOT_FUTURE_SECONDS * 1000
        min_past_ms = now_ms - PLOT_HISTORY_SECONDS * 1000
        visible_predictions = [
            p for p in predictions 
            if min_past_ms <= p['timestamp'] <= max_future_ms
        ]
        
        pending_predictions = [p for p in visible_predictions if p['actual_price'] is None]
        verified_predictions = [p for p in visible_predictions if p['actual_price'] is not None]
        
        if pending_predictions:
            pred_times = [ms_to_datetime(p['timestamp']) for p in pending_predictions]
            pred_prices = [p['predicted_price'] for p in pending_predictions]
            
            fig.add_trace(go.Scatter(
                x=pred_times,
                y=pred_prices,
                mode='markers',
                name='Future Predictions',
                marker=dict(
                    color='orange',
                    size=10,
                    symbol='triangle-up'
                ),
                hovertemplate='Predicted: %{y:.4f}<extra></extra>'
            ))
        
        if verified_predictions:
            actual_times = [ms_to_datetime(p['timestamp']) for p in verified_predictions]
            actual_prices = [p['actual_price'] for p in verified_predictions]
            pred_prices = [p['predicted_price'] for p in verified_predictions]
            
            errors = [abs(pred - actual) for pred, actual in zip(pred_prices, actual_prices)]
            colors = ['green' if e < 0.001 else 'red' for e in errors]
            
            fig.add_trace(go.Scatter(
                x=actual_times,
                y=actual_prices,
                mode='markers',
                name='Verified Predictions',
                marker=dict(
                    color=colors,
                    size=10,
                    symbol='circle'
                ),
                hovertemplate='Actual: %{y:.4f}<extra></extra>'
            ))
            
            for prediction in verified_predictions:
                pred_time = ms_to_datetime(prediction['timestamp'])
                
                fig.add_trace(go.Scatter(
                    x=[pred_time, pred_time],
                    y=[prediction['predicted_price'], prediction['actual_price']],
                    mode='lines',
                    line=dict(color='gray', width=1, dash='dot'),
                    showlegend=False,
                    hoverinfo='none'
                ))
    
    # Configuración del layout
    fig.update_layout(
        title=f'Price & 1-Minute Predictions',
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=50, r=30, t=60, b=40),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type='date'
        )
    )
    
    # Ajustar rango temporal
    if ticks:
        last_time = ms_to_datetime(ticks[-1]['timestamp'])
        fig.update_xaxes(
            range=[last_time - timedelta(seconds=PLOT_HISTORY_SECONDS),
                   last_time + timedelta(seconds=PLOT_FUTURE_SECONDS)]
        )
    
    return fig