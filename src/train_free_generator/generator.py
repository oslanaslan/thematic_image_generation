import os

import torch
from PIL import Image
from diffusers_interpret import StableDiffusionImg2ImgPipelineExplainer
from PIL import Image
from diffusers import StableDiffusionImg2ImgPipeline


BASE_STRENGTH = 0.7
BASE_SCALE = 7.5
MODEL_NAME = "CompVis/stable-diffusion-v1-4"
SEED = 42


class TrainFreeGenerator:
    """
    Generate images without training
    """
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            MODEL_NAME, 
            use_auth_token=os.environ["DIFFUSERS_ACCESS_TOKEN"],
            revision='fp16',
            torch_dtype=torch.float16
        )
        pipe.to(self.device).enable_attention_slicing()
        self.explainer = StableDiffusionImg2ImgPipelineExplainer(pipe, gradient_checkpointing=True)
        self.generator = torch.Generator(self.device).manual_seed(SEED)

    def predict(self, prompt: str, image: Image) -> Image:
        """ Generate image """
        with torch.autocast('cuda'):
            output = self.explainer(
                prompt=prompt,
                init_image=image,
                strength=BASE_STRENGTH,
                guidance_scale=BASE_SCALE,
                generator=self.generator
            )

        return output.image
