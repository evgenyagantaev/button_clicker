"""
MouseController module for simulating mouse clicks.
"""

import pyautogui
import time


class MouseController:
    """
    Class for controlling mouse movements and clicks.
    
    Attributes:
        click_coordinates: A list of lists where each inner list contains coordinate pairs [x, y] for each area.
        vertical_shift: Vertical shift to apply to click coordinates.
    """
    
    def __init__(self, target_x=0, target_y=0):
        """
        Initialize a MouseController with the given target coordinates.
        
        Args:
            target_x: The default x-coordinate to click at (legacy).
            target_y: The default y-coordinate to click at (legacy).
            
        Raises:
            ValueError: If coordinates are negative.
        """
        if target_x < 0 or target_y < 0:
            raise ValueError("Coordinates must be non-negative")
        
        # Initialize with a default click for each of the 4 areas
        self.click_coordinates = [
            [],  # Area 0 - no clicks by default
            [[target_x, target_y]],  # Area 1 - one click at the target coordinates
            [[target_x, target_y]],  # Area 2 - one click at the target coordinates
            [[target_x, target_y]]   # Area 3 - one click at the target coordinates
        ]
        
        self.vertical_shift = 0
    
    def set_click_coordinates(self, area_index, coordinates):
        """
        Set the click coordinates for a specific area.
        
        Args:
            area_index: The index of the area (0-3).
            coordinates: A list of coordinate pairs, where each pair is [x, y].
            
        Raises:
            ValueError: If area_index is out of range or coordinates are invalid.
        """
        if area_index < 0 or area_index > 3:
            raise ValueError("Area index must be between 0 and 3")
        
        if not isinstance(coordinates, list):
            raise ValueError("Coordinates must be a list of [x, y] pairs")
        
        for coord in coordinates:
            if not isinstance(coord, list) or len(coord) != 2:
                raise ValueError("Each coordinate must be a list of [x, y]")
            if coord[0] < 0 or coord[1] < 0:
                raise ValueError("Coordinates must be non-negative")
        
        self.click_coordinates[area_index] = coordinates
    
    def set_vertical_shift(self, shift):
        """
        Set the vertical shift to apply to click coordinates.
        
        Args:
            shift: The vertical shift value.
        """
        self.vertical_shift = shift
    
    def click_at_position(self, area_index=1):
        """
        Simulate a mouse click at the target position(s) for the specified area.
        
        Args:
            area_index: The index of the area (0-3).
            
        Returns:
            bool: True if all clicks were successful, False otherwise.
        """
        if area_index < 0 or area_index > 3:
            raise ValueError("Area index must be between 0 and 3")
        
        # Get the click coordinates for this area
        coordinates = self.click_coordinates[area_index]
        
        # If there are no coordinates, return successfully (no clicks needed)
        if len(coordinates) == 0:
            print(f"No clicks defined for area {area_index}")
            return True
        
        success = True
        
        try:
            for i, coord in enumerate(coordinates):
                x, y = coord[0], coord[1] + self.vertical_shift
                print(f"Clicking at position ({x}, {y}) with vertical shift {self.vertical_shift}")
                pyautogui.click(x=x, y=y)
                
                # Add a 2-second pause between clicks, but not after the last click
                if i < len(coordinates) - 1:
                    print("Waiting 2 seconds before the next click...")
                    time.sleep(2)
            
            return success
        
        except Exception as e:
            print(f"Error clicking at positions for area {area_index}: {e}")
            return False
    
    @staticmethod
    def get_screen_size():
        """
        Get the screen dimensions.
        
        Returns:
            tuple: A tuple containing the screen width and height.
        """
        return pyautogui.size() 