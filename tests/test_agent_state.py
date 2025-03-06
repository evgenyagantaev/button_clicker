import pytest
from screen_spy_agent.agent_state import AgentState


class TestAgentState:
    """Tests for the AgentState class."""

    def test_init(self):
        """Test initialization of AgentState."""
        state = AgentState()
        assert state.detection_history == []
        assert state.action_history == []
        assert state.current_screenshot == ""
        assert state.both_words_detected is False

    def test_update_detection(self):
        """Test updating detection state."""
        state = AgentState()
        
        # Test with False detection
        state.update_detection(False)
        assert state.both_words_detected is False
        assert len(state.detection_history) == 1
        assert state.detection_history[0] is False
        
        # Test with True detection
        state.update_detection(True)
        assert state.both_words_detected is True
        assert len(state.detection_history) == 2
        assert state.detection_history[1] is True

    def test_update_action(self):
        """Test updating action state."""
        state = AgentState()
        
        # Test with False action
        state.update_action(False)
        assert len(state.action_history) == 1
        assert state.action_history[0] is False
        
        # Test with True action
        state.update_action(True)
        assert len(state.action_history) == 2
        assert state.action_history[1] is True

    def test_set_current_screenshot(self):
        """Test setting current screenshot path."""
        state = AgentState()
        
        # Test with empty path
        state.set_current_screenshot("")
        assert state.current_screenshot == ""
        
        # Test with valid path
        state.set_current_screenshot("/path/to/screenshot.jpg")
        assert state.current_screenshot == "/path/to/screenshot.jpg"

    def test_get_state(self):
        """Test getting the full state as a dictionary."""
        state = AgentState()
        
        # Set up some state
        state.update_detection(True)
        state.update_action(True)
        state.set_current_screenshot("/path/to/screenshot.jpg")
        
        # Get the state
        state_dict = state.get_state()
        
        # Verify
        assert state_dict["detection_history"] == [True]
        assert state_dict["action_history"] == [True]
        assert state_dict["current_screenshot"] == "/path/to/screenshot.jpg"
        assert state_dict["both_words_detected"] is True

    def test_history_limit(self):
        """Test that history lists are limited to the specified size."""
        state = AgentState(history_limit=3)
        
        # Add more items than the limit
        for i in range(5):
            state.update_detection(i % 2 == 0)  # Alternating True/False
            state.update_action(i % 2 == 0)
        
        # Verify that only the most recent 3 items are kept
        assert len(state.detection_history) == 3
        assert len(state.action_history) == 3
        
        # The last 3 items should be [True, False, True] (for i=2,3,4)
        assert state.detection_history == [True, False, True]
        assert state.action_history == [True, False, True] 