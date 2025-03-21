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

        # Create a real CyclicPromptManager with empty prompt
        from screen_spy_agent.cyclic_prompt_manager import CyclicPromptManager
        real_prompt_manager = CyclicPromptManager("")

        # Create agent with empty cyclic prompt - shouldn't trigger start sequence
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_taker,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15,
            cyclic_prompt=""  # Empty prompt, shouldn't trigger start sequence
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
        
        # Make image analyzer not detect "new chat" to avoid restart cycle
        mock_image_analyzer.detect_text_in_image.return_value = False

        # Make the agent stop after one iteration
        def stop_after_one_iteration(*args, **kwargs):
            agent.running = False
            return None

        mock_sleep.side_effect = stop_after_one_iteration

        # Set running to True before calling agent_loop
        agent.running = True

        # Call method directly
        agent.agent_loop()

        # Since we used an empty prompt, execute_start_sequence shouldn't be called

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
        for i, (mock_taker, mock_screenshot) in enumerate(zip(mock_screenshot_takers, mock_screenshots)):
            mock_taker.capture_screenshot.return_value = mock_screenshot
            mock_taker.save_screenshot.return_value = f"/path/to/screenshot_{i}.jpg"
        
        # Create agent - manually execute agent_loop without threading
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_takers,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15,
            cyclic_prompt=""  # Empty prompt, shouldn't trigger start sequence
        )
        
        # Setup mock workflow with a simple return value
        workflow_result = {
            "detection_history": [],
            "action_history": [],
            "current_screenshots": [f"/path/to/screenshot_{i}.jpg" for i in range(4)],
            "both_words_detected": False,
            "should_click": False
        }
        agent.workflow = MagicMock()
        agent.workflow.invoke.return_value = workflow_result
        
        # Make image analyzer not detect "new chat" to avoid restart cycle
        mock_image_analyzer.detect_text_in_image.return_value = False
        
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
        
        # Configure mock image analyzer to return False for all detect_text_in_image calls
        # This prevents early break in the agent_loop
        mock_image_analyzer.detect_text_in_image.return_value = False
        
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

    @patch('screen_spy_agent.screen_spy_agent.CyclicPromptManager')
    def test_init_with_cyclic_prompt_manager(self, mock_cyclic_prompt_manager):
        """Test that a CyclicPromptManager is initialized when creating a ScreenSpyAgent."""
        # Create mock components
        mock_screenshot_taker = MagicMock()
        mock_image_analyzer = MagicMock()
        mock_mouse_controller = MagicMock()
        
        # Setup mock cyclic prompt manager
        mock_manager_instance = MagicMock()
        mock_cyclic_prompt_manager.return_value = mock_manager_instance
        
        # Create agent
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_taker,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15
        )
        
        # Verify
        assert agent.cyclic_prompt_manager is not None
        assert agent.cyclic_prompt_manager == mock_manager_instance
    
    @patch('screen_spy_agent.screen_spy_agent.time.sleep')
    def test_execute_start_sequence(self, mock_sleep):
        """Test the execute_start_sequence method that should perform clicks and clipboard operations."""
        # Create mock components
        mock_screenshot_taker = MagicMock()
        mock_image_analyzer = MagicMock()
        mock_mouse_controller = MagicMock()
        mock_cyclic_prompt_manager = MagicMock()
        
        # Create agent
        agent = ScreenSpyAgent(
            screenshot_taker=mock_screenshot_taker,
            image_analyzer=mock_image_analyzer,
            mouse_controller=mock_mouse_controller,
            interval=15
        )
        
        # Replace the agent's cyclic prompt manager with our mock
        agent.cyclic_prompt_manager = mock_cyclic_prompt_manager
        
        # Call the method
        agent.execute_start_sequence()
        
        # Verify expected behavior
        assert mock_mouse_controller.click_at_coordinates.call_count == 3
        mock_mouse_controller.click_at_coordinates.assert_any_call(1818, 46)  # Start new chat
        mock_mouse_controller.click_at_coordinates.assert_any_call(1419, 108)  # Focus on prompt field
        mock_mouse_controller.click_at_coordinates.assert_any_call(1874, 141)  # Send button
        
        assert mock_sleep.call_count == 3
        assert mock_cyclic_prompt_manager.copy_to_clipboard.call_count == 1
        assert mock_mouse_controller.paste_from_clipboard.call_count == 1
    
    @patch('screen_spy_agent.screen_spy_agent.time.sleep')
    def test_detect_new_chat_condition(self, mock_sleep):
        """Test that the agent detects 'new chat' in Area 1 and restarts the sequence."""
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
        
        # Set up mock to make the agent stop after detecting "new chat"
        def stop_after_detect(*args, **kwargs):
            agent.running = False
            return None
        
        mock_sleep.side_effect = stop_after_detect
        
        # Mock the execute_start_sequence method
        agent.execute_start_sequence = MagicMock()
        
        # Set up mock image analyzer to detect "new chat" in Area 1
        def mock_detect_text(screenshot_path, text_to_detect):
            if text_to_detect == "new chat" and screenshot_path.endswith("screenshot_0.jpg"):
                return True
            return False
        
        mock_image_analyzer.detect_text_in_image.side_effect = mock_detect_text
        
        # Set up mock screenshot takers
        mock_screenshots = [MagicMock() for _ in range(4)]
        for i, (taker, screenshot) in enumerate(zip(mock_screenshot_takers, mock_screenshots)):
            taker.capture_screenshot.return_value = screenshot
            taker.save_screenshot.return_value = f"/path/to/screenshot_{i}.jpg"
        
        # Set running to True
        agent.running = True
        
        # Call agent_loop directly
        agent.agent_loop()
        
        # Verify the start sequence was executed when "new chat" was detected
        agent.execute_start_sequence.assert_called_once()
    
    @patch('screen_spy_agent.screen_spy_agent.time.sleep')
    @patch('screen_spy_agent.screen_spy_agent.time.time')
    def test_detect_inactivity_in_area2(self, mock_time, mock_sleep):
        """Test that the agent detects inactivity in Area 2 (gray screen) for 2 minutes and restarts."""
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
        
        # Mock the execute_start_sequence method
        agent.execute_start_sequence = MagicMock()
        
        # Set up time mock to simulate 2 minutes passing
        mock_time.side_effect = [
            1000,  # First call - starting time
            1060,  # 1 minute later
            1180   # 3 minutes later, exceeding the 2-minute threshold
        ]
        
        # Set up image analyzer to detect empty/gray screen in Area 2
        def mock_detect_text(screenshot_path, text_to_detect):
            # Return False for all text detection
            return False
        
        def mock_detect_empty_screen(screenshot_path):
            # Return True for Area 2 to indicate empty/gray screen
            if screenshot_path.endswith("screenshot_2.jpg"):
                return True
            return False
        
        mock_image_analyzer.detect_text_in_image.side_effect = mock_detect_text
        mock_image_analyzer.detect_empty_screen.side_effect = mock_detect_empty_screen
        
        # Set up mock screenshot takers
        mock_screenshots = [MagicMock() for _ in range(4)]
        for i, (taker, screenshot) in enumerate(zip(mock_screenshot_takers, mock_screenshots)):
            taker.capture_screenshot.return_value = screenshot
            taker.save_screenshot.return_value = f"/path/to/screenshot_{i}.jpg"
        
        # Make the agent stop after one iteration
        def stop_after_one_iteration(*args, **kwargs):
            agent.running = False
            return None
        
        mock_sleep.side_effect = stop_after_one_iteration
        
        # Set running to True
        agent.running = True
        
        # Call agent_loop directly
        agent.agent_loop()
        
        # Verify the start sequence was executed when inactivity was detected
        agent.execute_start_sequence.assert_called()
    
    @patch('screen_spy_agent.screen_spy_agent.time.sleep')
    def test_cyclic_behavior(self, mock_sleep):
        """Test the cyclic behavior of the agent when conditions are met."""
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
        
        # Mock the execute_start_sequence method
        agent.execute_start_sequence = MagicMock()
        
        # Set up a scenario where we run through 3 cycles:
        # 1. Normal operation, no restart
        # 2. Detect "new chat" in Area 1 - trigger restart
        # 3. Detect inactivity in Area 2 - trigger restart
        
        # Side effect for sleep function to make the agent stop after three cycles
        agent._cycle_count = 0
        def simulate_cycles(*args, **kwargs):
            agent._cycle_count += 1
            if agent._cycle_count >= 3:
                agent.running = False
            return None
        
        mock_sleep.side_effect = simulate_cycles
        
        # Side effect for detect_text_in_image to simulate different scenarios
        def mock_detect_text(screenshot_path, text_to_detect):
            if agent._cycle_count == 2 and text_to_detect == "new chat" and screenshot_path.endswith("screenshot_0.jpg"):
                return True  # Detect "new chat" in Area 1 during the second cycle
            return False
        
        mock_image_analyzer.detect_text_in_image.side_effect = mock_detect_text
        
        # Side effect for detect_empty_screen to simulate different scenarios
        def mock_detect_empty_screen(screenshot_path):
            if agent._cycle_count == 3 and screenshot_path.endswith("screenshot_2.jpg"):
                return True  # Detect empty screen in Area 2 during the third cycle
            return False
        
        mock_image_analyzer.detect_empty_screen.side_effect = mock_detect_empty_screen
        
        # Set up mock screenshot takers
        mock_screenshots = [MagicMock() for _ in range(4)]
        for i, (taker, screenshot) in enumerate(zip(mock_screenshot_takers, mock_screenshots)):
            taker.capture_screenshot.return_value = screenshot
            taker.save_screenshot.return_value = f"/path/to/screenshot_{i}.jpg"
        
        # Set running to True
        agent.running = True
        
        # Call agent_loop directly
        agent.agent_loop()
        
        # Verify the start sequence was executed (at least once)
        assert agent.execute_start_sequence.call_count > 0
        
        # Verify sleep was called
        assert mock_sleep.call_count == 3 