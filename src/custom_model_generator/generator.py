import os

import torch
import dill
from PIL import Image
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from torch.cuda.amp import autocast
from PIL import Image
from basicsr.archs.rrdbnet_arch import RRDBNet

from realesrgan import RealESRGANer
from GFPGAN.gfpgan import GFPGANer


CUSTOM_MODEL_PATH = os.path.join("..", "..", "models")
PROMPT_GEN_PATH = os.path.join(CUSTOM_MODEL_PATH, "prompt_gen.dll")
GFPGAN_PATH = os.path.join(CUSTOM_MODEL_PATH, "GFPGANv1.4.pth")
ESRGAN_PATH = os.path.join(CUSTOM_MODEL_PATH, "RealESRGAN_x2plus.pth")
PROMPT_MODS_CNT = 5
BASE_STRENGTH = 0.7
BASE_SCALE = 10
BASE_NUM_STEPS = 50
IMG_SIZE = (512, 512)
SEED = 42
IMG_DEVICE = 'cuda'
DESC_DEVICE = 'cpu'


class ImageGenerator:
    """
    Generate images with custom pretrained model
    """
    def __init__(self, model_name) -> None:
        path_to_model = os.path.join(CUSTOM_MODEL_PATH, model_name)
        scheduler = DPMSolverMultistepScheduler.from_pretrained(path_to_model, subfolder="scheduler")
        self.pipe = StableDiffusionPipeline.from_pretrained(
            path_to_model,
            scheduler=scheduler,
            safety_checker=None,
            torch_dtype=torch.float16,
            solver_order=2,
        )
        self.pipe.to(IMG_DEVICE)
        self.pipe.enable_attention_slicing()
        # pipe.enable_vae_slicing()
        # pipe.enable_xformers_memory_efficient_attention()
        self.pipe.enable_sequential_cpu_offload()

    def predict(self, prompt: str) -> Image:
        with autocast(IMG_DEVICE), torch.inference_mode():
            output = self.pipe(
                prompt,
                height=IMG_SIZE[0],
                width=IMG_SIZE[1],
                negative_prompt="",
                num_images_per_prompt=1,
                num_inference_steps=BASE_NUM_STEPS,
                guidance_scale=BASE_SCALE,
                generator=None,
            ).images[0]

        return output


class PromptGenerator:
    """
    Generate prompt for model
    """
    def __init__(self) -> None:
        with open(PROMPT_GEN_PATH, 'r') as f:
            self.model = dill.load(f)
    
    def predict(self, prompt: str) -> Image:
        prompt_mods_lst = self.model.predict(prompt, cnt=PROMPT_MODS_CNT)
        prompt_mods_lst = [prompt] + prompt_mods_lst
        prompt = " ".join(prompt_mods_lst)

        return prompt


class Postprocessor:
    """
    
    """
    def __init__(self) -> None:
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
        bg_upsampler = RealESRGANer(
            scale=2,
            model_path=ESRGAN_PATH,
            model=model,
            tile=400,
            tile_pad=10,
            pre_pad=0,
            half=True
        )
        self.restorer = GFPGANer(
            model_path=GFPGAN_PATH,
            upscale=2,
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=bg_upsampler
        )

    def predict(self, image: Image) -> Image:
        _, _, restored_img = self.restorer.enhance(
            image,
            has_aligned=True,
            only_center_face=True,
            paste_back=True,
            weight=0.5
        )

        return restored_img


class CustomModelGenerator:
    """
    Run generation pipeline
    """
    def __init__(self, model_name: str) -> None:
        self.image_generator = ImageGenerator(model_name)
        self.prompt_generator = PromptGenerator()
        self.postprocessor = Postprocessor()

    def predict(self, prompt: str, image: Image = None) -> Image:
        prompt = self.prompt_generator(prompt)
        image = self.image_generator(prompt)
        image = self.postprocessor(image)

        return image
