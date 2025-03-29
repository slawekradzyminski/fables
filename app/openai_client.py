from openai import OpenAI
import requests
import tempfile
from pathlib import Path
from app.config import OPENAI_API_KEY
from typing import Tuple, List

def get_openai_client() -> OpenAI:
    """Get an instance of the OpenAI client."""
    return OpenAI()

def generate_fable_and_prompts(world_description: str, main_character: str, age: int, num_images: int = 2, client: OpenAI = None) -> Tuple[str, List[str]]:
    """
    Uses GPT-4O to generate both a fable and optimized DALL-E prompts for key scenes.
    Returns the fable text and a list of image prompts.
    """
    if client is None:
        client = get_openai_client()

    messages = [
        {
            "role": "system",
            "content": (
                "You are a creative story-teller specializing in short children's fables. "
                "You will write a fable and create prompts for DALL-E to illustrate key scenes. "
                "Keep the language simple and appropriate for the indicated age. "
                "Always end with a moral, labeled clearly as 'Moral:'. "
                "After the story, provide exactly the requested number of DALL-E prompts, "
                "each starting with 'DALLE_PROMPT:'. Make these prompts highly specific and "
                "optimized for DALL-E, focusing on key scenes from the story."
            )
        },
        {
            "role": "user",
            "content": f"""
            Write a short fable for a child of age {age} about:
            - World Description: {world_description}
            - Main Character: {main_character}
            
            Then provide {num_images} DALL-E prompts to illustrate key scenes.
            Make the prompts specific and detailed, optimized for DALL-E.
            Each prompt should start with 'DALLE_PROMPT:' on a new line.
            """
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=1000,
    )

    # Extract the content
    full_response = response.choices[0].message.content.strip()
    
    # Split into fable and prompts
    parts = full_response.split("DALLE_PROMPT:")
    fable = parts[0].strip()
    
    # Extract prompts (skip empty strings and strip whitespace)
    prompts = [p.strip() for p in parts[1:] if p.strip()]
    
    return fable, prompts

def _download_image(url: str) -> bytes:
    """Download image from URL and return as bytes."""
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def _save_temp_png(image_data: bytes) -> str:
    """Save image bytes to a temporary PNG file and return the path."""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp.write(image_data)
        return tmp.name

def generate_illustration_images(prompts: List[str], client: OpenAI = None) -> List[str]:
    """
    Calls DALL-E to generate images for each prompt.
    Uses standard quality settings for cost efficiency.
    Returns a list of image URLs.
    """
    if client is None:
        client = get_openai_client()

    image_urls = []
    for prompt in prompts:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard"
        )
        image_url = response.data[0].url
        image_urls.append(image_url)
    return image_urls 