"""
ScreenshotTaker module for capturing and saving screenshots of screen regions.
"""

import os
import time
import PIL.ImageGrab as ImageGrab


class ScreenshotTaker:
    """
    Class for capturing screenshots of a specific screen region.
    
    Attributes:
        x1: The left coordinate of the screen region.
        y1: The top coordinate of the screen region.
        x2: The right coordinate of the screen region.
        y2: The bottom coordinate of the screen region.
        interval: The interval in seconds between screenshots.
    """
    
    def __init__(self, x1, y1, x2, y2, interval):
        """
        Initialize a ScreenshotTaker with the given screen region and interval.
        
        Args:
            x1: The left coordinate of the screen region.
            y1: The top coordinate of the screen region.
            x2: The right coordinate of the screen region.
            y2: The bottom coordinate of the screen region.
            interval: The interval in seconds between screenshots.
            
        Raises:
            ValueError: If interval is less than or equal to 0.
        """
        # Ensure x1 < x2 and y1 < y2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
            
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        
        if interval <= 0:
            raise ValueError("Interval must be greater than 0")
        self.interval = interval
    
    def capture_screenshot(self, x1, y1, x2, y2):
        """
        Capture a screenshot of the defined screen region.
        
        Returns:
            PIL.Image: The captured screenshot.
        """
        return ImageGrab.grab(bbox=(x1, y1, x2, y2))
    
    def save_screenshot(self, image):
        """
        Save a screenshot with a fixed filename.
        
        Args:
            image: The PIL.Image to save.
            
        Returns:
            str: The absolute path to the saved image.
        """
        filename = "current_screenshot.jpg"
        path = os.path.abspath(filename)
        image.save(path)
        return path
    
    def get_screenshot_path(self):
        """
        Get the fixed filename for the screenshot.
        
        Returns:
            str: The filename for the screenshot.
        """
        return "current_screenshot.jpg" 