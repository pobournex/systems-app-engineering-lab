"""Good consumer: processes and acks each message (this is what 'drains' the queue)."""
import time
from common import connect

conn = connect()
ch = conn.channel()
ch.queue_declare(queue="orders", durable=True)
ch.basic_qos(prefetch_count=10)


def handle(ch, method, props, body):
    print("got", body.decode())
    time.sleep(0.05)
    ch.basic_ack(delivery_tag=method.delivery_tag)


ch.basic_consume(queue="orders", on_message_callback=handle)
print("waiting, Ctrl+C to stop")
ch.start_consuming()
