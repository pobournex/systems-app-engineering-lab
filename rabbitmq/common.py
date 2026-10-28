import os
import pika


def connect():
    user = os.environ.get("RABBITMQ_USER", "labuser")
    password = os.environ["RABBITMQ_PASS"]  # set in your shell, never hard-code
    host = os.environ.get("RABBITMQ_HOST", "localhost")
    creds = pika.PlainCredentials(user, password)
    return pika.BlockingConnection(pika.ConnectionParameters(host, credentials=creds))
