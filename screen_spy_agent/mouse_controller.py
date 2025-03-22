"""
MouseController module for simulating mouse clicks.
"""

import pyautogui
import time
import pyperclip


class MouseController:
    """
    Class for controlling mouse movements and clicks.
    
    Attributes:
        target_x: The x-coordinate to click at.
        target_y: The y-coordinate to click at.
        click_coordinates: A list of lists where each inner list contains coordinate pairs [x, y] for each area.
        vertical_shift: Vertical shift to apply to click coordinates.
    """
    
    def __init__(self, target_x=0, target_y=0):
        """
        Initialize a MouseController with the given target coordinates.
        
        Args:
            target_x: The default x-coordinate to click at.
            target_y: The default y-coordinate to click at.
            
        Raises:
            ValueError: If coordinates are negative.
        """
        if target_x < 0 or target_y < 0:
            raise ValueError("Coordinates must be non-negative")
        
        # Store target coordinates for backward compatibility
        self.target_x = target_x
        self.target_y = target_y
        
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
    
    def click_at_coordinates(self, x, y):
        """
        Simulate a mouse click at the specified coordinates.
        This method is a wrapper around the click method for backward compatibility.
        
        Args:
            x: The x-coordinate to click at.
            y: The y-coordinate to click at.
            
        Returns:
            bool: True if click was successful, False otherwise.
        """
        return self.click(x, y)
    
    def click(self, x, y):
        """
        Simulate a mouse click at the specified position.
        
        Args:
            x: The x-coordinate to click at.
            y: The y-coordinate to click at.
            
        Returns:
            bool: True if click was successful, False otherwise.
        """
        try:
            adjusted_y = y + self.vertical_shift
            print(f"Clicking at position ({x}, {adjusted_y}) with vertical shift {self.vertical_shift}")
            pyautogui.click(x=x, y=adjusted_y)
            return True
        except Exception as e:
            print(f"Error clicking at position ({x}, {y}): {e}")
            return False
    
    def paste_from_clipboard(self, use_context_menu=False):
        """
        Simulate pasting content from the clipboard.
        Uses a more reliable approach to avoid triggering microphone activation.
        
        Args:
            use_context_menu: Whether to prioritize context menu pasting over keyboard shortcuts
            
        Returns:
            bool: True if paste was successful, False otherwise.
        """
        try:
            print("Attempting to paste from clipboard")
            
            # Use context menu paste first to avoid microphone activation
            if use_context_menu:
                print("Using context menu paste as primary method")
                if self.context_menu_paste():
                    return True
                # If context menu paste fails, fall back to keyboard shortcut
                print("Context menu paste failed, trying keyboard shortcut")
            
            # # Method using keyboard shortcut (only as fallback by default)
            # print("Using keyboard shortcut method")
            # pyautogui.keyDown('ctrl')
            # time.sleep(0.3)  # Increased delay before pressing V
            # pyautogui.press('v')
            # time.sleep(0.3)  # Increased delay before releasing Ctrl
            # pyautogui.keyUp('ctrl')
            # # Add a small delay after pasting
            # time.sleep(0.5)

            # Method 2: Alternative keyboard shortcut for special cases
            # Some applications might require different shortcuts for paste
            print("Trying alternative paste method (Shift+Insert)")
            pyautogui.keyDown('shift')
            time.sleep(0.3)
            pyautogui.press('insert')
            time.sleep(0.3)
            pyautogui.keyUp('shift')
            time.sleep(0.5)
                

            return True
            
        except Exception as e:
            print(f"Error pasting from clipboard: {e}")
            return False
    
    def type_text(self, text, x=None, y=None):
        """
        Type text character by character.
        
        Args:
            text: The text to type
            x: X-coordinate for clicking to focus (optional)
            y: Y-coordinate for clicking to focus (optional)
            
        Returns:
            bool: True if typing was successful, False otherwise.
        """
        try:
            # Click to ensure focus if coordinates are provided
            if x is not None and y is not None:
                print(f"Clicking at coordinates ({x}, {y}) to ensure focus")
                pyautogui.click(x=x, y=y)
                time.sleep(0.5)
            
            print(f"Typing text character by character (length: {len(text)})")
            pyautogui.typewrite(text, interval=0.1)  # Type with a small delay between characters
            return True
        except Exception as e:
            print(f"Error typing text: {e}")
            return False
    
    def type_text_char_by_char(self, text, interval=0.1, x=None, y=None):
        """
        Type text character by character without using clipboard.
        
        Args:
            text: The text to type
            interval: Time between keystrokes in seconds
            x: X-coordinate for clicking to focus (optional)
            y: Y-coordinate for clicking to focus (optional)
            
        Returns:
            bool: True if typing was successful, False otherwise.
        """
        try:
            # Click to ensure focus if coordinates are provided
            if x is not None and y is not None:
                print(f"Clicking at coordinates ({x}, {y}) to ensure focus")
                pyautogui.click(x=x, y=y)
                time.sleep(0.5)
            
            print(f"Typing text character by character (length: {len(text)})")
            pyautogui.typewrite(text, interval=interval)
            return True
        except Exception as e:
            print(f"Error typing text character by character: {e}")
            return False
    
    def press_key(self, key):
        """
        Simulate pressing a keyboard key.
        
        Args:
            key: The key to press (e.g., 'enter', 'esc', 'tab', etc.)
            
        Returns:
            bool: True if key press was successful, False otherwise.
        """
        try:
            print(f"Pressing key: {key}")
            pyautogui.press(key)
            return True
        except Exception as e:
            print(f"Error pressing key {key}: {e}")
            return False
    
    def context_menu_paste(self, x=None, y=None):
        """
        Paste using the context menu (right-click and select paste).
        
        Args:
            x: Optional x-coordinate to right-click at
            y: Optional y-coordinate to right-click at
            
        Returns:
            bool: True if paste was successful, False otherwise.
        """
        try:
            print("Attempting to paste using context menu")
            
            # If coordinates are provided, right-click there
            if x is not None and y is not None:
                pyautogui.rightClick(x=x, y=y)
            else:
                # Right-click at current mouse position
                pyautogui.rightClick()
            
            # Wait for context menu to appear
            time.sleep(0.5)
            
            # Press 'P' or 'V' which is often the shortcut for paste in context menus
            # Different applications might use different shortcuts, so we try both
            print("Pressing 'p' shortcut for paste in context menu")
            pyautogui.press('p')
            
            return True
        except Exception as e:
            print(f"Error using context menu paste: {e}")
            return False
    
    @staticmethod
    def get_screen_size():
        """
        Get the screen dimensions.
        
        Returns:
            tuple: A tuple containing the screen width and height.
        """
        return pyautogui.size()
    
    def copy_paste_text(self, text, x=None, y=None):
        """
        Copy text to clipboard and paste it at the current position or specified coordinates.
        
        Args:
            text: The text to copy to clipboard and paste
            x: Optional x-coordinate to click before pasting
            y: Optional y-coordinate to click before pasting
            
        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            print(f"Copying text to clipboard (length: {len(text)})")
            # Copy the text to clipboard
            pyperclip.copy(text)
            
            # If coordinates are provided, click to focus
            if x is not None and y is not None:
                print(f"Clicking at coordinates ({x}, {y}) to ensure focus")
                self.click(x, y)
                time.sleep(0.5)
            
            # Paste from clipboard
            print("Pasting text from clipboard")
            return self.paste_from_clipboard()
            
        except Exception as e:
            print(f"Error in copy_paste_text: {e}")
            return False 