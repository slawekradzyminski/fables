from unittest.mock import patch, MagicMock
import pytest
from app.fable_service import create_fable_with_images

@pytest.fixture(autouse=True)
def mock_settings_env():
    """Mock environment settings for all tests"""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        yield

@pytest.fixture
def mock_openai_client():
    return MagicMock()

@pytest.fixture
def mock_generate_fable():
    with patch('app.fable_service.generate_fable_and_prompts') as mock:
        yield mock

@pytest.fixture
def mock_generate_images():
    with patch('app.fable_service.generate_illustration_images') as mock:
        yield mock

def test_create_fable_with_images_success(mock_openai_client, mock_generate_fable, mock_generate_images):
    # given
    fable_text = "Once upon a time..."
    image_prompts = ["prompt1", "prompt2"]
    image_urls = ["image1.jpg", "image2.jpg"]
    
    mock_generate_fable.return_value = (fable_text, image_prompts)
    mock_generate_images.return_value = image_urls
    
    # when
    result = create_fable_with_images(
        world_description="magical forest",
        main_character="wise owl",
        age=7,
        num_images=2,
        client=mock_openai_client
    )
    
    # then
    assert result == {
        "fable_text": fable_text,
        "images": image_urls,
        "prompts": image_prompts
    }
    
    mock_generate_fable.assert_called_once_with(
        world_description="magical forest",
        main_character="wise owl",
        age=7,
        num_images=2,
        client=mock_openai_client
    )
    
    mock_generate_images.assert_called_once_with(image_prompts, client=mock_openai_client)

def test_create_fable_with_images_no_client(mock_generate_fable, mock_generate_images):
    # given
    fable_text = "Once upon a time..."
    image_prompts = ["prompt1", "prompt2"]
    image_urls = ["image1.jpg", "image2.jpg"]
    
    mock_generate_fable.return_value = (fable_text, image_prompts)
    mock_generate_images.return_value = image_urls
    
    mock_client = MagicMock()
    with patch('app.fable_service.get_openai_client', return_value=mock_client):
        # when
        result = create_fable_with_images(
            world_description="magical forest",
            main_character="wise owl",
            age=7,
            num_images=2
        )
        
        # then
        assert result == {
            "fable_text": fable_text,
            "images": image_urls,
            "prompts": image_prompts
        }
        
        mock_generate_fable.assert_called_once_with(
            world_description="magical forest",
            main_character="wise owl",
            age=7,
            num_images=2,
            client=mock_client
        )
        
        mock_generate_images.assert_called_once_with(image_prompts, client=mock_client) 