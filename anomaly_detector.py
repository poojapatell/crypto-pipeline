from kafka import KafkaConsumer
from collections import deque
import json
import statistics
import boto3
from datetime import datetime

# Kafka consumer
consumer = KafkaConsumer(
    'price-ticks',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',  # Start from latest (real-time, not backlog)
    group_id='anomaly-detector'
)

# AWS SNS for alerts
sns = boto3.client('sns', region_name='us-east-1')
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:AKIA6ISJ3EPFS66QSWWR:crypto-alerts"  # Create this manually or use print instead

# Rolling window for stats (last 100 ticks)
price_window = deque(maxlen=100)
threshold = 3  # Z-score threshold for anomaly

print("[INFO] Anomaly Detector started. Monitoring BTC prices...")

try:
    for message in consumer:
        data = message.value
        price = data['price']
        timestamp = data['timestamp']
        
        price_window.append(price)
        
        # Need at least 20 prices to compute meaningful stats
        if len(price_window) < 20:
            print(f"[INFO] Warming up... {len(price_window)}/20 prices collected")
            continue
        
        # Compute rolling mean and std dev
        mean = statistics.mean(price_window)
        stdev = statistics.stdev(price_window)
        
        # Z-score
        z_score = (price - mean) / stdev if stdev > 0 else 0
        
        # Flag anomaly
        if abs(z_score) > threshold:
            alert_msg = f"🚨 ANOMALY DETECTED\nSymbol: {data['symbol']}\nPrice: ${price}\nMean: ${mean:.2f}\nZ-Score: {z_score:.2f}\nTime: {timestamp}"
            
            print(f"\n{alert_msg}\n")
            
            # Try to send SNS alert (or just print if SNS not set up)
            try:
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject="Crypto Price Anomaly Detected",
                    Message=alert_msg
                )
            except Exception as e:
                print(f"[DEBUG] SNS alert skipped (topic not configured): {e}")
        
        else:
            print(f"[{timestamp}] {data['symbol']} @ ${price} | Z-Score: {z_score:.3f} | Status: Normal")

except KeyboardInterrupt:
    print("[INFO] Anomaly Detector stopped")
finally:
    consumer.close()