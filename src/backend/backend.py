"""
Thematic Image Generation backend app

"""
import os
import io
import sys
import json
import struct
from typing import Dict, Tuple

import pika
import dill
import uuid
from PIL import Image
from dotenv import find_dotenv, load_dotenv

# sys.path.insert(1, '../train_free_generator')

from .logger import GrafanaLogger as Logger
from .saver import Drive
from ..train_free_generator.generator import TrainFreeGenerator, ImgGenerator
# from ..model.echo_model import EchoModel

# TEST PROMPT
DEFAULT_PROMPT = "The streets of old cairo at the time of the pharaohs, intricate, elegant, volumetric lighting, digital painting, highly detailed, artstation, sharp focus, illustration, concept art, ruan jia, steve mccurry"


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
        self.saver = Drive()
        self.model = None
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

            if len(message) != struct.calcsize("!cLL") + len_meta + len_image:
                self.logger.error("Wrong message structure in message")

            metab = message[9:9 + len_meta]
            image = message[-len_image:]
            meta = json.loads(metab.decode("utf-8"))

            return meta, image


        def on_recv_callback(ch, method, properties, body: bytes) -> None:
            """ Inference callback"""

            msg_uid = uuid.uuid4()
            meta, image = decode_message(body)
            self.logger.info(f"[x] Received message {msg_uid}: {meta}")
            self.saver.save(f"{msg_uid}_input", str(meta), image)
            image = Image.open(io.BytesIO(image))
            self.logger.debug("Start inference")

            if 'caption' in meta:
                prompt = meta['caption']
            else:
                # TODO: think of default prompt
                prompt = DEFAULT_PROMPT

            res_images_lst = self.model.predict(prompt, image)
            self.logger.debug("End inference")

            for i, res_image in enumerate(res_images_lst):
                with io.BytesIO() as f:
                    res_image.save(f, format="PNG")
                    res_image = f.getvalue()

                # TODO add meta
                res_meta = {}
                res_meta["chat"] = meta["chat"]
                self.saver.save(f"{msg_uid}_output_{i}", str(meta), res_image)
                self.logger.debug("Create response")
                resp_data = create_message(meta, res_image)
                self.logger.debug(f"Send response with message {meta}")
                channel.basic_publish(
                    exchange='',
                    routing_key=self.output_queue_name,
                    body=resp_data
                )
            
        # Load model

        try:
            self.logger.info("Loading model")
            self.model = TrainFreeGenerator()
            # self.model = EchoModel()
            # self.model = ImgGenerator()
        except Exception as e:
            self.logger.error("Failed to load model", e)
            sys.exit(0)

        try:
            self.logger.info("Connecting to queue")
            params = pika.URLParameters(self.queue_url)
            pika_connection = pika.BlockingConnection(params)
            channel = pika_connection.channel()
            channel.queue_declare(queue=self.input_queue_name)
            channel.queue_declare(queue=self.output_queue_name)
        except Exception as e:
            self.logger.error("Failed to connect", e)

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
            self.logger.error("Error occurred during inference", e)
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
