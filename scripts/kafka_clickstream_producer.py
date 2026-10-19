"""
Kafka Producer Script mô phỏng luồng Clickstream sự kiện thời gian thực (Streaming Simulation)
Gửi log tương tác người dùng (view, addtocart, transaction) vào Kafka Topic: 'ecommerce_clickstream'
"""

import json
import time
import random
from datetime import datetime

# Giả lập hoặc kết nối Kafka nếu có môi trường
def create_sample_event():
    event_types = ['view', 'view', 'view', 'addtocart', 'transaction']
    weights = [0.8, 0.8, 0.8, 0.15, 0.05]
    chosen_event = random.choices(event_types, weights=weights)[0]
    
    event = {
        "timestamp": int(time.time() * 1000),
        "visitorid": random.randint(10000, 200000),
        "event": chosen_event,
        "itemid": random.randint(1000, 50000),
        "transactionid": random.randint(100000, 999999) if chosen_event == 'transaction' else None
    }
    return event

def main():
    print("=" * 60)
    print("   KAFKA CLICKSTREAM STREAMING PRODUCER (SIMULATION)")
    print("=" * 60)
    print("Topic mục tiêu: ecommerce_clickstream")
    print("Cơ chế phân vùng: Phân tán theo visitorid (Hash Partitioning)")
    print("=" * 60)
    
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: str(k).encode('utf-8')
        )
        print("[+] Kết nối Kafka Broker thành công! Bắt đầu phát luồng sự kiện...")
        is_connected = True
    except Exception as e:
        print(f"[!] Chế độ Standalone Simulation (Chưa bật Kafka container): {e}")
        is_connected = False

    for i in range(10):
        evt = create_sample_event()
        if is_connected:
            producer.send('ecommerce_clickstream', key=evt['visitorid'], value=evt)
        print(f"[Kafka Event {i+1}] Visitor {evt['visitorid']} -> {evt['event'].upper()} Item {evt['itemid']}")
        time.sleep(0.5)

    if is_connected:
        producer.flush()
        print("\n[+] Đã gửi thành công 10 sự kiện vào Kafka Topic!")
    else:
        print("\n[+] Hoàn tất giả lập luồng sự kiện Kafka Clickstream.")

if __name__ == "__main__":
    main()
