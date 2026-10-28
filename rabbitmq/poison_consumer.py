"""Acks good messages; nacks 'bad' ones with requeue=False so they dead-letter."""
from common import connect

conn = connect()
ch = conn.channel()


def handle(ch, method, props, body):
    msg = body.decode()
    if "bad" in msg:
        print("rejecting (-> DLQ):", msg)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    else:
        print("ok:", msg)
        ch.basic_ack(delivery_tag=method.delivery_tag)


ch.basic_consume(queue="orders_dlq_demo", on_message_callback=handle)
print("waiting, Ctrl+C to stop")
ch.start_consuming()
