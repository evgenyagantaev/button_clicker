import pytest
from unittest.mock import MagicMock, patch
from screen_spy_agent.cyclic_prompt_manager import CyclicPromptManager


class TestCyclicPromptManager:
    """Tests for the CyclicPromptManager class."""

    def test_init(self):
        """Test initialization of CyclicPromptManager with default values."""
        manager = CyclicPromptManager()
        assert manager.cyclic_prompt == ""
        assert hasattr(manager, 'copy_to_clipboard')
        assert hasattr(manager, 'paste_from_clipboard')

    def test_init_with_prompt(self):
        """Test initialization with a custom prompt."""
        test_prompt = "This is a test prompt\nWith multiple lines"
        manager = CyclicPromptManager(test_prompt)
        assert manager.cyclic_prompt == test_prompt

    def test_set_get_cyclic_prompt(self):
        """Test setting and getting the cyclic prompt."""
        manager = CyclicPromptManager()
        
        # Test with empty prompt
        manager.set_cyclic_prompt("")
        assert manager.get_cyclic_prompt() == ""
        
        # Test with single-line prompt
        single_line = "This is a single line prompt"
        manager.set_cyclic_prompt(single_line)
        assert manager.get_cyclic_prompt() == single_line
        
        # Test with multi-line prompt
        multi_line = "This is a multi-line prompt\nWith several\nLines of text"
        manager.set_cyclic_prompt(multi_line)
        assert manager.get_cyclic_prompt() == multi_line

    @patch('pyperclip.copy')
    def test_copy_to_clipboard(self, mock_copy):
        """Test copying the cyclic prompt to clipboard."""
        test_prompt = "Test prompt for clipboard"
        manager = CyclicPromptManager(test_prompt)
        
        manager.copy_to_clipboard()
        mock_copy.assert_called_once_with(test_prompt)

    @patch('pyperclip.paste')
    def test_paste_from_clipboard(self, mock_paste):
        """Test pasting from clipboard to the cyclic prompt."""
        clipboard_content = "Content from clipboard"
        mock_paste.return_value = clipboard_content
        
        manager = CyclicPromptManager()
        manager.paste_from_clipboard()
        
        assert manager.get_cyclic_prompt() == clipboard_content
        mock_paste.assert_called_once()

    @patch('pyperclip.copy')
    @patch('pyperclip.paste')
    def test_clipboard_round_trip(self, mock_paste, mock_copy):
        """Test a full round-trip from setting prompt to clipboard and back."""
        original_prompt = "Original prompt"
        modified_prompt = "Modified prompt"
        
        # Set up mocks
        mock_paste.return_value = modified_prompt
        
        # Create manager with original prompt
        manager = CyclicPromptManager(original_prompt)
        
        # Copy to clipboard
        manager.copy_to_clipboard()
        mock_copy.assert_called_once_with(original_prompt)
        
        # Clear the prompt
        manager.set_cyclic_prompt("")
        assert manager.get_cyclic_prompt() == ""
        
        # Paste from clipboard (which now has modified_prompt)
        manager.paste_from_clipboard()
        assert manager.get_cyclic_prompt() == modified_prompt
        mock_paste.assert_called_once() 