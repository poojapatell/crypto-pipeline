import json
import asyncio
import websockets
from kafka import KafkaProducer
from datetime import datetime

# Kafka producer setup
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

async def binance_websocket():
    """Connect to Binance public WebSocket and stream crypto prices"""
    uri = "wss://stream.binance.com:9443/ws/btcusdt@trade"  # Bitcoin trades
    
    print(f"[{datetime.now()}] Connecting to Binance WebSocket...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"[{datetime.now()}] Connected! Streaming BTC trades...")
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                # Extract relevant fields
                price_tick = {
                    "timestamp": datetime.now().isoformat(),
                    "symbol": "BTCUSDT",
                    "price": float(data['p']),  # price
                    "quantity": float(data['q']),  # quantity
                    "trade_id": data['t']
                }
                
                # Publish to Kafka
                producer.send('price-ticks', value=price_tick)
                print(f"[{datetime.now()}] Published: {price_tick['symbol']} @ {price_tick['price']}")
                
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    asyncio.run(binance_websocket())