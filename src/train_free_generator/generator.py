import os
import logging
import torch
from  torch.cuda.amp import autocast
from PIL import Image
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
# from lavis.models import load_model_and_preprocess


logger = logging.getLogger("Generator-3")

BASE_STRENGTH = 0.35
BASE_SCALE = 10
MODEL_NAME = "stabilityai/stable-diffusion-2-1-base"
IMG_SIZE = (512, 512)
SEED = 42
IMG_DEVICE = 'cuda'
DESC_DEVICE = 'cpu'
STYLES_LST = [
    "painting in the style of Banksy of ",
    "painting in the style of Robert Delaunay of ",
    "painting in the style of Vincent Van Gogh of ",
    "painting in the style of Malevich of "
]


class ImgGenerator:
    """
    Generate images without training
    """
    def __init__(self) -> None:
        self.device = IMG_DEVICE
        scheduler = DPMSolverMultistepScheduler.from_pretrained(MODEL_NAME, subfolder="scheduler")
        self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            MODEL_NAME,
            use_auth_token=os.environ["DIFFUSERS_ACCESS_TOKEN"],
            scheduler=scheduler,
            safety_checker=None,
            torch_dtype=torch.float16,
            revision="fp16",
        )
        self.pipe.to(IMG_DEVICE)
        self.pipe.enable_attention_slicing()
        # pipe.enable_vae_slicing()
        # pipe.enable_xformers_memory_efficient_attention()
        self.pipe.enable_sequential_cpu_offload()

    def predict(self, prompt: str, image: Image) -> Image:
        """ Generate image """
        torch.cuda.empty_cache()

        with autocast(), torch.inference_mode():
            output = self.pipe(
                prompt=prompt, 
                image=image, 
                strength=0.25,
                # negative_prompt=negative_prompt,
                num_images_per_prompt=4,
                num_inference_steps=100,
                guidance_scale=10,
                generator=None,
            ).images

        return output.image


class DescGenerator:
    """
    Generate descritption for given image
    """
    def __init__(self) -> None:
        self.device = DESC_DEVICE
        model, vis_processors, _ = load_model_and_preprocess(
            name="blip_caption",
            model_type="large_coco",
            is_eval=True,
            device=self.device,
        )
        self.model = model
        self.vis_processors = vis_processors

    def predict(self, image: Image) -> str:
        image = self.vis_processors["eval"](image).unsqueeze(0).to(self.device)
        desc = self.model.generate({"image": image}, use_nucleus_sampling=True, num_captions=1)[0]

        return desc


class TrainFreeGenerator:
    """
    Run pipeline
    """
    def __init__(self) -> None:
        self.descriptor = DescGenerator()
        self.generator = ImgGenerator()

    def predict(self, msg: str, image: Image) -> Image:
        img_desc = self.descriptor.predict(image)
        res_imgs_lst = []

        for style in STYLES_LST:
            prompt = ' '.join([style, img_desc])
            res_imgs_lst.append(self.generator.predict(prompt, image))

        return res_imgs_lst
