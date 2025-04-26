from jinja2 import Template
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text()

def render_user_prompt(age: int, world_description: str, main_character: str, num_images: int) -> str:
    prompt_template = _load_prompt("user.txt")
    return Template(prompt_template).render(
        age=age,
        world_description=world_description,
        main_character=main_character,
        num_images=num_images
    )
