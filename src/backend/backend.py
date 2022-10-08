#!/usr/bin/env python
import pika, sys, os

QUEUE_NAME = "MADE_Image_Generation"
QUEUE_URL = "amqps://raqnxalf:eGIOYuVxZZK4LHSXRWZfRTI7euu1MuQK@rat.rmq2.cloudamqp.com/raqnxalf"

def main():
    params = pika.URLParameters(QUEUE_URL)
    pika_connection = pika.BlockingConnection(params)
    channel = pika_connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    def callback(ch, method, properties, body: bytes):
        print(" [x] Received %r" % body.decode("utf-8"))

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)