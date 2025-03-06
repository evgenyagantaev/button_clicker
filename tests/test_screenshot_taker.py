import os
import pytest
from unittest.mock import patch, MagicMock
import PIL.Image
from screen_spy_agent.screenshot_taker import ScreenshotTaker


class TestScreenshotTaker:
    """Tests for the ScreenshotTaker class."""

    def test_init_valid_coordinates(self):
        """Test initialization with valid coordinates."""
        taker = ScreenshotTaker(100, 200, 300, 400, 15)
        assert taker.x1 == 100
        assert taker.y1 == 200
        assert taker.x2 == 300
        assert taker.y2 == 400
        assert taker.interval == 15

    def test_init_invalid_coordinates(self):
        """Test that invalid coordinates are handled properly."""
        # x2 < x1 and y2 < y1 should be swapped
        taker = ScreenshotTaker(300, 400, 100, 200, 15)
        assert taker.x1 == 100
        assert taker.y1 == 200
        assert taker.x2 == 300
        assert taker.y2 == 400

    def test_init_invalid_interval(self):
        """Test that invalid interval raises ValueError."""
        with pytest.raises(ValueError):
            ScreenshotTaker(100, 200, 300, 400, 0)
        
        with pytest.raises(ValueError):
            ScreenshotTaker(100, 200, 300, 400, -5)

    @patch('screen_spy_agent.screenshot_taker.ImageGrab')
    def test_capture_screenshot(self, mock_image_grab):
        """Test that capture_screenshot calls ImageGrab with correct parameters."""
        # Setup mock
        mock_image = MagicMock(spec=PIL.Image.Image)
        mock_image_grab.grab.return_value = mock_image
        
        # Call method
        taker = ScreenshotTaker(100, 200, 300, 400, 15)
        result = taker.capture_screenshot()
        
        # Verify
        mock_image_grab.grab.assert_called_once_with(bbox=(100, 200, 300, 400))
        assert result == mock_image

    @patch('screen_spy_agent.screenshot_taker.ImageGrab')
    def test_save_screenshot(self, mock_image_grab):
        """Test that save_screenshot saves the image correctly."""
        # Setup mock
        mock_image = MagicMock(spec=PIL.Image.Image)
        mock_image_grab.grab.return_value = mock_image
        
        # Call method
        taker = ScreenshotTaker(100, 200, 300, 400, 15)
        image = taker.capture_screenshot()
        path = taker.save_screenshot(image, "test_screenshot.jpg")
        
        # Verify
        mock_image.save.assert_called_once()
        assert path == os.path.abspath("test_screenshot.jpg")

    @patch('screen_spy_agent.screenshot_taker.time')
    @patch('screen_spy_agent.screenshot_taker.ImageGrab')
    def test_get_screenshot_path(self, mock_image_grab, mock_time):
        """Test that get_screenshot_path generates the expected path."""
        # Setup mocks
        mock_time.strftime.return_value = "20230101_120000"
        
        # Call method
        taker = ScreenshotTaker(100, 200, 300, 400, 15)
        path = taker.get_screenshot_path()
        
        # Verify
        expected_path = os.path.abspath("screenshot_20230101_120000.jpg")
        assert path == expected_path
        mock_time.strftime.assert_called_once_with("%Y%m%d_%H%M%S") 