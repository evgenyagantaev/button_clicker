import pytest
import base64
import os
from unittest.mock import patch, MagicMock
from screen_spy_agent.image_analyzer import ImageAnalyzer


class TestImageAnalyzer:
    """Tests for the ImageAnalyzer class."""

    def test_init(self):
        """Test initialization with valid parameters."""
        analyzer = ImageAnalyzer(
            api_key="test_key",
            api_base="https://api.example.com",
            model="test-model"
        )
        assert analyzer.api_key == "test_key"
        assert analyzer.api_base == "https://api.example.com"
        assert analyzer.model == "test-model"

    def test_encode_image(self, sample_image):
        """Test that encode_image correctly encodes an image to base64."""
        analyzer = ImageAnalyzer(
            api_key="test_key",
            api_base="https://api.example.com",
            model="test-model"
        )
        
        # Encode the image
        base64_image = analyzer.encode_image(sample_image)
        
        # Verify it's a valid base64 string
        try:
            decoded = base64.b64decode(base64_image)
            assert len(decoded) > 0
        except Exception as e:
            pytest.fail(f"Failed to decode base64 string: {e}")

    @patch('screen_spy_agent.image_analyzer.openai')
    def test_analyze_image(self, mock_openai, sample_image, mock_api_response_both_words):
        """Test that analyze_image correctly calls the OpenAI API."""
        # Setup mock
        mock_openai.ChatCompletion.create.return_value = mock_api_response_both_words
        
        # Create analyzer
        analyzer = ImageAnalyzer(
            api_key="test_key",
            api_base="https://api.example.com",
            model="test-model"
        )
        
        # Call method
        response = analyzer.analyze_image(sample_image)
        
        # Verify
        assert response == mock_api_response_both_words
        mock_openai.ChatCompletion.create.assert_called_once()

    @patch('screen_spy_agent.image_analyzer.openai')
    def test_detect_text_in_image_both_words(self, mock_openai, sample_image, mock_api_response_both_words):
        """Test that detect_text_in_image returns True when both words are detected."""
        # Setup mock
        mock_openai.ChatCompletion.create.return_value = mock_api_response_both_words
        
        # Create analyzer
        analyzer = ImageAnalyzer(
            api_key="test_key",
            api_base="https://api.example.com",
            model="test-model"
        )
        
        # Call method
        result = analyzer.detect_text_in_image(sample_image)
        
        # Verify
        assert result is True

    @patch('screen_spy_agent.image_analyzer.openai')
    def test_detect_text_in_image_no_words(self, mock_openai, sample_image, mock_api_response_no_words):
        """Test that detect_text_in_image returns False when no words are detected."""
        # Setup mock
        mock_openai.ChatCompletion.create.return_value = mock_api_response_no_words
        
        # Create analyzer
        analyzer = ImageAnalyzer(
            api_key="test_key",
            api_base="https://api.example.com",
            model="test-model"
        )
        
        # Call method
        result = analyzer.detect_text_in_image(sample_image)
        
        # Verify
        assert result is False

    @patch('screen_spy_agent.image_analyzer.openai')
    def test_detect_text_in_image_only_accept(self, mock_openai, sample_image, mock_api_response_only_accept):
        """Test that detect_text_in_image returns False when only 'Accept' is detected."""
        # Setup mock
        mock_openai.ChatCompletion.create.return_value = mock_api_response_only_accept
        
        # Create analyzer
        analyzer = ImageAnalyzer(
            api_key="test_key",
            api_base="https://api.example.com",
            model="test-model"
        )
        
        # Call method
        result = analyzer.detect_text_in_image(sample_image)
        
        # Verify
        assert result is False

    @patch('screen_spy_agent.image_analyzer.openai')
    def test_detect_text_in_image_only_reject(self, mock_openai, sample_image, mock_api_response_only_reject):
        """Test that detect_text_in_image returns False when only 'Reject' is detected."""
        # Setup mock
        mock_openai.ChatCompletion.create.return_value = mock_api_response_only_reject
        
        # Create analyzer
        analyzer = ImageAnalyzer(
            api_key="test_key",
            api_base="https://api.example.com",
            model="test-model"
        )
        
        # Call method
        result = analyzer.detect_text_in_image(sample_image)
        
        # Verify
        assert result is False

    @patch('screen_spy_agent.image_analyzer.openai')
    def test_api_error_handling(self, mock_openai, sample_image):
        """Test that API errors are handled properly."""
        # Setup mock to raise an exception
        mock_openai.ChatCompletion.create.side_effect = Exception("API Error")
        
        # Create analyzer
        analyzer = ImageAnalyzer(
            api_key="test_key",
            api_base="https://api.example.com",
            model="test-model"
        )
        
        # Call method and verify it handles the exception
        with pytest.raises(Exception, match="API Error"):
            analyzer.analyze_image(sample_image) 