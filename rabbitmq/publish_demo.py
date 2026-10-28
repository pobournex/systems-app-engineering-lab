"""Publish 3 good and 2 'bad' messages to orders_dlq_demo."""
import pika
from common import connect

conn = connect()
ch = conn.channel()
for m in ["order-1", "bad-order-2", "order-3", "bad-order-4", "order-5"]:
    ch.basic_publish(
        exchange="",
        routing_key="orders_dlq_demo",
        body=m,
        properties=pika.BasicProperties(delivery_mode=2),
    )
print("published 5")
conn.close()
