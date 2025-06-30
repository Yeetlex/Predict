# rest_api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import DEBUG, API_PORT, MIN_PRICE_RATIO, MAX_PRICE_RATIO
from data_buffer import data_buffer, buffer_lock

app = FastAPI()

# Configuración CORS segura
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/ticks/{symbol}")
def get_ticks(symbol: str, max_ticks: int = 200):
    symbol = symbol.upper()
    with buffer_lock:
        ticks = data_buffer.get_buffer(symbol, max_ticks)
    if not ticks:
        raise HTTPException(404, detail="No hay datos disponibles")
    return {"symbol": symbol, "ticks": ticks, "count": len(ticks)}

@app.get("/price_stats/{symbol}")
def get_price_stats(symbol: str):
    symbol = symbol.upper()
    with buffer_lock:
        if hasattr(data_buffer, 'price_stats') and symbol in data_buffer.price_stats:
            prices = list(data_buffer.price_stats[symbol])
            avg = sum(prices) / len(prices) if prices else 0
            return {
                "symbol": symbol,
                "current_avg": avg,
                "min_valid": avg * MIN_PRICE_RATIO,
                "max_valid": avg * MAX_PRICE_RATIO,
                "samples": len(prices)
            }
        return {"symbol": symbol, "error": "No hay estadísticas disponibles"}

def add_tick_to_buffer(symbol: str, tick: dict):
    try:
        with buffer_lock:
            return data_buffer.add_tick(symbol.upper(), tick)
    except Exception as e:
        if DEBUG:
            print(f"Error adding tick to buffer: {str(e)}")
        return False

def run_api():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=API_PORT, log_level="warning" if not DEBUG else "info")