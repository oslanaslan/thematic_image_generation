import os
import logging
import torch
from PIL import Image
from diffusers_interpret import StableDiffusionImg2ImgPipelineExplainer
from PIL import Image
from diffusers import StableDiffusionImg2ImgPipeline
from lavis.models import load_model_and_preprocess

logger = logging.getLogger("Generator-3")

BASE_STRENGTH = 0.7
BASE_SCALE = 7.5
MODEL_NAME = "CompVis/stable-diffusion-v1-4"
IMG_SIZE = (448, 448)
SEED = 42
IMG_DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
IMG_DEVICE = 'cuda'
DESC_DEVICE = 'cuda'
STYLES_LST = [
    "painting in the style of Banksy of",
    "painting in the style of Robert Delaunay of",
    "painting in the style of Vincent Van Gogh of",
    "painting in the style of Malevich of"
]

# if torch.cude.is_available():
#     IMAGE_GEN_DEVICE = "cuda"
# else:
#     raise ValueError("cuda is not available")



class ImgGenerator:
    """
    Generate images without training
    """
    def __init__(self) -> None:
        self.device = IMG_DEVICE
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            MODEL_NAME,
            use_auth_token=os.environ["DIFFUSERS_ACCESS_TOKEN"],
            revision='fp16' if self.device == 'cuda' else None,
            torch_dtype=torch.float16 if self.device == 'cuda' else None,
        )
        pipe.to(self.device).enable_attention_slicing()
        self.explainer = StableDiffusionImg2ImgPipelineExplainer(pipe, gradient_checkpointing=True)
        self.generator = torch.Generator(self.device).manual_seed(SEED)

    def predict(self, prompt: str, image: Image) -> Image:
        """ Generate image """
        with torch.autocast('cuda'):
            print("Start generation")
            print("Device", self.device)
            output = self.explainer(
                prompt=prompt,
                init_image=image.resize(IMG_SIZE),
                strength=BASE_STRENGTH,
                guidance_scale=BASE_SCALE,
                generator=self.generator,
                get_images_for_all_inference_steps=False
            )
            print("Returned from generation")

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
