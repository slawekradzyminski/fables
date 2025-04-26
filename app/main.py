from fastapi import FastAPI, HTTPException
from app.services.fable_service import fable_generation_handler
from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from fastapi.middleware.cors import CORSMiddleware
from app.types.health import HealthResponse
from app.types.fable import FableRequest, FableResponse

settings = get_settings()
logger = get_logger(__name__)

# Initialize FastAPI app with custom Swagger UI configuration
app = FastAPI(
    title="Fable Generator API",
    description="Generate creative fables with AI-generated illustrations",
    version="1.0.0"
)

# Set up logging
setup_logging()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint that verifies API key is configured.

    Returns:
        HealthResponse: The health status and OpenAI API key configuration status
    """
    return HealthResponse(
        status="healthy"
    )

@app.post("/generate_fable", response_model=FableResponse, tags=["Fables"])
async def generate_fable(request: FableRequest):
    """
    Generate a fable with AI illustrations based on the provided parameters.
    
    Parameters:
    - world_description: The setting or world where the story takes place
    - main_character: The protagonist of the story
    - age: Target age of the reader (affects language complexity)
    - num_images: Number of illustrations to generate (default: 2)
    
    Returns:
        FableResponse: The generated fable with moral and illustrations
        
    Raises:
        HTTPException: If OpenAI API key is not configured or other errors occur
    """
    try:
        result = fable_generation_handler(
            world_description=request.world_description,
            main_character=request.main_character,
            age=request.age,
            num_images=request.num_images,
        )
        return result
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "invalid_api_key" in error_msg:
            raise HTTPException(status_code=401, detail=error_msg)
        logger.error(f"Error generating fable: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg) 