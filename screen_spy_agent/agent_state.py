"""
AgentState module for maintaining the state of the agent.
"""


class AgentState:
    """
    Class for maintaining the state of the agent.
    
    Attributes:
        detection_history: List of detection results (True/False).
        action_history: List of action results (True/False).
        current_screenshot: Path to the current screenshot.
        both_words_detected: Whether both 'Accept' and 'Reject' were detected.
        should_click: Whether the agent should click the mouse.
        history_limit: Maximum number of items to keep in history lists.
    """
    
    def __init__(self, history_limit=100):
        """
        Initialize an AgentState.
        
        Args:
            history_limit: Maximum number of items to keep in history lists.
        """
        self.detection_history = []
        self.action_history = []
        self.current_screenshot = ""
        self.both_words_detected = False
        self.should_click = False
        self.history_limit = history_limit
    
    def update_detection(self, detection_result):
        """
        Update the detection state.
        
        Args:
            detection_result: Whether both words were detected (True/False).
        """
        self.both_words_detected = detection_result
        self.detection_history.append(detection_result)
        
        # Limit history size
        if len(self.detection_history) > self.history_limit:
            self.detection_history = self.detection_history[-self.history_limit:]
    
    def update_action(self, action_taken):
        """
        Update the action state.
        
        Args:
            action_taken: Whether the action was successful (True/False).
        """
        self.action_history.append(action_taken)
        
        # Limit history size
        if len(self.action_history) > self.history_limit:
            self.action_history = self.action_history[-self.history_limit:]
    
    def set_current_screenshot(self, path):
        """
        Set the path to the current screenshot.
        
        Args:
            path: The path to the screenshot.
        """
        self.current_screenshot = path
    
    def set_should_click(self, should_click):
        """
        Set whether the agent should click the mouse.
        
        Args:
            should_click: Whether the agent should click (True/False).
        """
        self.should_click = should_click
    
    def get_state(self):
        """
        Get the current state as a dictionary.
        
        Returns:
            dict: The current state.
        """
        return {
            "detection_history": self.detection_history,
            "action_history": self.action_history,
            "current_screenshot": self.current_screenshot,
            "both_words_detected": self.both_words_detected,
            "should_click": self.should_click
        } 