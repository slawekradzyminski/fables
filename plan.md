Below is a comprehensive, step-by-step implementation plan to build a Fable Generation Service (fables + illustrations) using Python and OpenAI’s endpoints. This plan is designed to be followed by a “less capable AI agent” or junior developer, so it is extremely explicit about each step and contains minimal assumptions about the user’s prior knowledge. The final product will be a FastAPI-based web service with endpoints for creating a fable (including images) and for retrieving them, complete with Swagger documentation, tests, and environment variable handling.

1. Project Overview
We want a backend service that:

Accepts a JSON request specifying:

A short prompt describing the “world” or “characters.”

The age of the reader (for reading-level adjustments).

(Optional) The number of illustrations or key scenes to illustrate (≥2).

Generates:

A short fable (text) appropriate for the specified age level, with a moral at the end.

Multiple illustrations matching the fable, all in a consistent storybook style.

Returns a structured response containing the generated text plus URLs or data for the generated images.

Must be a fully automated pipeline, no manual intervention required.

Must run in a secure environment with an .env file storing the OpenAI API key.

Includes automated tests (pytest) and auto-generated Swagger docs from FastAPI.

2. Technical Stack
2.1 Language & Frameworks
Python 3.9+ (some features require at least 3.7+, but 3.9 or 3.10 is recommended).

FastAPI for building the REST API.

uvicorn as the ASGI server to run the FastAPI app.

python-dotenv for environment variables.

openai Python client library for calling OpenAI’s text and image endpoints.

2.2 Additional Tools
pytest for automated testing.

requests or httpx (already included in openai library, but may want for any additional calls).

Pydantic (built into FastAPI) for request/response models.

Swagger auto-generation is built into FastAPI (via /docs endpoint).

Git for version control (optional, but strongly recommended).

3. Setting Up the Environment
Create a Project Folder

For example: mkdir fable-generator && cd fable-generator

Initialize a Virtual Environment

bash
Copy
Edit
python -m venv venv
source venv/bin/activate   # On Unix-like systems
# or
.\venv\Scripts\activate    # On Windows
Create and populate requirements.txt

ini
Copy
Edit
fastapi==0.95.2
uvicorn==0.22.0
python-dotenv==1.0.0
openai==0.27.0
pytest==7.4.0
(These version numbers are examples. Adjust as needed, or pin them to the latest stable releases.)

Install Dependencies

bash
Copy
Edit
pip install -r requirements.txt
Create a .env file

In the root of your project, create a file named .env:

bash
Copy
Edit
touch .env
Inside .env, store your OpenAI API key, for example:

env
Copy
Edit
OPENAI_API_KEY="sk-XXXXXX..."
Important: Add .env to .gitignore to avoid committing secrets to version control.

Project Structure
For clarity, here’s a suggested folder layout:

bash
Copy
Edit
fable-generator/
├─ app/
│  ├─ main.py             # FastAPI entry point
│  ├─ config.py           # Environment variable loading
│  ├─ models.py           # Pydantic models
│  ├─ openai_client.py    # Utility for calling OpenAI APIs
│  ├─ fable_service.py    # Core logic for text + image generation
│  └─ __init__.py
├─ tests/
│  ├─ test_fable.py       # Pytest tests for the Fable generation
│  └─ test_api.py         # Pytest tests for FastAPI endpoints
├─ .env
├─ requirements.txt
└─ README.md
4. Loading Environment Variables and Configuration
In config.py, load the .env using python-dotenv:

python
Copy
Edit
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in .env file")
This ensures any file importing config.py has access to OPENAI_API_KEY safely.

5. Creating the OpenAI Client (Text + Image)
5.1 openai_client.py
python
Copy
Edit
import openai
from app.config import OPENAI_API_KEY

# Initialize OpenAI with the API key
openai.api_key = OPENAI_API_KEY

def generate_fable_text(world_description: str, main_character: str, age: int) -> str:
    """
    Calls OpenAI's GPT endpoint to generate a short fable for children of a given age.
    Returns the fable text (including a moral).
    """
    # Construct a system or developer message to guide the style
    # We'll use ChatCompletion with GPT-4 or GPT-3.5
    messages = [
        {
            "role": "system",
            "content": (
                "You are a creative story-teller specializing in short children's fables. "
                "Keep the language simple and appropriate for the indicated age. "
                "Always end with a moral, labeled clearly as 'Moral:'."
            )
        },
        {
            "role": "user",
            "content": f"""
            Write a short fable for a child of age {age} about:
            - World Description: {world_description}
            - Main Character: {main_character}
            Make it whimsical but also easy to read. 
            """
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4"
        messages=messages,
        temperature=0.7,
        max_tokens=300,
    )

    # Extract the text from the response
    fable = response.choices[0].message["content"].strip()
    return fable


def generate_illustration_images(prompt_list: list) -> list:
    """
    Calls OpenAI's DALL·E (or DALL·E 3) image generation endpoint for each prompt in prompt_list.
    Returns a list of image URLs (or base64 if needed).
    Each prompt in prompt_list is a string describing the scene to illustrate.
    """
    image_urls = []
    for prompt in prompt_list:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        # Extract URL(s) from response; n=1 so we'll have just one
        image_url = response["data"][0]["url"]
        image_urls.append(image_url)
    return image_urls
Notes:

temperature=0.7 for mild creativity.

max_tokens=300 helps keep the fable short.

For advanced usage, you might adapt the prompt or system messages further, or do multi-step generation (outline first, then final story).

DALL·E 3 uses the same openai.Image.create call, but you must have access to that feature in your account.

The exact size can be adjusted based on your design needs.

The function returns a list of public image URLs that OpenAI provides for a short time (usually a few hours). If you want permanent storage, you must download and host them yourself.

6. Core Service Logic: Fable + Illustrations
6.1 fable_service.py
python
Copy
Edit
from app.openai_client import generate_fable_text, generate_illustration_images

def create_fable_with_images(world_description: str, main_character: str, age: int, num_images: int) -> dict:
    """
    High-level function orchestrating the entire fable creation process:
    1) Generate fable text
    2) Identify or define 'scene prompts' for each illustration
    3) Generate images for each scene
    4) Return a dict with the fable text and list of image URLs
    """
    # 1) Generate the fable
    fable_text = generate_fable_text(world_description, main_character, age)

    # 2) Create prompts for each illustration
    # For simplicity, we just do generic scene prompts. 
    # In practice, you might parse the story for key scenes or let the user specify them.
    # We'll highlight a short approach:
    scene_prompts = []
    for i in range(num_images):
        scene_prompts.append(
            f"Illustration for a children's fable. "
            f"Show {main_character} in the {world_description}, scene {i+1}."
            "Use a colorful storybook style."
        )

    # 3) Generate images
    image_urls = generate_illustration_images(scene_prompts)

    # 4) Compile the result
    result = {
        "fable_text": fable_text,
        "images": image_urls
    }
    return result
Notes:
This method could be more sophisticated by performing text analysis on fable_text to find important scenes. However, for now, we generate num_images prompts with consistent language to keep style uniform.

The phrase "Use a colorful storybook style." guides the model to produce cartoonish/children’s illustration style images. You can refine that prompt as needed.

7. FastAPI Application
7.1 main.py
python
Copy
Edit
from fastapi import FastAPI, Body
from pydantic import BaseModel
from app.fable_service import create_fable_with_images

app = FastAPI(
    title="Fable Generator API",
    description="API to generate short fables with consistent storybook-style illustrations.",
    version="1.0.0"
)

class FableRequest(BaseModel):
    world_description: str
    main_character: str
    age: int
    num_images: int = 2  # default 2 if not specified

class FableResponse(BaseModel):
    fable_text: str
    images: list[str]

@app.post("/generate_fable", response_model=FableResponse, tags=["Fables"])
def generate_fable(request: FableRequest = Body(...)):
    """
    Generate a short fable plus corresponding illustrations.
    Returns the text of the fable and a list of image URLs.
    """
    result = create_fable_with_images(
        world_description=request.world_description,
        main_character=request.main_character,
        age=request.age,
        num_images=request.num_images
    )
    return FableResponse(**result)

Explanation:
Pydantic is used to define request/response models.

We specify a default num_images=2.

The endpoint is /generate_fable with POST, returning a structured JSON containing fable_text and images.

FastAPI auto-generates Swagger at /docs and ReDoc at /redoc.

7.2 Running the App
In your command line, from the project root:

bash
Copy
Edit
uvicorn app.main:app --reload
Visit http://127.0.0.1:8000/docs to see the Swagger interface.

8. Testing with pytest
Create tests in tests/test_fable.py:

python
Copy
Edit
import pytest
from app.fable_service import create_fable_with_images

@pytest.mark.integration
def test_create_fable_with_images():
    # Basic integration test that calls the entire pipeline
    world_description = "enchanted forest"
    main_character = "Timmy the Tortoise"
    age = 6
    num_images = 2

    result = create_fable_with_images(world_description, main_character, age, num_images)

    # Check that fable_text is non-empty
    assert "Moral:" in result["fable_text"], "Should contain a moral"
    assert len(result["images"]) == num_images, f"Expected {num_images} images"

    # Possibly check that each image is a valid URL
    for url in result["images"]:
        assert url.startswith("http"), f"Expected a URL, got {url}"
Create tests in tests/test_api.py:

python
Copy
Edit
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_fable_endpoint():
    payload = {
        "world_description": "magical pond",
        "main_character": "Lucy the Duck",
        "age": 5,
        "num_images": 2
    }
    response = client.post("/generate_fable", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "fable_text" in data
    assert len(data["images"]) == 2
Running Tests

bash
Copy
Edit
pytest
The test_fable.py uses a real integration test calling OpenAI. This will consume tokens and require network access.

The test_api.py uses FastAPI’s TestClient to check the endpoint. It also calls the real generation function, so it’s also an integration test. If you want purely offline unit tests, you’d need to mock the OpenAI calls.

9. Deployment Considerations
Production vs Development

In production, remove --reload from the uvicorn command.

Consider using a production server like gunicorn with uvicorn workers.

Token Usage and Cost

Monitor usage on your OpenAI account. Generating many images or large fables can become costly.

Implement caching if repeated requests for the same scenario are common.

Security

Always keep your .env out of version control.

Rate-limit or secure the endpoint if you want to prevent malicious usage that could rack up costs.

Content Moderation

If your front-end allows arbitrary user prompts, consider hooking into OpenAI’s Moderation API to check the user’s request for disallowed content before generating text or images.

Image Hosting

By default, the openai.Image.create returns temporary hosted URLs that expire after some hours. If you need permanent hosting, you must download these images (e.g., using requests.get(url).content) and store them in a cloud bucket (e.g., AWS S3 or local storage).

Advanced Consistency

If you need truly identical characters across all images, consider a more advanced approach like [fine-tuning or DreamBooth with Stable Diffusion], or feeding a reference image to DALL·E or MidJourney. This is outside the scope of the basic example but is important for very strict consistency.

10. Final Summary of Steps
Initialize Project:

mkdir fable-generator && cd fable-generator

python -m venv venv && source venv/bin/activate

Create requirements.txt and install dependencies.

Create .env with your OPENAI_API_KEY.

Directory Setup:

Create app/ folder with the following modules:

config.py, openai_client.py, fable_service.py, main.py, models.py, __init__.py

Create tests/ folder with test_fable.py and test_api.py.

Implement:

config.py loads environment variables (OPENAI_API_KEY).

openai_client.py has generate_fable_text + generate_illustration_images.

fable_service.py orchestrates the combined flow.

main.py defines FastAPI routes and Pydantic models.

Test:

pytest to verify everything works.

Run & Check:

uvicorn app.main:app --reload

Check http://127.0.0.1:8000/docs for Swagger.

Send a POST request to /generate_fable.

Refine:

Adjust prompt engineering, style instructions, and test coverage as needed.

With these steps completed, you will have a working, fully automated pipeline that generates short, age-appropriate fables along with consistent, storybook-style images—exposed via a clean FastAPI service with built-in Swagger documentation, using your .env file to keep secrets secure, and tested using pytest.