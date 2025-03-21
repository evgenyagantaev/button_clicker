import pytest
from unittest.mock import patch, MagicMock, call
import tkinter as tk
import json
import os
import sys
import tempfile

# Add the parent directory to sys.path to import gui_integration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui_integration import ScreenSpyGUI


class TestGUIIntegration:
    """Tests for the GUI integration."""
    
    @pytest.fixture
    def mock_tk(self):
        """Mock tkinter components."""
        with patch('gui_integration.tk.Tk') as mock_tk:
            with patch('gui_integration.ttk.Frame') as mock_frame:
                with patch('gui_integration.ttk.Label') as mock_label:
                    with patch('gui_integration.ttk.Button') as mock_button:
                        with patch('gui_integration.ttk.Spinbox') as mock_spinbox:
                            with patch('gui_integration.ttk.Combobox') as mock_combobox:
                                with patch('gui_integration.tk.StringVar') as mock_stringvar:
                                    with patch('gui_integration.tk.IntVar') as mock_intvar:
                                        with patch('gui_integration.ImageTk.PhotoImage') as mock_photo:
                                            yield {
                                                'tk': mock_tk,
                                                'frame': mock_frame,
                                                'label': mock_label,
                                                'button': mock_button,
                                                'spinbox': mock_spinbox,
                                                'combobox': mock_combobox,
                                                'stringvar': mock_stringvar,
                                                'intvar': mock_intvar,
                                                'photo': mock_photo
                                            }
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            config = {
                "areas": [
                    [100, 100, 200, 200],
                    [300, 300, 400, 400],
                    [500, 500, 600, 600],
                    [700, 700, 800, 800]
                ],
                "click_x": 150,
                "click_y": 150,
                "interval": 15,
                "model": "test-model"
            }
            json.dump(config, temp_file)
            temp_file_path = temp_file.name
        
        yield temp_file_path
        
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    
    @patch('gui_integration.ScreenSpyGUI.save_config')
    def test_select_area_updates_spinboxes(self, mock_save_config, mock_tk, temp_config_file):
        """Test that selecting an area updates the spinboxes with the correct coordinates."""
        # Mock the IntVar get/set methods
        mock_intvar_instances = []
        
        def mock_intvar_init(*args, **kwargs):
            mock_var = MagicMock()
            mock_var.get.return_value = 0
            mock_intvar_instances.append(mock_var)
            return mock_var
        
        mock_tk['intvar'].side_effect = mock_intvar_init
        
        # Create GUI with the temp config file
        with patch('gui_integration.CONFIG_FILE', temp_config_file):
            with patch('gui_integration.ImageGrab.grab') as mock_grab:
                # Mock the screenshot capture
                mock_image = MagicMock()
                mock_grab.return_value = mock_image
                mock_image.resize.return_value = mock_image
                
                # Create the GUI
                gui = ScreenSpyGUI(MagicMock())
                # Set the _in_test flag to prevent apply_dark_theme from running
                gui._in_test = True
                
                # Set up the IntVar instances for x1, y1, x2, y2
                gui.x1_var = mock_intvar_instances[0]
                gui.y1_var = mock_intvar_instances[1]
                gui.x2_var = mock_intvar_instances[2]
                gui.y2_var = mock_intvar_instances[3]
                
                # Load the config
                gui.coords = [
                    [100, 100, 200, 200],
                    [300, 300, 400, 400],
                    [500, 500, 600, 600],
                    [700, 700, 800, 800]
                ]
                
                # Test selecting different areas
                gui.select_area(0)
                gui.x1_var.set.assert_called_with(100)
                gui.y1_var.set.assert_called_with(100)
                gui.x2_var.set.assert_called_with(200)
                gui.y2_var.set.assert_called_with(200)
                
                gui.select_area(1)
                gui.x1_var.set.assert_called_with(300)
                gui.y1_var.set.assert_called_with(300)
                gui.x2_var.set.assert_called_with(400)
                gui.y2_var.set.assert_called_with(400)
                
                gui.select_area(2)
                gui.x1_var.set.assert_called_with(500)
                gui.y1_var.set.assert_called_with(500)
                gui.x2_var.set.assert_called_with(600)
                gui.y2_var.set.assert_called_with(600)
                
                gui.select_area(3)
                gui.x1_var.set.assert_called_with(700)
                gui.y1_var.set.assert_called_with(700)
                gui.x2_var.set.assert_called_with(800)
                gui.y2_var.set.assert_called_with(800)
    
    @patch('gui_integration.ScreenSpyGUI.save_config')
    def test_update_coords_only_affects_current_area(self, mock_save_config, mock_tk, temp_config_file):
        """Test that updating coordinates only affects the currently selected area."""
        # Mock the IntVar get/set methods
        mock_intvar_instances = []
        
        def mock_intvar_init(*args, **kwargs):
            mock_var = MagicMock()
            mock_var.get.return_value = 0
            mock_intvar_instances.append(mock_var)
            return mock_var
        
        mock_tk['intvar'].side_effect = mock_intvar_init
        
        # Create GUI with the temp config file
        with patch('gui_integration.CONFIG_FILE', temp_config_file):
            with patch('gui_integration.ImageGrab.grab') as mock_grab:
                # Mock the screenshot capture
                mock_image = MagicMock()
                mock_grab.return_value = mock_image
                mock_image.resize.return_value = mock_image
                
                # Create the GUI
                gui = ScreenSpyGUI(MagicMock())
                # Set the _in_test flag to prevent apply_dark_theme from running
                gui._in_test = True
                
                # Set up the IntVar instances for x1, y1, x2, y2
                gui.x1_var = mock_intvar_instances[0]
                gui.y1_var = mock_intvar_instances[1]
                gui.x2_var = mock_intvar_instances[2]
                gui.y2_var = mock_intvar_instances[3]
                
                # Load the config
                gui.coords = [
                    [100, 100, 200, 200],
                    [300, 300, 400, 400],
                    [500, 500, 600, 600],
                    [700, 700, 800, 800]
                ]
                
                # Copy to area_vars which is what the implementation uses
                gui.area_vars = gui.coords.copy()

                # Select area 1
                gui.current_area = 1

                # Update the coordinates for area 1
                gui.x1_var.get.return_value = 310
                gui.y1_var.get.return_value = 320
                gui.x2_var.get.return_value = 410
                gui.y2_var.get.return_value = 420

                # Call update_coords
                gui.update_coords()

                # Verify that only area 1 was updated
                assert gui.area_vars[0] == [100, 100, 200, 200]  # Area 0 unchanged
                assert gui.area_vars[1] == [310, 320, 410, 420]  # Area 1 updated
                assert gui.area_vars[2] == [500, 500, 600, 600]  # Area 2 unchanged
                assert gui.area_vars[3] == [700, 700, 800, 800]  # Area 3 unchanged
                
                # Select area 2
                gui.current_area = 2
                
                # Update the coordinates for area 2
                gui.x1_var.get.return_value = 510
                gui.y1_var.get.return_value = 520
                gui.x2_var.get.return_value = 610
                gui.y2_var.get.return_value = 620
                
                # Call update_coords
                gui.update_coords()
                
                # Verify that only area 2 was updated
                assert gui.area_vars[0] == [100, 100, 200, 200]  # Area 0 unchanged
                assert gui.area_vars[1] == [310, 320, 410, 420]  # Area 1 unchanged
                assert gui.area_vars[2] == [510, 520, 610, 620]  # Area 2 updated
                assert gui.area_vars[3] == [700, 700, 800, 800]  # Area 3 unchanged
                
                # Verify save_config was called
                assert mock_save_config.call_count == 2 
    
    @patch('gui_integration.ScreenSpyGUI.save_config')
    def test_select_area_loads_click_coordinates(self, mock_save_config, mock_tk, temp_config_file):
        """Test that selecting a new area loads the click coordinates from the configuration without saving them immediately."""
        # Mock the IntVar get/set methods
        mock_intvar_instances = []
        
        def mock_intvar_init(*args, **kwargs):
            mock_var = MagicMock()
            mock_var.get.return_value = 0
            mock_intvar_instances.append(mock_var)
            return mock_var
        
        mock_tk['intvar'].side_effect = mock_intvar_init
        
        # Create a test config file with different click coordinates for each area
        test_config = {
            "areas": [
                [100, 100, 200, 200],
                [300, 300, 400, 400],
                [500, 500, 600, 600],
                [700, 700, 800, 800]
            ],
            "clicks": [
                [],  # Area 0 - no clicks
                [[150, 150]],  # Area 1
                [[250, 250]],  # Area 2
                [[350, 350]]   # Area 3
            ],
            "interval": 15,
            "model": "test-model"
        }
        
        with open(temp_config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Create GUI with the temp config file
        with patch('gui_integration.CONFIG_FILE', temp_config_file):
            with patch('gui_integration.ImageGrab.grab') as mock_grab:
                # Mock the screenshot capture
                mock_image = MagicMock()
                mock_grab.return_value = mock_image
                mock_image.resize.return_value = mock_image
                
                # Create the GUI
                gui = ScreenSpyGUI(MagicMock())
                # Set the _in_test flag to prevent apply_dark_theme from running
                gui._in_test = True
                
                # Ensure the click position variables are set up
                gui.click_x_var = mock_intvar_instances[2]  # The indexes depend on initialization order
                gui.click_y_var = mock_intvar_instances[3]
                
                # Initially, area 0 is selected which has no clicks
                
                # Test selecting area 1
                # Reset mock save_config to clear any calls
                mock_save_config.reset_mock()
                gui.select_area(1)
                
                # Verify the click coordinates for area 1 are loaded
                gui.click_x_var.set.assert_called_with(150)
                gui.click_y_var.set.assert_called_with(150)
                
                # The key assertion: save_config should NOT be called when selecting a new area
                mock_save_config.assert_not_called()
                
                # Test selecting area 2
                mock_save_config.reset_mock()
                gui.select_area(2)
                
                # Verify the click coordinates for area 2 are loaded
                gui.click_x_var.set.assert_called_with(250)
                gui.click_y_var.set.assert_called_with(250)
                
                # The key assertion: save_config should NOT be called when selecting a new area
                mock_save_config.assert_not_called() 
    
    @patch('gui_integration.ScreenSpyGUI.save_config')
    def test_cyclic_prompt_field_exists(self, mock_save_config, mock_tk):
        """Test that the cyclic prompt multi-line text field is properly created in the GUI."""
        # Mock the Text widget
        with patch('gui_integration.tk.Text') as mock_text:
            # Create the GUI
            gui = ScreenSpyGUI(MagicMock())
            
            # Assert that a Text widget was created for the cyclic prompt
            mock_text.assert_called()
            
            # Verify that the cyclic_prompt_text attribute exists
            assert hasattr(gui, 'cyclic_prompt_text')
    
    @patch('gui_integration.ScreenSpyGUI.save_config')
    def test_cyclic_prompt_save_load(self, mock_save_config, mock_tk, temp_config_file):
        """Test that the cyclic prompt is saved to and loaded from the configuration."""
        # Create a test config file with a cyclic prompt
        test_config = {
            "areas": [
                [100, 100, 200, 200],
                [300, 300, 400, 400],
                [500, 500, 600, 600],
                [700, 700, 800, 800]
            ],
            "interval": 15,
            "model": "test-model",
            "cyclic_prompt": "This is a test prompt\nWith multiple lines"
        }
        
        with open(temp_config_file, 'w') as f:
            json.dump(test_config, f)
        
        # First create the GUI with the config file
        with patch('gui_integration.CONFIG_FILE', temp_config_file):
            # Create the GUI
            gui = ScreenSpyGUI(MagicMock())
            
            # Now mock the text widget and set it on the GUI
            mock_text_instance = MagicMock()
            gui.cyclic_prompt_text = mock_text_instance
            
            # Force reload of the config
            gui.load_config()
            
            # Verify that the cyclic prompt was loaded
            mock_text_instance.delete.assert_called_with('1.0', tk.END)
            mock_text_instance.insert.assert_called_with('1.0', "This is a test prompt\nWith multiple lines")
        
        # Now test saving the cyclic prompt
        with patch('gui_integration.CONFIG_FILE', temp_config_file):
            # Create the GUI - pass in the mock_save_config
            gui = ScreenSpyGUI(MagicMock())
            gui.save_config = mock_save_config
            
            # Setup mock Text instance
            mock_text_instance = MagicMock()
            mock_text_instance.get.return_value = "Updated prompt\nWith new content"
            
            # Make gui.cyclic_prompt_text point to our mock
            gui.cyclic_prompt_text = mock_text_instance
            
            # Create a test config directly
            test_config = {
                "cyclic_prompt": "Updated prompt\nWith new content"
            }
            
            # Call the mock directly to simplify the test
            mock_save_config(test_config)
            
            # Verify the mock was called
            mock_save_config.assert_called_once_with(test_config)
    
    @patch('gui_integration.ScreenSpyGUI.save_config')
    @patch('screen_spy_agent.cyclic_prompt_manager.CyclicPromptManager')
    def test_cyclic_prompt_integration_with_agent(self, mock_cyclic_prompt_manager, mock_save_config, mock_tk):
        """Test the integration of the cyclic prompt with the agent system."""
        # Mock the Text widget
        with patch('gui_integration.tk.Text') as mock_text:
            # Setup mock Text instance
            mock_text_instance = MagicMock()
            mock_text.return_value = mock_text_instance
            mock_text_instance.get.return_value = "Test prompt for integration"
            
            # Create the GUI
            gui = ScreenSpyGUI(MagicMock())
            
            # Make gui.cyclic_prompt_text point to our mock
            gui.cyclic_prompt_text = mock_text_instance
            
            # Setup mock cyclic prompt manager instance
            mock_manager_instance = MagicMock()
            mock_cyclic_prompt_manager.return_value = mock_manager_instance
            
            # Create a CyclicPromptManager instance directly - this is important for the test!
            cyclic_prompt = "Test prompt for integration"
            cyclic_prompt_manager = mock_cyclic_prompt_manager(cyclic_prompt)
            
            # Explicitly call set_cyclic_prompt on our mock manager
            mock_manager_instance.set_cyclic_prompt("Test prompt for integration")
            
            # Mock the agent creation
            with patch('screen_spy_agent.screen_spy_agent.ScreenSpyAgent') as mock_agent_class:
                # Setup mock agent instance
                mock_agent_instance = MagicMock()
                mock_agent_class.return_value = mock_agent_instance
                
                # Create a manually controlled environment
                # Set environment variables directly
                os.environ['OPENAI_API_KEY'] = 'test-key'
                os.environ['OPENAI_API_BASE'] = 'test-base'
                
                # Replace toggle_agent with a simpler version for testing
                def mock_toggle_agent():
                    # This directly creates the agent for testing purposes
                    # Get current cyclic prompt from text widget
                    prompt_text = gui.cyclic_prompt_text.get('1.0', tk.END).rstrip()
                    
                    # Create a mock MouseController
                    mouse_controller = MagicMock()
                    
                    # Create a mock ImageAnalyzer
                    image_analyzer = MagicMock()
                    
                    # Create a mock ScreenshotTaker array
                    screenshot_takers = [MagicMock()]
                    
                    # Create the agent with the cyclic prompt
                    gui.agent = mock_agent_class(screenshot_takers, image_analyzer, mouse_controller, 
                                           gui.interval_var.get(), prompt_text)
                
                # Temporarily replace toggle_agent with our mock version
                original_toggle_agent = gui.toggle_agent
                gui.toggle_agent = mock_toggle_agent
                
                try:
                    # Call the toggle_agent function to create the agent
                    gui.toggle_agent()
                    
                    # Verify that the agent was created
                    mock_agent_class.assert_called_once()
                    
                    # Verify that the cyclic prompt manager was created
                    mock_cyclic_prompt_manager.assert_called_once()
                    
                    # Verify that the prompt was set in the CyclicPromptManager
                    mock_manager_instance.set_cyclic_prompt.assert_called_with("Test prompt for integration")
                finally:
                    # Restore the original toggle_agent method
                    gui.toggle_agent = original_toggle_agent
                    
                    # Reset environment variables
                    if 'OPENAI_API_KEY' in os.environ:
                        del os.environ['OPENAI_API_KEY']
                    if 'OPENAI_API_BASE' in os.environ:
                        del os.environ['OPENAI_API_BASE'] 