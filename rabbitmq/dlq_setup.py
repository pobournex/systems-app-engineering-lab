"""Create a dead-letter exchange, a dead_letters queue, and orders_dlq_demo wired to them."""
from common import connect

conn = connect()
ch = conn.channel()

ch.exchange_declare(exchange="dlx", exchange_type="direct", durable=True)
ch.queue_declare(queue="dead_letters", durable=True)
ch.queue_bind(queue="dead_letters", exchange="dlx", routing_key="orders_dlq_demo")

ch.queue_declare(
    queue="orders_dlq_demo",
    durable=True,
    arguments={
        "x-dead-letter-exchange": "dlx",
        "x-dead-letter-routing-key": "orders_dlq_demo",
    },
)
print("dlq demo set up")
conn.close()
