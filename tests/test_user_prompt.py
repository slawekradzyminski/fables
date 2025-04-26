import pytest
from unittest.mock import patch
from app.prompts.user_prompt import render_user_prompt

# Use patch to mock the internal _load_prompt function
@patch('app.prompts.user_prompt._load_prompt')
def test_render_user_prompt(mock_load_prompt):
    # given
    # Provide a mock template content for _load_prompt
    mock_template = "Age: {{ age }}, World: {{ world_description }}, Character: {{ main_character }}, Images: {{ num_images }}"
    mock_load_prompt.return_value = mock_template
    
    age = 10
    world = "Cosmic Playground"
    char = "Playful Alien"
    num_images = 3
    
    expected_output = "Age: 10, World: Cosmic Playground, Character: Playful Alien, Images: 3"

    # when
    result = render_user_prompt(age, world, char, num_images)

    # then
    mock_load_prompt.assert_called_once_with("user.txt")
    assert result == expected_output 