#!/usr/bin/env python
import pika, sys, os, json, struct
from typing import Dict, Tuple

QUEUE_NAME1 = "MADE_Image_Generation bot2back"
QUEUE_NAME2 = "MADE_Image_Generation back2bot"
QUEUE_URL = "amqps://raqnxalf:eGIOYuVxZZK4LHSXRWZfRTI7euu1MuQK@rat.rmq2.cloudamqp.com/raqnxalf"

# Utils
def create_message(meta: Dict, image: bytes) -> bytes:
    meta = json.dumps(meta).encode("utf-8")
    header = struct.pack("!LL", len(meta), len(image))
    return b''.join((b'I', header, meta, image))

def decode_message(message: bytes) -> Tuple[Dict, bytes]:
    header = message[:9]
    signature, len_meta, len_image = struct.unpack("!cLL", header)
    assert signature == b'I'
    assert len(message) == struct.calcsize("!cLL") + len_meta + len_image
    metab = message[9:9 + len_meta]
    image = message[-len_image:]
    meta = json.loads(metab.decode("utf-8"))
    return meta, image

def main():
    params = pika.URLParameters(QUEUE_URL)
    pika_connection = pika.BlockingConnection(params)
    channel = pika_connection.channel()
    channel.queue_declare(queue=QUEUE_NAME1)
    channel.queue_declare(queue=QUEUE_NAME2)

    i = 0
    def callback(ch, method, properties, body: bytes):
        nonlocal i
        filename = f"file{i:05d}.jpg"
        meta, data = decode_message(body)
        with open(filename, "bw") as f:
            f.write(data)
        print(" [x] Received image, saved '%s'" % filename)
        i += 1

        meta["message"] = "Готово!"
        data = create_message(meta, data)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME2,
            body=data
        )

    channel.basic_consume(
        queue=QUEUE_NAME1,
        on_message_callback=callback,
        auto_ack=True
    )

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
