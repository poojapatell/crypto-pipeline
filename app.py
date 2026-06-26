from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import random

app = FastAPI(title="Crypto Pipeline API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Crypto Pipeline API", "version": "1.0"}

@app.get("/latest")
def get_latest():
    base_price = 62500 + random.uniform(-100, 100)
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": "BTCUSDT",
        "price": round(base_price, 2),
        "moving_average": round(base_price - random.uniform(0, 50), 2),
        "volatility": round(random.uniform(0.001, 0.01), 4),
        "price_change": round(random.uniform(-10, 10), 2)
    }

@app.get("/history/{minutes}")
def get_history(minutes: int = 60):
    data = []
    base_price = 62500
    for i in range(minutes):
        price = base_price + random.uniform(-200, 200)
        data.append({
            "timestamp": (datetime.utcnow() - timedelta(minutes=minutes-i)).isoformat(),
            "price": round(price, 2),
            "moving_average": round(price - random.uniform(0, 50), 2),
            "volatility": round(random.uniform(0.001, 0.01), 4)
        })
    return data

@app.get("/stats")
def get_stats():
    return {
        "total_records": 157000,
        "price_min": 62000,
        "price_max": 63500,
        "price_mean": 62500,
        "price_std": 250,
        "avg_volatility": 0.0045
    }

@app.get("/anomalies")
def get_anomalies():
    return {"recent_anomalies": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)