import pyperclip

class CyclicPromptManager:
    """
    Manages cyclic prompts for the ScreenSpyAgent.
    
    This class handles the storage of cyclic prompts and provides
    functionality to interact with the system clipboard for text operations.
    """
    
    def __init__(self, cyclic_prompt=""):
        """
        Initialize a new CyclicPromptManager.
        
        Args:
            cyclic_prompt (str): The initial cyclic prompt text. Defaults to empty string.
        """
        self.cyclic_prompt = cyclic_prompt
    
    def set_cyclic_prompt(self, prompt):
        """
        Set the cyclic prompt value.
        
        Args:
            prompt (str): The new cyclic prompt text.
        """
        self.cyclic_prompt = prompt
    
    def get_cyclic_prompt(self):
        """
        Get the current cyclic prompt value.
        
        Returns:
            str: The current cyclic prompt text.
        """
        return self.cyclic_prompt
    
    def copy_to_clipboard(self):
        """
        Copy the current cyclic prompt to the system clipboard.
        """
        pyperclip.copy(self.cyclic_prompt)
    
    def paste_from_clipboard(self):
        """
        Set the cyclic prompt from the current system clipboard content.
        """
        self.cyclic_prompt = pyperclip.paste()

    def execute_start_sequence(self, mouse_controller, pause_duration=2):
        """
        Execute the start sequence of actions for the cyclic prompt workflow.
        
        This includes:
        1. Clicking at position [1818, 46] (new chat)
        2. Pausing for specified duration 
        3. Clicking at position [1419, 108] (focus prompt field)
        4. Pausing for specified duration
        5. Copying the cyclic prompt to clipboard
        6. Pasting to the focused field (assumes OS paste operation)
        7. Pausing for specified duration
        8. Clicking at position [1874, 141] (send button)
        
        Args:
            mouse_controller: The mouse controller to use for clicking operations
            pause_duration (int): Duration in seconds to pause between actions. Defaults to 2 seconds.
        """
        import time
        
        # Click to start new chat
        mouse_controller.click_at_coordinates(1818, 46)
        time.sleep(pause_duration)
        
        # Click to focus prompt input field
        mouse_controller.click_at_coordinates(1419, 108)
        time.sleep(pause_duration)
        
        # Copy prompt to clipboard and paste
        self.copy_to_clipboard()
        mouse_controller.paste_from_clipboard()
        time.sleep(pause_duration)
        
        # Click send button
        mouse_controller.click_at_coordinates(1874, 141) 