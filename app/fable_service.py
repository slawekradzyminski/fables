from app.openai_client import generate_fable_and_prompts, generate_illustration_images, get_openai_client
from openai import OpenAI

def create_fable_with_images(world_description: str, main_character: str, age: int, num_images: int, client: OpenAI | None = None) -> dict:
    """
    High-level function orchestrating the fable creation process:
    1) Generate fable text and optimized DALL-E prompts using GPT-4o
    2) Generate images using the optimized prompts
    3) Return a dict with the fable text and list of image URLs
    """
    client = client or get_openai_client()

    # 1) Generate the fable and prompts
    fable_text, image_prompts = generate_fable_and_prompts(
        world_description=world_description,
        main_character=main_character,
        age=age,
        num_images=num_images,
        client=client
    )

    # 2) Generate images using the optimized prompts
    image_urls = generate_illustration_images(image_prompts, client=client)

    # 3) Compile the result
    result = {
        "fable_text": fable_text,
        "images": image_urls,
        "prompts": image_prompts  # Include prompts in response for reference
    }
    return result 