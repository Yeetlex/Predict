# utils.py

from datetime import datetime

def ms_to_datetime(ms):
    """Convierte timestamp en milisegundos a objeto datetime."""
    return datetime.fromtimestamp(ms / 1000.0)

def format_price(price, decimals=4):
    """Formatea un precio a un string con decimales fijos."""
    return f"{price:.{decimals}f}"

def percent_change(old, new):
    """Calcula cambio porcentual entre old y new."""
    if old == 0:
        return 0.0
    return ((new - old) / old) * 100

def clamp(value, min_value, max_value):
    """Limita value entre min_value y max_value."""
    return max(min_value, min(value, max_value))