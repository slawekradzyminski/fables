import pytest
from unittest.mock import patch, MagicMock, ANY
from app.services.openai_client import generate_fable_and_prompts, generate_illustration_image, get_openai_client
from app.core.config import Settings
from app.types.openai_response import OpenAiResponse
import json
from io import BytesIO

# Mock settings to avoid issues with real API keys
@pytest.fixture
def mock_settings():
    with patch('app.services.openai_client.get_settings') as mock_get:
        mock_get.return_value = Settings(openai_api_key="fake-key")
        yield

# Mock OpenAI client fixture
@pytest.fixture
def mock_openai_client():
    with patch('app.services.openai_client.OpenAI') as mock_constructor:
        mock_instance = MagicMock()
        mock_constructor.return_value = mock_instance
        yield mock_instance # Yield the mock instance for assertions

# Mock file loading
@pytest.fixture
def mock_file_io():
     with patch('app.services.openai_client._load_prompt') as mock_load_prompt, \
          patch('app.services.openai_client.render_user_prompt') as mock_render_prompt:
        mock_load_prompt.return_value = "System prompt content"
        mock_render_prompt.return_value = "User prompt content"
        yield mock_load_prompt, mock_render_prompt

# --- Tests for generate_fable_and_prompts --- 

def test_generate_fable_and_prompts_success(mock_settings, mock_openai_client, mock_file_io):
    # given
    world = "Moon Base Alpha"
    char = "Curious Astronaut"
    age = 12
    num_images = 1
    
    # Mock the API response
    mock_response_content = OpenAiResponse(
        fable="An astronaut explored the moon...",
        moral="Curiosity is key.",
        image_prompts=["Astronaut on moon surface"]
    )
    mock_api_response = MagicMock()
    mock_api_response.choices[0].message.content = mock_response_content.model_dump_json()
    mock_openai_client.chat.completions.create.return_value = mock_api_response
    
    mock_load_prompt, mock_render_prompt = mock_file_io

    # when
    result = generate_fable_and_prompts(world, char, age, num_images)

    # then
    mock_load_prompt.assert_called_once_with("system.txt")
    mock_render_prompt.assert_called_once_with(age, world, char, num_images)
    mock_openai_client.chat.completions.create.assert_called_once_with(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "System prompt content"},
            {"role": "user", "content": "User prompt content"}
        ],
        temperature=0.8,
        max_tokens=1000,
        response_format={"type": "json_object"}
    )
    assert result == mock_response_content

# --- Tests for generate_illustration_image --- 

def test_generate_illustration_image_no_reference(mock_settings, mock_openai_client):
    # given
    prompt = "A colorful nebula"
    expected_b64 = "base64_encoded_image_data"
    
    mock_api_response = MagicMock()
    mock_api_response.data[0].b64_json = expected_b64
    mock_openai_client.images.generate.return_value = mock_api_response

    # when
    result = generate_illustration_image(prompt)

    # then
    mock_openai_client.images.generate.assert_called_once_with(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )
    assert result == expected_b64
    mock_openai_client.images.edit.assert_not_called() # Ensure edit endpoint wasn't called

def test_generate_illustration_image_with_reference(mock_settings, mock_openai_client):
    # given
    prompt = "A spaceship landing"
    reference_image_data = b'reference_image_bytes'
    reference_image_file = BytesIO(reference_image_data)
    reference_image_file.name = "ref.png" # Name is set in the calling function usually
    expected_b64 = "base64_encoded_edited_image_data"

    mock_api_response = MagicMock()
    mock_api_response.data[0].b64_json = expected_b64
    mock_openai_client.images.edit.return_value = mock_api_response

    # when
    # We pass the original BytesIO object, the function reads from it
    result = generate_illustration_image(prompt, reference_image=reference_image_file)

    # then
    # Assert that images.edit was called with the correct arguments
    # Note: The function creates a *new* BytesIO object internally, so we check args
    mock_openai_client.images.edit.assert_called_once()
    call_args = mock_openai_client.images.edit.call_args[1]
    assert call_args['model'] == "gpt-image-1"
    assert call_args['prompt'] == prompt
    assert call_args['size'] == "1024x1024"
    # Check the image arg passed to the API call
    assert isinstance(call_args['image'], BytesIO)
    assert call_args['image'].read() == reference_image_data # Check content
    assert call_args['image'].name == "image.png" # Check filename set internally

    assert result == expected_b64
    mock_openai_client.images.generate.assert_not_called() # Ensure generate wasn't called 