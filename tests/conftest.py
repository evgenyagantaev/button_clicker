import pytest
import os
import tempfile
from PIL import Image
from unittest.mock import MagicMock


@pytest.fixture
def mock_api_response_both_words():
    """Mock API response where both 'Accept' and 'Reject' are detected."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Yes, both words 'Accept' and 'Reject' are present in the image."
                }
            }
        ]
    }


@pytest.fixture
def mock_api_response_no_words():
    """Mock API response where neither 'Accept' nor 'Reject' are detected."""
    return {
        "choices": [
            {
                "message": {
                    "content": "No, neither 'Accept' nor 'Reject' are present in the image."
                }
            }
        ]
    }


@pytest.fixture
def mock_api_response_only_accept():
    """Mock API response where only 'Accept' is detected."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Only the word 'Accept' is present in the image. 'Reject' is not visible."
                }
            }
        ]
    }


@pytest.fixture
def mock_api_response_only_reject():
    """Mock API response where only 'Reject' is detected."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Only the word 'Reject' is present in the image. 'Accept' is not visible."
                }
            }
        ]
    }


@pytest.fixture
def sample_image():
    """Create a temporary test image."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        img = Image.new('RGB', (100, 30), color='white')
        img.save(tmp.name)
        yield tmp.name
    # Clean up
    if os.path.exists(tmp.name):
        os.remove(tmp.name)


@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    mock = MagicMock()
    mock.chat.completions.create.return_value = MagicMock()
    return mock 