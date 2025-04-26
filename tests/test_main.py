import pytest
import pytest_asyncio # Import explicitly for the fixture decorator
from httpx import AsyncClient, ASGITransport # Import ASGITransport
from app.main import app  # Import your FastAPI app instance
from app.types.fable import FableRequest, FableResponse, IllustrationResponse # Import IllustrationResponse
from app.types.health import HealthResponse
from unittest.mock import patch

# Using pytest-asyncio for async tests
pytestmark = pytest.mark.asyncio

# Fixture for the async test client
@pytest_asyncio.fixture(scope="module")
async def client():
    # Use ASGITransport to wrap the FastAPI app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

async def test_health_check(client: AsyncClient):
    # when
    response = await client.get("/health")
    
    # then
    assert response.status_code == 200
    health_response = HealthResponse(**response.json())
    assert health_response.status == "healthy"

@patch("app.main.fable_generation_handler")
async def test_generate_fable_success(mock_handler, client: AsyncClient):
    # given
    request_data = FableRequest(
        world_description="A magical forest",
        main_character="A brave squirrel",
        age=8,
        num_images=1
    )
    mock_response = FableResponse(
        fable="Once upon a time...", # Changed title to fable
        moral="Bravery comes in all sizes.",
        illustrations=[
            IllustrationResponse(prompt="A brave squirrel facing a challenge", image="http://example.com/image1.png")
        ]
    )
    mock_handler.return_value = mock_response

    # when
    response = await client.post("/generate_fable", json=request_data.model_dump())

    # then
    assert response.status_code == 200
    fable_response = FableResponse(**response.json())
    assert fable_response == mock_response
    mock_handler.assert_called_once_with(
        world_description="A magical forest",
        main_character="A brave squirrel",
        age=8,
        num_images=1
    )

@patch("app.main.fable_generation_handler")
async def test_generate_fable_api_key_error(mock_handler, client: AsyncClient):
    # given
    request_data = FableRequest(
        world_description="A haunted castle",
        main_character="A timid ghost",
        age=10,
        num_images=1
    )
    mock_handler.side_effect = Exception("Invalid API key provided.")

    # when
    response = await client.post("/generate_fable", json=request_data.model_dump())

    # then
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]

@patch("app.main.fable_generation_handler")
async def test_generate_fable_generic_error(mock_handler, client: AsyncClient):
    # given
    request_data = FableRequest(
        world_description="An underwater city",
        main_character="A curious octopus",
        age=6,
        num_images=1
    )
    mock_handler.side_effect = Exception("Something went wrong during generation.")

    # when
    response = await client.post("/generate_fable", json=request_data.model_dump())

    # then
    assert response.status_code == 500
    assert "Something went wrong" in response.json()["detail"] 