from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_openai_client():
    with patch('app.main.get_openai_client') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_create_fable():
    with patch('app.main.create_fable_with_images') as mock:
        yield mock

def test_health_check_with_api_key():
    # given
    with patch('app.main.OPENAI_API_KEY', 'test-key'):
        # when
        response = client.get("/health")
        
        # then
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "openai_key_configured": True
        }

def test_health_check_without_api_key():
    # given
    with patch('app.main.OPENAI_API_KEY', ''):
        # when
        response = client.get("/health")
        
        # then
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "openai_key_configured": False
        }

def test_generate_fable_success(mock_openai_client, mock_create_fable):
    # given
    mock_result = {
        "fable_text": "Once upon a time...",
        "images": ["image1.jpg", "image2.jpg"],
        "prompts": ["prompt1", "prompt2"]
    }
    mock_create_fable.return_value = mock_result
    
    request_data = {
        "world_description": "magical forest",
        "main_character": "wise owl",
        "age": 7,
        "num_images": 2
    }
    
    with patch('app.main.OPENAI_API_KEY', 'test-key'):
        # when
        response = client.post("/generate_fable", json=request_data)
        
        # then
        assert response.status_code == 200
        assert response.json() == mock_result
        mock_create_fable.assert_called_once_with(
            world_description="magical forest",
            main_character="wise owl",
            age=7,
            num_images=2,
            client=mock_openai_client.return_value
        )

def test_generate_fable_without_api_key(mock_openai_client):
    # given
    request_data = {
        "world_description": "magical forest",
        "main_character": "wise owl",
        "age": 7
    }
    
    with patch('app.main.OPENAI_API_KEY', ''):
        # when
        response = client.post("/generate_fable", json=request_data)
        
        # then
        assert response.status_code == 500
        assert response.json() == {"detail": "OpenAI API key not configured"}
        mock_openai_client.assert_not_called()

def test_generate_fable_invalid_request():
    # given
    invalid_data = {
        "world_description": "magical forest",
        # missing required fields
    }
    
    # when
    response = client.post("/generate_fable", json=invalid_data)
    
    # then
    assert response.status_code == 422 