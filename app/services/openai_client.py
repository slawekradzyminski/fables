from openai import OpenAI
from pathlib import Path
from jinja2 import Template
from typing import Tuple, List, Optional, IO
import base64
from io import BytesIO

from app.core.config import get_settings
from app.core.logging import get_logger
from app.prompts.user_prompt import render_user_prompt
from app.types.openai_response import OpenAiResponse

settings = get_settings()
logger = get_logger(__name__)
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

def _load_prompt(name: str) -> str:
    """Load a prompt from the prompts directory."""
    return (PROMPTS_DIR / name).read_text()

def get_openai_client() -> OpenAI:
    """Get an instance of the OpenAI client."""
    if not settings.openai_api_key:
        return None
        
    return OpenAI(api_key=settings.openai_api_key)

def generate_fable_and_prompts(world_description: str, main_character: str, age: int, num_images: int = 2) -> OpenAiResponse:
    """
    Uses GPT-4o to generate both a fable and optimized DALL-E prompts for key scenes.
    Returns the fable text and a list of image prompts.
    """
    client = get_openai_client()
    messages = [
        {"role": "system", "content": _load_prompt("system.txt")},
        {"role": "user", "content": render_user_prompt(age, world_description, main_character, num_images)}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.8,
        max_tokens=1000,
        response_format={"type": "json_object"}
    )

    full_response = response.choices[0].message.content.strip()
    return OpenAiResponse.model_validate_json(full_response)


def generate_illustration_image(prompt: str, reference_image: Optional[IO] = None) -> str:
    """
    Calls GPT Image (gpt-image-1) to generate an image for the given prompt.
    If reference_image is provided, uses it as a style reference (edit endpoint).
    Returns a base64-encoded PNG image string.
    """
    client = get_openai_client()
    if reference_image is not None:
        image_file = BytesIO(reference_image.read())
        image_file.name = f"image.png"
        response = client.images.edit(
            model="gpt-image-1",
            image=image_file,
            prompt=prompt,
            size="1024x1024"
        )
    else:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
    return response.data[0].b64_json 