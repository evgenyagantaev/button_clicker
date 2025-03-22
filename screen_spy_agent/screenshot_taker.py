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
    
    def capture_screenshot(self, x1=None, y1=None, x2=None, y2=None):
        """
        Capture a screenshot of the defined screen region or a custom region if coordinates are provided.
        
        Args:
            x1: Optional custom left coordinate. If None, uses self.x1.
            y1: Optional custom top coordinate. If None, uses self.y1.
            x2: Optional custom right coordinate. If None, uses self.x2.
            y2: Optional custom bottom coordinate. If None, uses self.y2.
            
        Returns:
            PIL.Image: The captured screenshot.
        """
        # Use the provided coordinates if available, otherwise use the instance's coordinates
        x1 = x1 if x1 is not None else self.x1
        y1 = y1 if y1 is not None else self.y1
        x2 = x2 if x2 is not None else self.x2
        y2 = y2 if y2 is not None else self.y2
        
        return ImageGrab.grab(bbox=(x1, y1, x2, y2))
    
    def save_screenshot(self, image, path=None):
        """
        Save a screenshot.
        
        Args:
            image: The PIL.Image to save.
            path: Optional path to save the image to. If not provided, a default filename will be used.
            
        Returns:
            str: The absolute path to the saved image.
        """
        if path is None:
            path = self.get_screenshot_path()
        
        abs_path = os.path.abspath(path)
        image.save(abs_path)
        return abs_path
    
    def get_screenshot_path(self):
        """
        Get the path for the screenshot using a timestamp.
        
        Returns:
            str: The filename for the screenshot.
        """
        # timestamp = time.strftime("%Y%m%d_%H%M%S")
        # return os.path.abspath(f"screenshot_{timestamp}.jpg") 
        return os.path.abspath("current_screenshot.jpg")