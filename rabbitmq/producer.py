"""Publish N messages to the durable 'orders' queue. Usage: python producer.py 1000"""
import sys
import pika
from common import connect

conn = connect()
ch = conn.channel()
ch.queue_declare(queue="orders", durable=True)

count = int(sys.argv[1]) if len(sys.argv) > 1 else 5
for i in range(count):
    ch.basic_publish(
        exchange="",
        routing_key="orders",
        body=f"order-{i}",
        properties=pika.BasicProperties(delivery_mode=2),
    )
print(f"sent {count} messages")
conn.close()
