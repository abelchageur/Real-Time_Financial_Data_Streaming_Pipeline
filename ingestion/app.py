import json
import os
import websocket
from kafka import KafkaProducer

# Configure Kafka producer
producer = KafkaProducer(
    bootstrap_servers=os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Get API key from environment variable
API_KEY = os.environ.get('FINNHUB_API_KEY', '')
if not API_KEY:
    print("WARNING: FINNHUB_API_KEY environment variable not set!")

def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {message[:100]}...")  # Print start of message for debugging
    
    # Send data to Kafka if it's trade data
    if data['type'] == 'trade':
        for trade in data['data']:
            trade_data = {
                'symbol': trade['s'],
                'price': trade['p'],
                'volume': trade['v'],
                'timestamp': trade['t']
            }
            producer.send('raw-financial-data', trade_data)
            print(f"Sent to Kafka: {trade['s']} price={trade['p']}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, *args):
    print("### Connection closed ###")

def on_open(ws):
    print("Connection open, subscribing to symbols...")
    ws.send('{"type":"subscribe","symbol":"AAPL"}')
    ws.send('{"type":"subscribe","symbol":"AMZN"}')
    ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
    ws.send('{"type":"subscribe","symbol":"IC MARKETS:1"}')
    print("Subscriptions sent")

if __name__ == "__main__":
    websocket.enableTrace(True)
    socket_url = f"wss://ws.finnhub.io?token={API_KEY}"
    print(f"Connecting to Finnhub with API key: {API_KEY[:4]}****")
    
    ws = websocket.WebSocketApp(socket_url,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    ws.on_open = on_open
    
    print("Starting WebSocket connection...")
    ws.run_forever()