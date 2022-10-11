"""
    MADE Image Generation Telegram Bot
"""
from typing import List, Dict, Tuple
import os
import json
import struct
import pika
import logging
import telebot
import pika

## Constants
TOKEN = os.environ["TELEBOT_TOKEN"]
QUEUE_URL = os.environ["QUEUE_URL"]
QUEUE_NAME_back2bot = os.environ["QUEUE_NAME_BACK"]
APP_NAME = "Telebot-Receiver"

## Globals variables
# Logger
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(APP_NAME)

# Telegram
bot = telebot.TeleBot(TOKEN)
logger.info("Telegram bot created (%s)", bot.get_me().full_name)

# Queue
params = pika.URLParameters(QUEUE_URL)
pika_connection = pika.BlockingConnection(params)
channel = pika_connection.channel()
channel.queue_declare(queue=QUEUE_NAME_back2bot)
logger.info("Queue '%s' declared", QUEUE_NAME_back2bot)

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

# Backend listener
def queue_listener(ch, method, properties, body: bytes):
    """
    When a new message arrives from Backend
    """
    logger.info("Got message from back")
    meta, image = decode_message(body)
    logger.info(json.dumps(meta))
    bot.send_photo(meta["chat"]["id"], image)
    if "message" in meta:
        bot.send_message(chat_id=meta["chat"]["id"], text=meta["message"])

# Main
def main():
    """
    Main
    """
    channel.basic_consume(
        queue=QUEUE_NAME_back2bot,
        on_message_callback=queue_listener,
        auto_ack=True
    )
    channel.start_consuming()

if __name__ == "__main__":
    main()
