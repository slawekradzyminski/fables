from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.fable_service import create_fable_with_images
from app.config import OPENAI_API_KEY
from app.openai_client import get_openai_client
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Fable Generator API",
    description="API to generate short fables with consistent storybook-style illustrations.",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class FableRequest(BaseModel):
    world_description: str = Field(
        description="Description of the world where the story takes place",
        example="A whimsical steampunk city in the clouds where buildings float on giant copper balloons and mechanical birds deliver messages between towers"
    )
    main_character: str = Field(
        description="Description of the main character of the story",
        example="a young inventor mouse named Gizmo"
    )
    age: int = Field(
        description="Target age of the audience",
        example=8,
        ge=1,
        le=12
    )
    num_images: int = Field(
        default=2,
        description="Number of illustrations to generate",
        example=2,
        ge=1,
        le=4
    )

    class Config:
        json_schema_extra = {
            "example": {
                "world_description": "A whimsical steampunk city in the clouds where buildings float on giant copper balloons and mechanical birds deliver messages between towers",
                "main_character": "a young inventor mouse named Gizmo",
                "age": 8,
                "num_images": 2
            }
        }

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