import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv, find_dotenv

from generator import ImgGenerator


# IMG_SIZE = (448, 448)
IMG_SIZE = (256, 256)

def run_test_inf():
    prompt = 'painting in the style of Banksy on the wall photo a very cute furry teddy bear with a blue nose'
    url = "https://i.pinimg.com/736x/13/7c/50/137c50f6cffb025a6cf3d634e5a15834.jpg"
    response = requests.get(url)
    init_image = Image.open(BytesIO(response.content)).convert("RGB")
    init_image = init_image.resize(IMG_SIZE)

    model = ImgGenerator()
    # res_img = model.predict(prompt, init_image)

    return res_img


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    res_img = run_test_inf()
    res_img.show()
