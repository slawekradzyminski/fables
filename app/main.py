from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from typing import List
from app.fable_service import create_fable_with_images
from app.config import OPENAI_API_KEY
from app.openai_client import get_openai_client

app = FastAPI(
    title="Fable Generator API",
    description="API to generate short fables with consistent storybook-style illustrations.",
    version="1.0.0"
)

class FableRequest(BaseModel):
    world_description: str
    main_character: str
    age: int
    num_images: int = 2

class FableResponse(BaseModel):
    fable_text: str
    images: List[str]
    prompts: List[str]

class HealthResponse(BaseModel):
    status: str
    openai_key_configured: bool

@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Check if the application is running and OpenAI API key is configured.
    """
    return HealthResponse(
        status="ok",
        openai_key_configured=bool(OPENAI_API_KEY and OPENAI_API_KEY.strip())
    )

@app.post("/generate_fable", response_model=FableResponse, tags=["Fables"])
def generate_fable(request: FableRequest = Body(...)):
    """
    Generate a short fable plus corresponding illustrations.
    Returns:
    - The text of the fable
    - A list of image URLs
    - The DALL-E prompts used to generate each image
    """
    if not OPENAI_API_KEY or not OPENAI_API_KEY.strip():
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
    client = get_openai_client()
    result = create_fable_with_images(
        world_description=request.world_description,
        main_character=request.main_character,
        age=request.age,
        num_images=request.num_images,
        client=client
    )
    return FableResponse(**result) 