import pytest
from unittest.mock import patch, MagicMock
from screen_spy_agent.mouse_controller import MouseController


class TestMouseController:
    """Tests for the MouseController class."""

    def test_init(self):
        """Test initialization with valid coordinates."""
        controller = MouseController(100, 200)
        assert controller.target_x == 100
        assert controller.target_y == 200

    def test_init_invalid_coordinates(self):
        """Test that invalid coordinates raise ValueError."""
        with pytest.raises(ValueError):
            MouseController(-1, 200)
        
        with pytest.raises(ValueError):
            MouseController(100, -1)

    @patch('screen_spy_agent.mouse_controller.pyautogui')
    def test_click_at_position(self, mock_pyautogui):
        """Test that click_at_position calls pyautogui.click with correct parameters."""
        # Setup mock
        mock_pyautogui.click.return_value = None
        
        # Call method
        controller = MouseController(100, 200)
        result = controller.click_at_position()
        
        # Verify
        mock_pyautogui.click.assert_called_once_with(x=100, y=200)
        assert result is True

    @patch('screen_spy_agent.mouse_controller.pyautogui')
    def test_click_at_position_error(self, mock_pyautogui):
        """Test that click_at_position handles errors properly."""
        # Setup mock to raise an exception
        mock_pyautogui.click.side_effect = Exception("Click Error")
        
        # Call method
        controller = MouseController(100, 200)
        result = controller.click_at_position()
        
        # Verify
        mock_pyautogui.click.assert_called_once_with(x=100, y=200)
        assert result is False

    @patch('screen_spy_agent.mouse_controller.pyautogui')
    def test_get_screen_size(self, mock_pyautogui):
        """Test that get_screen_size returns the correct screen dimensions."""
        # Setup mock
        mock_pyautogui.size.return_value = (1920, 1080)
        
        # Call method
        result = MouseController.get_screen_size()
        
        # Verify
        assert result == (1920, 1080)
        mock_pyautogui.size.assert_called_once() 