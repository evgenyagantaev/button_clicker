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
                assert gui.coords[0] == [100, 100, 200, 200]  # Area 0 unchanged
                assert gui.coords[1] == [310, 320, 410, 420]  # Area 1 updated
                assert gui.coords[2] == [500, 500, 600, 600]  # Area 2 unchanged
                assert gui.coords[3] == [700, 700, 800, 800]  # Area 3 unchanged
                
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
                assert gui.coords[0] == [100, 100, 200, 200]  # Area 0 unchanged
                assert gui.coords[1] == [310, 320, 410, 420]  # Area 1 unchanged
                assert gui.coords[2] == [510, 520, 610, 620]  # Area 2 updated
                assert gui.coords[3] == [700, 700, 800, 800]  # Area 3 unchanged
                
                # Verify save_config was called
                assert mock_save_config.call_count == 2 