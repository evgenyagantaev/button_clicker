import pytest
from unittest.mock import patch, MagicMock, call
import time
from screen_spy_agent.screen_spy_agent import ScreenSpyAgent


class TestScreenSpyAgent:
    """Tests for the ScreenSpyAgent class."""

    def test_init(self):
        """Test initialization with valid parameters."""
        # Create mock components
        mock_screenshot_taker = MagicMock()
        mock_image_analyzer = MagicMock()
        mock_mouse_controller = MagicMock()
        
        # Create agent
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_taker,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15
        )
        
        # Verify
        assert agent.screenshot_taker == mock_screenshot_taker
        assert agent.image_analyzer == mock_image_analyzer
        assert agent.mouse_controller == mock_mouse_controller
        assert agent.interval == 15
        assert agent.running is False
        assert agent.agent_state is not None

    @patch('screen_spy_agent.screen_spy_agent.AgentNode')
    def test_setup_workflow(self, mock_agent_node):
        """Test that setup_workflow correctly sets up the workflow."""
        # Create mock components
        mock_screenshot_taker = MagicMock()
        mock_image_analyzer = MagicMock()
        mock_mouse_controller = MagicMock()
        
        # Create agent
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_taker,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15
        )
        
        # Call method
        agent.setup_workflow()
        
        # Verify
        assert agent.workflow is not None

    @patch('screen_spy_agent.screen_spy_agent.threading.Thread')
    def test_run_agent(self, mock_thread):
        """Test that run_agent starts the agent thread."""
        # Create mock components
        mock_screenshot_taker = MagicMock()
        mock_image_analyzer = MagicMock()
        mock_mouse_controller = MagicMock()
        
        # Create agent
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_taker,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15
        )
        
        # Setup mock thread
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        # Call method
        agent.run_agent()
        
        # Verify
        assert agent.running is True
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    def test_stop_agent(self):
        """Test that stop_agent stops the agent."""
        # Create mock components
        mock_screenshot_taker = MagicMock()
        mock_image_analyzer = MagicMock()
        mock_mouse_controller = MagicMock()
        
        # Create agent
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_taker,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15
        )
        
        # Set running to True
        agent.running = True
        
        # Call method
        agent.stop_agent()
        
        # Verify
        assert agent.running is False

    @patch('screen_spy_agent.screen_spy_agent.time.sleep')
    def test_agent_loop(self, mock_sleep):
        """Test the agent_loop method."""
        # Create mock components
        mock_screenshot_taker = MagicMock()
        mock_image_analyzer = MagicMock()
        mock_mouse_controller = MagicMock()
        
        # Setup mock screenshot taker
        mock_screenshot = MagicMock()
        mock_screenshot_taker.capture_screenshot.return_value = mock_screenshot
        mock_screenshot_taker.save_screenshot.return_value = "/path/to/screenshot.jpg"
        mock_screenshot_taker.get_screenshot_path.return_value = "screenshot_20230101_120000.jpg"
        
        # Create agent
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_taker,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15
        )
        
        # Setup mock workflow
        agent.workflow = MagicMock()
        
        # Make the agent stop after one iteration
        def stop_after_one_iteration(*args, **kwargs):
            agent.running = False
            return None
        
        mock_sleep.side_effect = stop_after_one_iteration
        
        # Set running to True before calling agent_loop
        agent.running = True
        
        # Call method
        agent.agent_loop()
        
        # Verify
        mock_screenshot_taker.capture_screenshot.assert_called_once()
        mock_screenshot_taker.save_screenshot.assert_called_once_with(mock_screenshot, "screenshot_20230101_120000.jpg")
        agent.workflow.assert_called_once()
        mock_sleep.assert_called_once_with(15)

    @patch('screen_spy_agent.screen_spy_agent.AgentNode')
    @patch('screen_spy_agent.screen_spy_agent.time.sleep')
    def test_end_to_end_with_mocks(self, mock_sleep, mock_agent_node):
        """Test end-to-end functionality with mocks."""
        # Create mock components
        mock_screenshot_taker = MagicMock()
        mock_image_analyzer = MagicMock()
        mock_mouse_controller = MagicMock()
        
        # Setup mock screenshot taker
        mock_screenshot = MagicMock()
        mock_screenshot_taker.capture_screenshot.return_value = mock_screenshot
        mock_screenshot_taker.save_screenshot.return_value = "/path/to/screenshot.jpg"
        mock_screenshot_taker.get_screenshot_path.return_value = "screenshot_20230101_120000.jpg"
        
        # Setup mock agent node methods
        mock_detect_result = MagicMock()
        mock_decide_result = MagicMock()
        mock_execute_result = MagicMock()
        
        mock_agent_node.detect_words_in_screenshot.return_value = mock_detect_result
        mock_agent_node.decide_action.return_value = mock_decide_result
        mock_agent_node.execute_action.return_value = mock_execute_result
        
        # Create agent
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_taker,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15
        )
        
        # Make the agent stop after one iteration
        def stop_after_one_iteration(*args, **kwargs):
            agent.running = False
            return None
        
        mock_sleep.side_effect = stop_after_one_iteration
        
        # Run the agent
        agent.run_agent()
        
        # Wait for the agent to stop
        time.sleep(0.1)
        
        # Verify
        mock_screenshot_taker.capture_screenshot.assert_called_once()
        mock_screenshot_taker.save_screenshot.assert_called_once_with(mock_screenshot, "screenshot_20230101_120000.jpg")
        mock_agent_node.detect_words_in_screenshot.assert_called_once()
        mock_agent_node.decide_action.assert_called_once()
        mock_agent_node.execute_action.assert_called_once() 