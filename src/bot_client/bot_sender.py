"""
    MADE Image Generation Telegram Bot
"""
import os
import json
import struct
from typing import List, Dict, Tuple

import logging
import telebot
import pika
from telebot.types import Message
from dotenv import find_dotenv, load_dotenv


# Load env. variables
load_dotenv(find_dotenv())

## Constants
TOKEN = os.environ["TELEBOT_TOKEN"]
QUEUE_URL = os.environ["QUEUE_URL"]
QUEUE_NAME_bot2back = os.environ["QUEUE_NAME_FRONT"]
APP_NAME = "Telebot-Sender"

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
channel.queue_declare(queue=QUEUE_NAME_bot2back)
logger.info("Queue '%s' declared", QUEUE_NAME_bot2back)

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

# Telegram listener
def telegram_listener(messages: List[Message]):
    """
    When new messages arrive TeleBot will call this function.
    """
    for message in messages:
        logger.info("Got message from user")
        logger.info(json.dumps(message.json))
        if message.content_type != "photo":
            bot.reply_to(message, "Пришли мне картинку!")
            return
        image_info = bot.get_file(message.photo[-1].file_id)
        logger.info("Downloading file '%s'", image_info.file_path)
        image_content = bot.download_file(image_info.file_path)
        data = create_message(message.json, image_content)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME_bot2back,
            body=data
        )

# Main
def main():
    """
    Main
    """
    bot.set_update_listener(telegram_listener)
    logger.info("Starting cycle")
    bot.polling()

if __name__ == "__main__":
    main()
