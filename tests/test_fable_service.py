import pytest
from unittest.mock import patch, MagicMock, call
from app.services.fable_service import fable_generation_handler
from app.types.openai_response import OpenAiResponse # Corrected import path
import base64

@patch("app.services.fable_service.generate_fable_and_prompts")
@patch("app.services.fable_service.generate_illustration_image")
@patch("app.services.fable_service.save_base64_image")
@patch("app.services.fable_service.os.makedirs") # Mock makedirs
@patch("app.services.fable_service.BytesIO") # Mock BytesIO if needed for reference image handling
@patch("app.services.fable_service.base64.b64decode") # Mock b64decode for reference image handling
def test_fable_generation_handler(
    mock_b64decode,
    mock_bytesio,
    mock_makedirs,
    mock_save_image,
    mock_gen_image,
    mock_gen_fable
):
    # given
    world = "Enchanted Forest"
    char = "Brave Fox"
    age = 7
    num_images = 2

    # Use the actual type for mocking
    mock_fable_response = OpenAiResponse(
        fable="The fox went on an adventure...",
        moral="Bravery leads to discovery.",
        image_prompts=["Fox in forest", "Fox finds a treasure"]
    )
    mock_gen_fable.return_value = mock_fable_response

    # Mock image generation - return different base64 strings
    mock_image_1_b64 = base64.b64encode(b'image1_data').decode('utf-8')
    mock_image_2_b64 = base64.b64encode(b'image2_data').decode('utf-8')
    mock_gen_image.side_effect = [mock_image_1_b64, mock_image_2_b64]

    # Mock BytesIO return value needs a 'name' attribute for the handler logic
    mock_file_object = MagicMock()
    mock_bytesio.return_value = mock_file_object

    # when
    result = fable_generation_handler(world, char, age, num_images)

    # then
    # 1. Check if fable generation was called correctly
    mock_gen_fable.assert_called_once_with(
        world_description=world,
        main_character=char,
        age=age,
        num_images=num_images
    )

    # 2. Check if directory creation was attempted
    mock_makedirs.assert_called_once_with("output_folder", exist_ok=True)

    # 3. Check image generation calls
    assert mock_gen_image.call_count == 2
    calls = mock_gen_image.call_args_list
    # First call without reference image
    calls[0].assert_called_with("Fox in forest")
    # Second call *with* reference image
    # We need to check the arguments passed to generate_illustration_image for the reference image
    # It expects a file-like object from BytesIO
    mock_b64decode.assert_called_once_with(mock_image_1_b64)
    mock_bytesio.assert_called_once_with(mock_b64decode.return_value)
    calls[1].assert_called_with("Fox finds a treasure", reference_image=mock_file_object)


    # 4. Check image saving calls (ignore timestamp in filename check)
    assert mock_save_image.call_count == 2
    save_calls = mock_save_image.call_args_list
    assert save_calls[0][0][0] == mock_image_1_b64
    assert save_calls[0][0][1].startswith("output_folder/image0_")
    assert save_calls[1][0][0] == mock_image_2_b64
    assert save_calls[1][0][1].startswith("output_folder/image1_")

    # 5. Check the final returned structure
    expected_result = {
        "fable": mock_fable_response.fable,
        "moral": mock_fable_response.moral,
        "illustrations": [
            {"prompt": "Fox in forest", "image": mock_image_1_b64},
            {"prompt": "Fox finds a treasure", "image": mock_image_2_b64}
        ]
    }
    assert result == expected_result 