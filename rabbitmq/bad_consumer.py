"""Broken on purpose: receives messages but never acks (unacked stall demo)."""
from common import connect

conn = connect()
ch = conn.channel()
ch.queue_declare(queue="orders", durable=True)
ch.basic_qos(prefetch_count=10)


def handle(ch, method, props, body):
    print("received (not acking)", body.decode())


ch.basic_consume(queue="orders", on_message_callback=handle)
print("holding messages, Ctrl+C to stop")
ch.start_consuming()
