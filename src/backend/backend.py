"""
Thematic Image Generation backend app

"""
import os
import sys
import json
import struct
from typing import Dict, Tuple

import pika
import dill
from dotenv import find_dotenv, load_dotenv

from logger import Logger
# from saver import Drive


class Application:
    """
    Connect to queue, get data, run prediction, send results
    
    """

    def __init__(self, config) -> None:
        self.input_queue_name = config['input_queue_name']
        self.output_queue_name = config['output_queue_name']
        self.queue_url = config['queue_url']
        self.model_path = config['model']
        self.logger = Logger()
        # self.drive = Drive()
        self.logger.info("Initializtion finished")


    def run(self) -> None:
        """ Runs prediction and sends results """

        def create_message(meta: Dict, image: bytes) -> bytes:
            """ Create message """

            meta = json.dumps(meta).encode("utf-8")
            header = struct.pack("!LL", len(meta), len(image))

            return b''.join((b'I', header, meta, image))


        def decode_message(message: bytes) -> Tuple[Dict, bytes]:
            """ Decode data from queue """

            header = message[:9]
            signature, len_meta, len_image = struct.unpack("!cLL", header)

            if signature != b'I':
                self.logger.error("Wrong signature format")
                raise ValueError("Wrong signature format")

            assert len(message) == struct.calcsize("!cLL") + len_meta + len_image
            metab = message[9:9 + len_meta]
            image = message[-len_image:]
            meta = json.loads(metab.decode("utf-8"))

            return meta, image


        def on_recv_callback(ch, method, properties, body: bytes) -> None:
            """ Inference callback"""

            meta, image = decode_message(body)
            self.logger.info(f"[x] Received message: {meta}")
            self.logger.debug("Start inference")
            res_image = self.model.predict(meta, image)
            self.logger.debug("End inference")
            # TODO add meta
            resp_msg = {}
            self.logger.debug("Create response")
            resp_data = create_message(resp_msg, res_image)
            self.logger.debug("Send response")
            channel.basic_publish(
                exchange='',
                routing_key=self.output_queue_name,
                body=resp_data
            )


        try:
            self.logger.info("Loading model")
            self.model = dill.load(self.model_path)
        except Exception as e:
            self.logger.error("Failed to load model: " + str(e))

        try:
            self.logger.info("Connecting to queue")
            params = pika.URLParameters(self.queue_url)
            pika_connection = pika.BlockingConnection(params)
            channel = pika_connection.channel()
            channel.queue_declare(queue=self.input_queue_name)
            channel.queue_declare(queue=self.output_queue_name)
        except Exception as e:
            self.logger.error("Failed to connect " + str(e))

        try:
            self.logger.info("Starting inference")
            channel.basic_consume(
                queue=self.input_queue_name,
                on_message_callback=on_recv_callback,
                auto_ack=True
            )
            self.logger.info('[*] Waiting for messages')
            channel.start_consuming()
        except KeyboardInterrupt:
            self.logger.info("Exiting")
            channel.close()
            raise KeyboardInterrupt()
        except Exception as e:
            self.logger.error("Error occurred during inference: " + str(e))
            raise RuntimeError("Error occurred during inference") from e


def main() -> None:
    """ Main """

    # TODO think of a better way to load config
    load_dotenv(find_dotenv())
    config = {
        "input_queue_name": os.environ.get("INPUT_QUEUE_NAME"),
        "output_queue_name": os.environ.get("OUTPUT_QUEUE_NAME"),
        "queue_url": os.environ.get("QUEUE_URL"),
        "model": os.environ.get("MODEL"),
    }

    try:
        app = Application(config)
        app.run()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()