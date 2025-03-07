"""
AgentNode module for defining the agent workflow nodes.
"""

import copy


class AgentNode:
    """
    Class containing static methods that define the agent workflow nodes.
    Each node takes a state dictionary and returns updates to the state as a dictionary.
    """
    
    @staticmethod
    def detect_words_in_screenshot(state):
        """
        Node for detecting words in a screenshot.
        
        Args:
            state: The current state dictionary.
            
        Returns:
            dict: The updated state as a dictionary.
        """
        # Make a copy of the state to avoid modifying the original
        new_state = copy.deepcopy(state)
        
        # Use the image analyzer from the thread-local state
        from screen_spy_agent.screen_spy_agent import thread_local
        image_analyzer = thread_local.image_analyzer
        
        # Check if we're in single area or multiple areas mode
        if "current_screenshots" in state and len(state.get("current_screenshots", [])) > 0:
            # Multiple areas mode
            # The detection has already been done in the agent_loop
            # Just return the state as is
            return new_state
        else:
            # Single area mode
            # Detect words in the screenshot
            detection_result = image_analyzer.detect_text_in_image(state["current_screenshot"])
            
            # Update the state
            new_state["both_words_detected"] = detection_result
            new_state["detection_history"] = new_state["detection_history"] + [detection_result]
            
            # Return the state as a dictionary
            return new_state
    
    @staticmethod
    def decide_action(state):
        """
        Node for deciding whether to take action based on detection results.
        
        Args:
            state: The current state dictionary.
            
        Returns:
            dict: The updated state as a dictionary with a decision on whether to click.
        """
        # Make a copy of the state to avoid modifying the original
        new_state = copy.deepcopy(state)
        
        # Check if we're in single area or multiple areas mode
        if "detection_results" in state:
            # Multiple areas mode
            # Decide whether to click based on detection results
            # Click if any area has a detection
            should_click = any(state["detection_results"])
        else:
            # Single area mode
            # Decide whether to click based on detection results
            should_click = state["both_words_detected"]
        
        # Update the state
        new_state["should_click"] = should_click
        
        # Return the state as a dictionary
        return new_state
    
    @staticmethod
    def execute_action(state):
        """
        Node for executing the decided action.
        
        Args:
            state: The current state dictionary.
            
        Returns:
            dict: The updated state as a dictionary.
        """
        # Make a copy of the state to avoid modifying the original
        new_state = copy.deepcopy(state)
        
        # Use the mouse controller from the thread-local state
        from screen_spy_agent.screen_spy_agent import thread_local
        mouse_controller = thread_local.mouse_controller
        
        # Check if we should click
        if state["should_click"]:
            # Execute the click
            action_result = mouse_controller.click_at_position()
            
            # Update the state
            new_state["action_history"] = new_state["action_history"] + [action_result]
        
        # Return the state as a dictionary
        return new_state 