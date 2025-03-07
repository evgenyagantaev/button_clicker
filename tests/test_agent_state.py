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

    def test_init_with_multiple_areas(self):
        """Test initialization of AgentState with support for multiple areas."""
        state = AgentState(num_areas=4)
        assert state.detection_history == []
        assert state.action_history == []
        assert state.current_screenshots == ["", "", "", ""]
        assert state.detection_results == [False, False, False, False]
        assert state.should_click is False
        assert state.num_areas == 4

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

    def test_update_detection_with_multiple_areas(self):
        """Test updating detection state with multiple areas."""
        state = AgentState(num_areas=4)
        
        # Test with all False detections
        state.update_detection_for_area(0, False)
        state.update_detection_for_area(1, False)
        state.update_detection_for_area(2, False)
        state.update_detection_for_area(3, False)
        
        assert state.detection_results == [False, False, False, False]
        assert len(state.detection_history) == 1
        assert state.detection_history[0] == [False, False, False, False]
        assert state.should_click is False
        
        # Test with some True detections
        state.update_detection_for_area(1, True)
        state.update_detection_for_area(3, True)
        
        assert state.detection_results == [False, True, False, True]
        assert len(state.detection_history) == 2
        assert state.detection_history[1] == [False, True, False, True]
        
        # Test that should_click is True if any area has a detection
        assert state.should_click is True

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

    def test_set_current_screenshot_for_area(self):
        """Test setting current screenshot path for a specific area."""
        state = AgentState(num_areas=4)
        
        # Test with empty paths
        for i in range(4):
            state.set_current_screenshot_for_area(i, "")
            assert state.current_screenshots[i] == ""
        
        # Test with valid paths
        for i in range(4):
            path = f"/path/to/screenshot_{i}.jpg"
            state.set_current_screenshot_for_area(i, path)
            assert state.current_screenshots[i] == path

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

    def test_get_state_with_multiple_areas(self):
        """Test getting the full state as a dictionary with multiple areas."""
        state = AgentState(num_areas=4)
        
        # Set up some state
        state.update_detection_for_area(0, False)
        state.update_detection_for_area(1, True)
        state.update_detection_for_area(2, False)
        state.update_detection_for_area(3, True)
        
        state.update_action(True)
        
        for i in range(4):
            path = f"/path/to/screenshot_{i}.jpg"
            state.set_current_screenshot_for_area(i, path)
        
        # Get the state
        state_dict = state.get_state()
        
        # Verify
        assert state_dict["detection_history"] == [[False, True, False, True]]
        assert state_dict["action_history"] == [True]
        assert state_dict["current_screenshots"] == [
            "/path/to/screenshot_0.jpg",
            "/path/to/screenshot_1.jpg",
            "/path/to/screenshot_2.jpg",
            "/path/to/screenshot_3.jpg"
        ]
        assert state_dict["detection_results"] == [False, True, False, True]
        assert state_dict["should_click"] is True

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

    def test_history_limit_with_multiple_areas(self):
        """Test that history lists are limited to the specified size with multiple areas."""
        state = AgentState(history_limit=3, num_areas=4)
        
        # Add more items than the limit
        for i in range(5):
            # Alternating patterns for each area
            state.update_detection_for_area(0, i % 2 == 0)
            state.update_detection_for_area(1, i % 2 == 1)
            state.update_detection_for_area(2, i % 3 == 0)
            state.update_detection_for_area(3, i % 3 != 0)
            
            state.update_action(i % 2 == 0)
        
        # Verify that only the most recent 3 items are kept
        assert len(state.detection_history) == 3
        assert len(state.action_history) == 3
        
        # Check the last 3 detection history items
        expected_history = [
            [True, False, True, False],   # i=2
            [False, True, False, True],   # i=3
            [True, False, False, True]    # i=4
        ]
        assert state.detection_history == expected_history
        
        # The last 3 action items should be [True, False, True] (for i=2,3,4)
        assert state.action_history == [True, False, True] 