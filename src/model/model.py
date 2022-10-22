import os
import warnings

import torch
import requests
from PIL import Image
from io import BytesIO
from diffusers import StableDiffusionPipeline
from dotenv import load_dotenv
from tqdm.notebook import tqdm


class Model:

    def __init__(self) -> None:

        def null_safety(images, **kwargs):
            return images, False

        self.model = StableDiffusionPipeline.from_pretrained(
            "CompVis/stable-diffusion-v1-4",
            use_auth_token=os.environ["DIFFUSERS_ACCESS_TOKEN"],
            # revision="fp16", 
            # torch_dtype=torch.float16,
        )
        self.model.to('cuda')
        self.model.safety_checker = null_safety
        self.generator = torch.Generator("cuda").manual_seed(1024)
    

    def predict(self, prompt: str, image: Image) -> Image:
        image = self.model(
            prompt,
            guidance_scale=7.5,
            num_inference_steps=100,
            generator=self.generator
        )
        image = image["sample"][0]

        return image
