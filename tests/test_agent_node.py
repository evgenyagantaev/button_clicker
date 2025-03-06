import pytest
from unittest.mock import patch, MagicMock
from screen_spy_agent.agent_node import AgentNode
from screen_spy_agent.agent_state import AgentState


class TestAgentNode:
    """Tests for the AgentNode class."""

    def test_detect_words_in_screenshot(self):
        """Test the detect_words_in_screenshot node function."""
        # Create a mock state
        state = AgentState()
        state.set_current_screenshot("/path/to/screenshot.jpg")
        
        # Create a mock image analyzer that returns True
        mock_analyzer = MagicMock()
        mock_analyzer.detect_text_in_image.return_value = True
        
        # Call the node function
        new_state = AgentNode.detect_words_in_screenshot(state, mock_analyzer)
        
        # Verify
        assert new_state.both_words_detected is True
        assert len(new_state.detection_history) == 1
        assert new_state.detection_history[0] is True
        mock_analyzer.detect_text_in_image.assert_called_once_with("/path/to/screenshot.jpg")

    def test_decide_action_words_detected(self):
        """Test the decide_action node function when words are detected."""
        # Create a mock state with words detected
        state = AgentState()
        state.update_detection(True)
        
        # Call the node function
        new_state = AgentNode.decide_action(state)
        
        # Verify
        assert new_state.get_state()["should_click"] is True

    def test_decide_action_words_not_detected(self):
        """Test the decide_action node function when words are not detected."""
        # Create a mock state with words not detected
        state = AgentState()
        state.update_detection(False)
        
        # Call the node function
        new_state = AgentNode.decide_action(state)
        
        # Verify
        assert new_state.get_state()["should_click"] is False

    def test_execute_action_should_click(self):
        """Test the execute_action node function when should_click is True."""
        # Create a mock state with should_click=True
        state = AgentState()
        state.update_detection(True)
        state = AgentNode.decide_action(state)  # This sets should_click to True
        
        # Create a mock mouse controller that returns True
        mock_controller = MagicMock()
        mock_controller.click_at_position.return_value = True
        
        # Call the node function
        new_state = AgentNode.execute_action(state, mock_controller)
        
        # Verify
        assert len(new_state.action_history) == 1
        assert new_state.action_history[0] is True
        mock_controller.click_at_position.assert_called_once()

    def test_execute_action_should_not_click(self):
        """Test the execute_action node function when should_click is False."""
        # Create a mock state with should_click=False
        state = AgentState()
        state.update_detection(False)
        state = AgentNode.decide_action(state)  # This sets should_click to False
        
        # Create a mock mouse controller
        mock_controller = MagicMock()
        
        # Call the node function
        new_state = AgentNode.execute_action(state, mock_controller)
        
        # Verify
        assert len(new_state.action_history) == 0
        mock_controller.click_at_position.assert_not_called()

    def test_node_transitions(self):
        """Test the transitions between nodes."""
        # Create a mock state
        state = AgentState()
        state.set_current_screenshot("/path/to/screenshot.jpg")
        
        # Create mock components
        mock_analyzer = MagicMock()
        mock_analyzer.detect_text_in_image.return_value = True
        
        mock_controller = MagicMock()
        mock_controller.click_at_position.return_value = True
        
        # Execute the workflow
        state = AgentNode.detect_words_in_screenshot(state, mock_analyzer)
        state = AgentNode.decide_action(state)
        state = AgentNode.execute_action(state, mock_controller)
        
        # Verify the final state
        assert state.both_words_detected is True
        assert state.get_state()["should_click"] is True
        assert len(state.detection_history) == 1
        assert len(state.action_history) == 1
        assert state.detection_history[0] is True
        assert state.action_history[0] is True 