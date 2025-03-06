"""
MouseController module for simulating mouse clicks.
"""

import pyautogui


class MouseController:
    """
    Class for controlling mouse movements and clicks.
    
    Attributes:
        target_x: The x-coordinate to click at.
        target_y: The y-coordinate to click at.
    """
    
    def __init__(self, target_x, target_y):
        """
        Initialize a MouseController with the given target coordinates.
        
        Args:
            target_x: The x-coordinate to click at.
            target_y: The y-coordinate to click at.
            
        Raises:
            ValueError: If coordinates are negative.
        """
        if target_x < 0 or target_y < 0:
            raise ValueError("Coordinates must be non-negative")
        
        self.target_x = target_x
        self.target_y = target_y
    
    def click_at_position(self):
        """
        Simulate a mouse click at the target position.
        
        Returns:
            bool: True if the click was successful, False otherwise.
        """
        try:
            pyautogui.click(x=self.target_x, y=self.target_y)
            return True
        except Exception as e:
            print(f"Error clicking at position ({self.target_x}, {self.target_y}): {e}")
            return False
    
    @staticmethod
    def get_screen_size():
        """
        Get the screen dimensions.
        
        Returns:
            tuple: A tuple containing the screen width and height.
        """
        return pyautogui.size() 