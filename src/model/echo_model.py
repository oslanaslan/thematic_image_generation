import io
import time

from PIL import Image


class EchoModel:

    def __init__(self) -> None:
        pass

    def predict(self, prompt: str, image: Image) -> Image:
        # image = Image.open(io.BytesIO(image))
        time.sleep(60)
        image = Image.open("data/test_imgs/test_out_v2.jpg")
        return image
