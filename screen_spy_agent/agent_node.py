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
        if isinstance(new_state, dict) and "current_screenshots" in new_state and len(new_state.get("current_screenshots", [])) > 0:
            # Multiple areas mode
            # The detection has already been done in the agent_loop
            # Just return the state as is
            return new_state
        elif isinstance(new_state, dict):
            # Single area mode for dictionary input
            # Detect words in the screenshot
            detection_result = image_analyzer.detect_text_in_image(new_state["current_screenshot"])
            
            # Update the state
            new_state["both_words_detected"] = detection_result
            new_state["detection_history"] = new_state["detection_history"] + [detection_result]
            
            # Return the state as a dictionary
            return new_state
        else:
            # Handle AgentState object (for tests)
            try:
                if hasattr(new_state, 'get_state'):
                    # Convert to dictionary for processing
                    state_dict = new_state.get_state()
                    
                    # Check if we're in single area or multiple areas mode
                    if "current_screenshots" in state_dict and len(state_dict.get("current_screenshots", [])) > 0:
                        # Multiple areas mode - no action needed
                        return state_dict
                    else:
                        # Single area mode - detect words
                        detection_result = image_analyzer.detect_text_in_image(state_dict["current_screenshot"])
                        
                        # Update the AgentState object
                        new_state.update_detection(detection_result)
                        
                        # Return the updated state dictionary
                        return new_state.get_state()
                else:
                    # Not an AgentState object - return as is
                    return state_dict
            except (AttributeError, TypeError):
                # Fallback - return the input state
                return state
    
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
        
        # Check if we're dealing with a dictionary or an AgentState object
        if isinstance(new_state, dict):
            # Dictionary input
            # Check if we're in single area or multiple areas mode
            if "detection_results" in new_state:
                # Multiple areas mode
                # Decide whether to click based on detection results
                # Click if any area has a detection
                should_click = any(new_state["detection_results"])
            else:
                # Single area mode
                # Decide whether to click based on detection results
                should_click = new_state["both_words_detected"]
            
            # Update the state
            new_state["should_click"] = should_click
            
            # Return the state as a dictionary
            return new_state
        else:
            # Handle AgentState object (for tests)
            try:
                if hasattr(new_state, 'set_should_click'):
                    # For single area mode
                    if hasattr(new_state, 'both_words_detected'):
                        should_click = new_state.both_words_detected
                    # For multiple areas mode
                    elif hasattr(new_state, 'detection_results'):
                        should_click = any(new_state.detection_results)
                    else:
                        should_click = False
                    
                    # Update the state
                    new_state.set_should_click(should_click)
                    
                    # Return the updated state
                    return new_state
                else:
                    # Not an AgentState object - convert to dictionary
                    state_dict = dict(new_state)
                    
                    # Apply the decision logic
                    if "detection_results" in state_dict:
                        should_click = any(state_dict["detection_results"])
                    else:
                        should_click = state_dict.get("both_words_detected", False)
                    
                    # Update and return the dictionary
                    state_dict["should_click"] = should_click
                    return state_dict
            except (AttributeError, TypeError):
                # Fallback - return the input state
                return state
    
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
        
        # Check if we're dealing with a dictionary or an AgentState object
        if isinstance(new_state, dict):
            # Dictionary input
            # Check if we should click
            if new_state["should_click"]:
                # Execute the click
                action_result = mouse_controller.click_at_position()
                
                # Update the state
                new_state["action_history"] = new_state["action_history"] + [action_result]
            
            # Return the state as a dictionary
            return new_state
        else:
            # Handle AgentState object (for tests)
            try:
                if hasattr(new_state, 'update_action'):
                    # Check if we should click
                    if getattr(new_state, 'should_click', False):
                        # Execute the click
                        action_result = mouse_controller.click_at_position()
                        
                        # Update the state
                        new_state.update_action(action_result)
                    
                    # Return the updated state
                    return new_state
                else:
                    # Not an AgentState object - return as is
                    return new_state
            except (AttributeError, TypeError):
                # Fallback - return the input state
                return state 