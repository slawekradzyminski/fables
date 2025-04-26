from typing import Dict, Any
import base64
from io import BytesIO
from datetime import datetime
import os

from app.services.openai_client import generate_fable_and_prompts, generate_illustration_image
from app.core.logging import get_logger

logger = get_logger(__name__)

def fable_generation_handler(world_description: str, main_character: str, age: int, num_images: int = 2) -> Dict[str, Any]:
    """
    Main service function that:
    1) Generate fable, moral and prompts for image generation using GPT-4.1
    2) Generate images using the optimized prompts, using previous image as reference for style consistency
    """

    # 1) Generate the fable and prompts
    open_ai_response = generate_fable_and_prompts(
        world_description=world_description,
        main_character=main_character,
        age=age,
        num_images=num_images,
    )
    logger.info(f"Generated fable and prompts: {open_ai_response}")

    # 2) Generate images using the optimized prompts, using previous image as reference for style consistency
    illustrations = []
    prev_image_b64 = None
    os.makedirs("output_folder", exist_ok=True)
    
    for idx, prompt in enumerate(open_ai_response.image_prompts):
        if idx == 0:
            image_b64 = generate_illustration_image(prompt)
        else:
            image_bytes = base64.b64decode(prev_image_b64)
            image_file = BytesIO(image_bytes)
            image_file.name = f"image{idx-1}.png"
            image_b64 = generate_illustration_image(prompt, reference_image=image_file)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        save_base64_image(image_b64, f"output_folder/image{idx}_{timestamp}.png")
        illustrations.append({"prompt": prompt, "image": image_b64})
        prev_image_b64 = image_b64

    return {
        "fable": open_ai_response.fable,
        "moral": open_ai_response.moral,
        "illustrations": illustrations
    }

def save_base64_image(base64_str, filename):
    with open(filename, "wb") as f:
        f.write(base64.b64decode(base64_str))
    logger.info(f"Saved image to {filename}")