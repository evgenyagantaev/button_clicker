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
        assert agent.screenshot_takers[0] == mock_screenshot_taker
        assert agent.image_analyzer == mock_image_analyzer
        assert agent.mouse_controller == mock_mouse_controller
        assert agent.interval == 15
        assert agent.running is False
        assert agent.agent_state is not None

    def test_init_with_multiple_screenshot_areas(self):
        """Test initialization with multiple screenshot areas."""
        # Create mock components
        mock_screenshot_takers = [MagicMock() for _ in range(4)]
        mock_image_analyzer = MagicMock()
        mock_mouse_controller = MagicMock()
        
        # Create agent
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_takers,  # Pass a list of screenshot takers
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15
        )
        
        # Verify
        assert len(agent.screenshot_takers) == 4
        for i, taker in enumerate(mock_screenshot_takers):
            assert agent.screenshot_takers[i] == taker
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

    @patch('screen_spy_agent.screen_spy_agent.AgentNode')
    def test_setup_workflow_with_multiple_areas(self, mock_agent_node):
        """Test that setup_workflow correctly sets up the workflow for multiple screenshot areas."""
        # Create mock components
        mock_screenshot_takers = [MagicMock() for _ in range(4)]
        mock_image_analyzer = MagicMock()
        mock_mouse_controller = MagicMock()
        
        # Create agent
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_takers,
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
        
        # Create agent - manually execute agent_loop without threading
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_taker,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15
        )
        
        # Setup mock workflow with a simple return value
        workflow_result = {
            "detection_history": [],
            "action_history": [],
            "current_screenshot": "/path/to/screenshot.jpg",
            "both_words_detected": False,
            "should_click": False
        }
        agent.workflow = MagicMock()
        agent.workflow.invoke.return_value = workflow_result
        
        # Make the agent stop after one iteration
        def stop_after_one_iteration(*args, **kwargs):
            agent.running = False
            return None
        
        mock_sleep.side_effect = stop_after_one_iteration
        
        # Set running to True before calling agent_loop
        agent.running = True
        
        # Call method directly
        agent.agent_loop()
        
        # Verify capture and save were called
        assert mock_screenshot_taker.capture_screenshot.call_count == 1
        assert mock_screenshot_taker.save_screenshot.call_count == 1
        assert mock_screenshot_taker.save_screenshot.call_args == call(mock_screenshot)
        
        # Verify workflow was invoked
        assert agent.workflow.invoke.call_count == 1
        
        # Verify sleep was called
        assert mock_sleep.call_count == 1
        assert mock_sleep.call_args == call(15)

    @patch('screen_spy_agent.screen_spy_agent.time.sleep')
    def test_agent_loop_with_multiple_areas(self, mock_sleep):
        """Test the agent_loop method with multiple screenshot areas."""
        # Create mock components
        mock_screenshot_takers = [MagicMock() for _ in range(4)]
        mock_image_analyzer = MagicMock()
        mock_mouse_controller = MagicMock()
        
        # Setup mock screenshot takers
        mock_screenshots = [MagicMock() for _ in range(4)]
        for i, (taker, screenshot) in enumerate(zip(mock_screenshot_takers, mock_screenshots)):
            taker.capture_screenshot.return_value = screenshot
            taker.save_screenshot.return_value = f"/path/to/screenshot_{i}.jpg"
        
        # Create agent - manually execute agent_loop without threading
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_takers,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15
        )
        
        # Setup mock workflow with a simple return value for each area
        workflow_results = [
            {
                "detection_history": [[]],
                "action_history": [[]],
                "current_screenshots": ["/path/to/screenshot_0.jpg", "/path/to/screenshot_1.jpg", "/path/to/screenshot_2.jpg", "/path/to/screenshot_3.jpg"],
                "detection_results": [False, False, False, False],
                "should_click": False
            }
        ]
        agent.workflow = MagicMock()
        agent.workflow.invoke.return_value = workflow_results[0]
        
        # Make the agent stop after one iteration
        def stop_after_one_iteration(*args, **kwargs):
            agent.running = False
            return None
        
        mock_sleep.side_effect = stop_after_one_iteration
        
        # Set running to True before calling agent_loop
        agent.running = True
        
        # Call method directly
        agent.agent_loop()
        
        # Verify capture and save were called for each area
        for i, (taker, screenshot) in enumerate(zip(mock_screenshot_takers, mock_screenshots)):
            assert taker.capture_screenshot.call_count == 1
            assert taker.save_screenshot.call_count == 1
            assert taker.save_screenshot.call_args == call(screenshot)
        
        # Verify workflow was invoked once with the combined state
        assert agent.workflow.invoke.call_count == 1
        
        # Get the actual argument passed to workflow.invoke
        invoke_arg = agent.workflow.invoke.call_args[0][0]
        
        # Verify the state contains information for all areas
        assert "current_screenshots" in invoke_arg
        assert len(invoke_arg["current_screenshots"]) == 4
        assert "detection_results" in invoke_arg
        assert len(invoke_arg["detection_results"]) == 4
        
        # Verify sleep was called
        assert mock_sleep.call_count == 1
        assert mock_sleep.call_args == call(15)

    @patch('threading.Thread')
    def test_end_to_end_with_mocks(self, mock_thread):
        """Test end-to-end functionality with mocks."""
        # Create mock components
        mock_screenshot_taker = MagicMock()
        mock_image_analyzer = MagicMock()
        mock_mouse_controller = MagicMock()
        
        # Setup mock screenshot taker
        mock_screenshot = MagicMock()
        mock_screenshot_taker.capture_screenshot.return_value = mock_screenshot
        mock_screenshot_taker.save_screenshot.return_value = "/path/to/screenshot.jpg"
        
        # Create agent
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_taker,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15
        )
        
        # Instead of starting a real thread, we'll directly call agent_loop once
        
        # Override the threading.Thread to call agent_loop directly and then finish
        def execute_agent_loop_once(*args, **kwargs):
            # Extract the target function from kwargs
            target_func = kwargs.get('target')
            if target_func:
                # Set a flag to stop after one iteration
                agent.running = True
                
                # Mock sleep to stop the agent after one iteration
                with patch('time.sleep') as mock_sleep:
                    def stop_agent(*args, **kwargs):
                        agent.running = False
                    mock_sleep.side_effect = stop_agent
                    
                    # Call the target function (should be agent_loop)
                    target_func()
            
            # Return a mock thread object
            mock_thread_instance = MagicMock()
            return mock_thread_instance
        
        mock_thread.side_effect = execute_agent_loop_once
        
        # Run the agent - this will directly execute agent_loop once
        agent.run_agent()
        
        # Verify screenshot was captured and saved
        assert mock_screenshot_taker.capture_screenshot.call_count == 1
        assert mock_screenshot_taker.save_screenshot.call_count == 1
        assert mock_screenshot_taker.save_screenshot.call_args == call(mock_screenshot)

    @patch('threading.Thread')
    def test_end_to_end_with_multiple_areas(self, mock_thread):
        """Test end-to-end functionality with multiple screenshot areas."""
        # Create mock components
        mock_screenshot_takers = [MagicMock() for _ in range(4)]
        mock_image_analyzer = MagicMock()
        mock_mouse_controller = MagicMock()
        
        # Setup mock screenshot takers
        mock_screenshots = [MagicMock() for _ in range(4)]
        for i, (taker, screenshot) in enumerate(zip(mock_screenshot_takers, mock_screenshots)):
            taker.capture_screenshot.return_value = screenshot
            taker.save_screenshot.return_value = f"/path/to/screenshot_{i}.jpg"
        
        # Create agent
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_takers,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15
        )
        
        # Instead of starting a real thread, we'll directly call agent_loop once
        
        # Override the threading.Thread to call agent_loop directly and then finish
        def execute_agent_loop_once(*args, **kwargs):
            # Extract the target function from kwargs
            target_func = kwargs.get('target')
            if target_func:
                # Set a flag to stop after one iteration
                agent.running = True
                
                # Mock sleep to stop the agent after one iteration
                with patch('time.sleep') as mock_sleep:
                    def stop_agent(*args, **kwargs):
                        agent.running = False
                    mock_sleep.side_effect = stop_agent
                    
                    # Call the target function (should be agent_loop)
                    target_func()
            
            # Return a mock thread object
            mock_thread_instance = MagicMock()
            return mock_thread_instance
        
        mock_thread.side_effect = execute_agent_loop_once
        
        # Run the agent - this will directly execute agent_loop once
        agent.run_agent()
        
        # Verify screenshots were captured and saved for each area
        for i, (taker, screenshot) in enumerate(zip(mock_screenshot_takers, mock_screenshots)):
            assert taker.capture_screenshot.call_count == 1
            assert taker.save_screenshot.call_count == 1
            assert taker.save_screenshot.call_args == call(screenshot) 