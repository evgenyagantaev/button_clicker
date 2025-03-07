"""
GUI integration for the Screen Spy Agent.
Provides a tkinter GUI for configuring and monitoring the Screen Spy Agent.
"""

import tkinter as tk
from tkinter import ttk
import threading
import sys
import ctypes
import os
import json
import time
from PIL import Image, ImageTk
import PIL.ImageGrab as ImageGrab
from dotenv import load_dotenv

from screen_spy_agent.screenshot_taker import ScreenshotTaker
from screen_spy_agent.image_analyzer import ImageAnalyzer
from screen_spy_agent.mouse_controller import MouseController
from screen_spy_agent.screen_spy_agent import ScreenSpyAgent

CONFIG_FILE = "screen_spy_config.json"

def test_openai_connection(api_key, api_base, model):
    """Test the OpenAI API connection and return any error message or None if successful."""
    try:
        from openai import OpenAI
        
        # Create a client to test the connection
        client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        # For some API providers, we need to use a specific model format
        # Try to extract the model name if it's in the format "provider/model"
        if "/" in model:
            test_model = model.split("/")[-1]  # Use just the model name part
        else:
            test_model = model
        
        print(f"Testing connection with model: {test_model}")
        
        # Just make a simple API call to test the connection
        response = client.chat.completions.create(
            model=test_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, is the API working?"}
            ],
            max_tokens=10
        )
        
        # If we get here, the connection was successful
        return None
    except Exception as e:
        # Return the error message
        import traceback
        error_details = traceback.format_exc()
        print(f"OpenAI API test error:\n{error_details}")
        return str(e)

class ScreenSpyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Spy")
        self.root.geometry("550x600")  # Increased height for area selector
        
        # Initialize variables
        self.status_var = tk.StringVar(value="Ready")
        self.agent_status_var = tk.StringVar(value="Agent: Idle")
        self.agent_thread = None
        self.agent = None
        self.screenshot_thread = None
        self.running = True
        self.disable_auto_save = False  # Flag to control automatic saving
        
        # Variables for multiple screenshot areas
        self.num_areas = 4
        self.current_area = 0  # Currently selected area (0-3)
        
        # Initialize area variables with default values
        self.area_vars = [
            [0, 0, 100, 100],
            [100, 0, 200, 100],
            [200, 0, 300, 100],
            [300, 0, 400, 100]
        ]
        
        # Initialize click lists with default values
        self.click_lists = [
            [],  # Area 0 - no clicks
            [[50, 50]],  # Area 1
            [[50, 50]],  # Area 2
            [[50, 50]]   # Area 3
        ]
        
        # Initialize the GUI variables with the appropriate values for the current area
        self.x1_var = tk.IntVar(value=self.area_vars[self.current_area][0])
        self.y1_var = tk.IntVar(value=self.area_vars[self.current_area][1])
        self.x2_var = tk.IntVar(value=self.area_vars[self.current_area][2])
        self.y2_var = tk.IntVar(value=self.area_vars[self.current_area][3])
        
        # Initialize click position variables
        if self.current_area > 0 and len(self.click_lists[self.current_area]) > 0:
            self.click_x_var = tk.IntVar(value=self.click_lists[self.current_area][0][0])
            self.click_y_var = tk.IntVar(value=self.click_lists[self.current_area][0][1])
        else:
            # Default values for area 0 or empty click lists
            self.click_x_var = tk.IntVar(value=50)
            self.click_y_var = tk.IntVar(value=50)
        
        # Other settings
        self.interval_var = tk.IntVar(value=15)
        self.model_var = tk.StringVar(value="vis-openai/gpt-4o-mini")
        
        # Initialize area info variable
        self.area_info_var = tk.StringVar(value=f"Area {self.current_area}: ({self.get_area_coords(self.current_area)})")
        
        # Load saved configuration if available
        self.load_config()
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Create main UI components
        self.create_control_panel()
        
        # Create image display
        self.image_frame = ttk.Frame(self.root, style="ImageFrame.TFrame")
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.image_label = ttk.Label(self.image_frame, style="Image.TLabel")
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create status bar
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                                   style='Status.TLabel', anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Agent status indicator
        self.agent_status_bar = ttk.Label(self.root, textvariable=self.agent_status_var, 
                                       style='AgentStatus.TLabel', anchor=tk.W)
        self.agent_status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Take initial screenshot
        self.take_screenshot()
        
        # Start screenshot thread for live preview
        self.screenshot_thread = threading.Thread(target=self.screenshot_loop)
        self.screenshot_thread.daemon = True
        self.screenshot_thread.start()
        
        # Setup window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        # Configure the main theme colors
        bg_color = "#2d2d2d"
        fg_color = "#d4d4d4"
        highlight_color = "#2a7ada"
        alert_color = "#ff4040"  # Red color for alerts
        input_bg_color = "#1a1a1a"
        
        # Configure root window background
        self.root.configure(bg=bg_color)
        
        # Make the title bar dark on Windows
        if sys.platform == "win32":
            try:
                # Use Windows API to set dark mode for title bar
                self.root.update()
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
                value = 2
                value = ctypes.c_int(value)
                set_window_attribute(hwnd, rendering_policy, ctypes.byref(value), ctypes.sizeof(value))
            except:
                # Fallback to the old method if the above fails
                try:
                    self.root.attributes("-alpha", 0.999)
                except:
                    pass
        
        # Create and configure ttk style
        style = ttk.Style()
        
        # Try to use 'clam' theme as base (works well for dark themes)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass  # If 'clam' is not available, continue with default
        
        # Configure common elements
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TLabelframe', background=bg_color, foreground=fg_color)
        style.configure('TLabelframe.Label', background=bg_color, foreground=fg_color)
        
        # Special style for image display with a border
        style.configure('ImageFrame.TFrame', 
                        background="#1a1a1a", 
                        borderwidth=1, 
                        relief='solid')
        
        style.configure('Image.TLabel', 
                        background="#1a1a1a", 
                        foreground=fg_color)
        
        # Configure button style
        style.configure('TButton', 
                        background="#3a3a3a", 
                        foreground=fg_color, 
                        borderwidth=1,
                        focusthickness=0,
                        focuscolor=highlight_color)
        
        style.map('TButton',
                background=[('active', '#404040'), ('pressed', highlight_color)],
                foreground=[('pressed', 'white'), ('active', 'white')])
        
        # Configure entry fields
        style.configure('TEntry', 
                        fieldbackground=input_bg_color,
                        foreground=fg_color,
                        insertcolor=fg_color,
                        bordercolor="#3a3a3a",
                        lightcolor="#3a3a3a",
                        darkcolor="#3a3a3a")
        
        # Configure spinbox
        style.configure('TSpinbox', 
                        fieldbackground=input_bg_color,
                        foreground=fg_color,
                        insertcolor=fg_color,
                        bordercolor="#3a3a3a",
                        lightcolor="#3a3a3a",
                        darkcolor="#3a3a3a",
                        arrowcolor=fg_color)
        
        # Configure dropdown/combobox
        style.configure('TCombobox', 
                    fieldbackground=input_bg_color,
                    background=input_bg_color,
                    foreground=fg_color,
                    arrowcolor=fg_color,
                    bordercolor="#3a3a3a")
        
        # Configure control panel frames
        style.configure('Control.TLabelframe', 
                        background=bg_color, 
                        foreground=fg_color, 
                        bordercolor="#3a3a3a")
        
        style.configure('Control.TLabelframe.Label', 
                        background=bg_color, 
                        foreground=fg_color, 
                        font=('Arial', 9, 'bold'))
        
        # Configure status bar
        style.configure('Status.TLabel',
                        background="#1a1a1a",
                        foreground=fg_color,
                        relief='sunken')
        
        # Set specific style for agent status bar
        style.configure('AgentStatus.TLabel',
                        background=highlight_color,
                        foreground="white",
                        relief='sunken',
                        font=('Arial', 9, 'bold'))
    
    def create_control_panel(self):
        # Area selection controls
        area_frame = ttk.LabelFrame(self.root, text="Screenshot Area Selection", style='Control.TLabelframe')
        area_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create area selector
        ttk.Label(area_frame, text="Select Area:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.area_selector_var = tk.IntVar(value=self.current_area)
        area_selector = ttk.Combobox(area_frame, textvariable=self.area_selector_var, width=5,
                                    values=["0", "1", "2", "3"])
        area_selector.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        area_selector.bind("<<ComboboxSelected>>", lambda e: self.select_area(self.area_selector_var.get()))
        
        # Area info display
        self.area_info_var = tk.StringVar(value=f"Area {self.current_area}: ({self.get_area_coords(self.current_area)})")
        area_info_label = ttk.Label(area_frame, textvariable=self.area_info_var)
        area_info_label.grid(row=0, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Screenshot area settings
        control_frame = ttk.LabelFrame(self.root, text="Screenshot Area Coordinates", style='Control.TLabelframe')
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create grid layout
        for i in range(4):
            control_frame.columnconfigure(i, weight=1)
        
        # X1 control
        ttk.Label(control_frame, text="X1:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        x1_spin = ttk.Spinbox(control_frame, from_=0, to=3000, textvariable=self.x1_var, width=10)
        x1_spin.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.x1_var.trace_add("write", lambda *args: self.update_coords())
        
        # Y1 control
        ttk.Label(control_frame, text="Y1:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        y1_spin = ttk.Spinbox(control_frame, from_=0, to=3000, textvariable=self.y1_var, width=10)
        y1_spin.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        self.y1_var.trace_add("write", lambda *args: self.update_coords())
        
        # X2 control
        ttk.Label(control_frame, text="X2:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        x2_spin = ttk.Spinbox(control_frame, from_=0, to=3000, textvariable=self.x2_var, width=10)
        x2_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.x2_var.trace_add("write", lambda *args: self.update_coords())
        
        # Y2 control
        ttk.Label(control_frame, text="Y2:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        y2_spin = ttk.Spinbox(control_frame, from_=0, to=3000, textvariable=self.y2_var, width=10)
        y2_spin.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        self.y2_var.trace_add("write", lambda *args: self.update_coords())
        
        # Add refresh button with custom styling
        refresh_button = ttk.Button(control_frame, text="Take Screenshot Now", command=self.take_screenshot)
        refresh_button.grid(row=0, column=4, rowspan=2, padx=10, pady=5)
        
        # Agent settings
        agent_frame = ttk.LabelFrame(self.root, text="Agent Settings", style='Control.TLabelframe')
        agent_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Click position
        ttk.Label(agent_frame, text="Click X:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        click_x_spin = ttk.Spinbox(agent_frame, from_=0, to=3000, textvariable=self.click_x_var, width=10)
        click_x_spin.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.click_x_var.trace_add("write", lambda *args: self.update_click_pos())
        
        ttk.Label(agent_frame, text="Click Y:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        click_y_spin = ttk.Spinbox(agent_frame, from_=0, to=3000, textvariable=self.click_y_var, width=10)
        click_y_spin.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        self.click_y_var.trace_add("write", lambda *args: self.update_click_pos())
        
        # Interval
        ttk.Label(agent_frame, text="Interval (seconds):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        interval_spin = ttk.Spinbox(agent_frame, from_=1, to=60, textvariable=self.interval_var, width=10)
        interval_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.interval_var.trace_add("write", lambda *args: self.update_interval())
        
        # Model
        ttk.Label(agent_frame, text="Model:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        model_entry = ttk.Entry(agent_frame, textvariable=self.model_var, width=25)
        model_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        self.model_var.trace_add("write", lambda *args: self.update_model())
        
        # Add start/stop agent button
        self.agent_button = ttk.Button(agent_frame, text="Start Agent", command=self.toggle_agent)
        self.agent_button.grid(row=0, column=4, rowspan=2, padx=10, pady=5)
    
    def get_area_coords(self, area_index):
        """Get the coordinate string for the given area index."""
        coords = self.area_vars[area_index]
        return f"{coords[0]},{coords[1]} to {coords[2]},{coords[3]}"

    def select_area(self, area_index):
        """Select a screenshot area"""
        try:
            # Validate area index
            if area_index < 0 or area_index >= self.num_areas:
                raise ValueError(f"Invalid area index: {area_index}")
            
            # Print debug info
            print(f"Selecting area {area_index}")
            print(f"Current area_vars: {self.area_vars}")
            print(f"Current click_lists: {self.click_lists}")
            
            # Disable automatic saving during area change
            self.disable_auto_save = True
            
            # Update current area
            self.current_area = area_index
            
            # Update coordinate spinboxes - make sure we're using the right values
            # First clear any existing trace to prevent errors during updates
            try:
                x1 = self.area_vars[self.current_area][0]
                y1 = self.area_vars[self.current_area][1]
                x2 = self.area_vars[self.current_area][2]
                y2 = self.area_vars[self.current_area][3]
                
                print(f"Setting coordinate values for area {self.current_area}: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
                self.x1_var.set(x1)
                self.y1_var.set(y1)
                self.x2_var.set(x2)
                self.y2_var.set(y2)
            except Exception as e:
                print(f"Error setting area coordinates: {e}")
            
            # Update click position spinboxes for areas 1-3
            # Ensure we handle click positions correctly
            if self.current_area > 0 and len(self.click_lists[self.current_area]) > 0:
                # Print debug info for clicks
                print(f"Setting click coordinates for area {self.current_area}: {self.click_lists[self.current_area][0]}")
                click_x = self.click_lists[self.current_area][0][0]
                click_y = self.click_lists[self.current_area][0][1]
                self.click_x_var.set(click_x)
                self.click_y_var.set(click_y)
            else:
                # For area 0 or if no clicks exist, set default values
                print(f"No clicks for area {self.current_area}, setting default values")
                self.click_x_var.set(50)
                self.click_y_var.set(50)
            
            # Update area info text
            self.area_info_var.set(f"Area {self.current_area}: ({self.get_area_coords(self.current_area)})")
            
            # Update screenshot
            self.take_screenshot()
            
            # Re-enable automatic saving
            self.disable_auto_save = False
            
            # Print final state
            print(f"Area selection complete. Current area: {self.current_area}")
            try:
                print(f"Coordinate values: x1={self.x1_var.get()}, y1={self.y1_var.get()}, x2={self.x2_var.get()}, y2={self.y2_var.get()}")
                print(f"Area in area_vars: {self.area_vars[self.current_area]}")
                print(f"Click values: x={self.click_x_var.get()}, y={self.click_y_var.get()}")
            except Exception as e:
                print(f"Error getting final state: {e}")
            
            self.status_var.set(f"Selected area {self.current_area}")
        except Exception as e:
            # Make sure to re-enable auto-save even if an error occurs
            self.disable_auto_save = False
            
            import traceback
            print(f"Error selecting area: {e}")
            print(traceback.format_exc())
            self.status_var.set(f"Error: {str(e)}")
    
    def update_coords(self):
        """Update screenshot area coordinates from spinboxes"""
        try:
            # Get values from spinboxes - handle empty strings or invalid values
            try:
                x1 = int(self.x1_var.get())
            except (ValueError, tk.TclError):
                print("Warning: Invalid value for x1, using default")
                x1 = self.area_vars[self.current_area][0]  # Use existing value
                self.x1_var.set(x1)  # Reset the variable to a valid value
                
            try:
                y1 = int(self.y1_var.get())
            except (ValueError, tk.TclError):
                print("Warning: Invalid value for y1, using default")
                y1 = self.area_vars[self.current_area][1]
                self.y1_var.set(y1)
                
            try:
                x2 = int(self.x2_var.get())
            except (ValueError, tk.TclError):
                print("Warning: Invalid value for x2, using default")
                x2 = self.area_vars[self.current_area][2]
                self.x2_var.set(x2)
                
            try:
                y2 = int(self.y2_var.get())
            except (ValueError, tk.TclError):
                print("Warning: Invalid value for y2, using default")
                y2 = self.area_vars[self.current_area][3]
                self.y2_var.set(y2)
            
            # Update only the currently selected area
            self.area_vars[self.current_area] = [x1, y1, x2, y2]
            
            # Print debug info 
            print(f"Updated area_vars for area {self.current_area}: {self.area_vars[self.current_area]}")
            
            # Update the screenshot with new coordinates
            self.take_screenshot()
            
            # Save configuration only if auto-save is not disabled
            if not self.disable_auto_save:
                self.save_config()
        except Exception as e:
            import traceback
            print(f"Error updating coordinates: {e}")
            print(traceback.format_exc())
            self.status_var.set(f"Error: {str(e)}")
    
    def update_click_pos(self):
        """Update mouse click position from spinboxes"""
        try:
            # Get values from spinboxes
            click_x = int(self.click_x_var.get())
            click_y = int(self.click_y_var.get())
            
            # Update the click list for the current area (except area 0)
            if self.current_area > 0:
                # For areas 1-3, update the first click in the list (or create it if empty)
                if len(self.click_lists[self.current_area]) == 0:
                    self.click_lists[self.current_area].append([click_x, click_y])
                else:
                    self.click_lists[self.current_area][0] = [click_x, click_y]
            
            # Save configuration only if auto-save is not disabled
            if not self.disable_auto_save:
                self.save_config()
        except Exception as e:
            import traceback
            print(f"Error updating click position: {e}")
            print(traceback.format_exc())
            self.status_var.set(f"Error: {str(e)}")
    
    def update_interval(self):
        """Update interval value from spinbox"""
        try:
            # No need to store in a separate property, the value is already in self.interval_var
            if not self.disable_auto_save:
                self.save_config()
        except Exception as e:
            import traceback
            print(f"Error updating interval: {e}")
            print(traceback.format_exc())
            self.status_var.set(f"Error: {str(e)}")
    
    def update_model(self):
        """Update model value from entry field"""
        try:
            # No need to store in a separate property, the value is already in self.model_var
            if not self.disable_auto_save:
                self.save_config()
        except Exception as e:
            import traceback
            print(f"Error updating model: {e}")
            print(traceback.format_exc())
            self.status_var.set(f"Error: {str(e)}")
    
    def take_screenshot(self):
        try:
            # Get coordinates for the current area
            x1, y1, x2, y2 = self.area_vars[self.current_area]
            
            # Ensure valid coordinates (x1 < x2, y1 < y2)
            left = min(x1, x2)
            top = min(y1, y2)
            right = max(x1, x2)
            bottom = max(y1, y2)
            
            # Ensure valid dimensions
            width = right - left
            height = bottom - top
            
            if width <= 0 or height <= 0:
                raise ValueError("Invalid screenshot area dimensions")
            
            # Capture screenshot
            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
            
            # Get image dimensions
            img_width, img_height = screenshot.size
            
            # Calculate scale to fit in the display area
            # Get display area dimensions
            display_width = self.image_frame.winfo_width() - 10
            display_height = self.image_frame.winfo_height() - 10
            
            # If dimensions are not available yet, set defaults
            if display_width <= 0:
                display_width = 500
            if display_height <= 0:
                display_height = 300
            
            # Calculate scale factors
            width_scale = display_width / img_width
            height_scale = display_height / img_height
            
            # Use the smaller scale to fit the image in the display
            scale = min(width_scale, height_scale)
            
            # Calculate new dimensions
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image
            if new_width > 0 and new_height > 0:
                resized = screenshot.resize((new_width, new_height), Image.LANCZOS)
                
                # Convert to Tkinter-compatible format
                self.tk_image = ImageTk.PhotoImage(resized)
                
                # Update the label with the new image
                self.image_label.configure(image=self.tk_image)
                
                self.status_var.set(f"Area {self.current_area} screenshot: {img_width}x{img_height} pixels")
            
        except Exception as e:
            self.status_var.set(f"Error taking screenshot: {str(e)}")
    
    def screenshot_loop(self):
        """Thread function to update the screenshot at regular intervals"""
        while self.running:
            self.take_screenshot()
            time.sleep(3)  # Update every 3 seconds for the preview
    
    def toggle_agent(self):
        """Start or stop the Screen Spy Agent"""
        if self.agent is None:  # Start agent
            try:
                # Create API key and base check
                api_key = os.environ.get("OPENAI_API_KEY", "")
                api_base = os.environ.get("OPENAI_API_BASE", "")
                
                # Add diagnostic output (masked for security)
                if api_key:
                    masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "****"
                    print(f"API Key found: {masked_key}")
                else:
                    print("API Key not found in environment variables")
                    
                if api_base:
                    print(f"API Base URL found: {api_base}")
                else:
                    print("API Base URL not found in environment variables")
                    
                if not api_key:
                    self.status_var.set("Error: API key is required. Set OPENAI_API_KEY environment variable.")
                    return
                
                if not api_base:
                    self.status_var.set("Error: API base URL is required. Set OPENAI_API_BASE environment variable.")
                    return
                
                # Process the model name - some API providers need format adjustments
                model = self.model_var.get()
                if "/" in model:
                    # For vision models with specific providers
                    clean_model = model.split("/")[-1]  # Use just the model name part
                    print(f"Using model: {clean_model} (from {model})")
                else:
                    clean_model = model
                
                # Test the OpenAI connection before proceeding
                self.status_var.set("Testing OpenAI API connection...")
                error = test_openai_connection(api_key, api_base, clean_model)
                if error:
                    self.status_var.set(f"OpenAI API connection error: {error}")
                    return
                
                # Show what we're using
                self.status_var.set(f"Using API base: {api_base}, Model: {clean_model}")
                
                # Create components
                try:
                    # Create screenshot takers for each area
                    screenshot_takers = []
                    for i in range(self.num_areas):
                        x1, y1, x2, y2 = self.area_vars[i]
                        screenshot_takers.append(ScreenshotTaker(
                            min(x1, x2), 
                            min(y1, y2), 
                            max(x1, x2), 
                            max(y1, y2), 
                            self.interval_var.get()
                        ))
                except Exception as e:
                    self.status_var.set(f"Error creating screenshot takers: {str(e)}")
                    return
                    
                try:
                    # Use the clean model name
                    image_analyzer = ImageAnalyzer(api_key, api_base, clean_model)
                except Exception as e:
                    self.status_var.set(f"Error creating image analyzer: {str(e)}")
                    return
                    
                try:
                    mouse_controller = MouseController()
                    
                    # Set click coordinates for each area from the click_lists
                    for i in range(self.num_areas):
                        mouse_controller.set_click_coordinates(i, self.click_lists[i])
                except Exception as e:
                    self.status_var.set(f"Error creating mouse controller: {str(e)}")
                    return
                
                # Create agent
                try:
                    self.agent = ScreenSpyAgent(screenshot_takers, image_analyzer, mouse_controller, self.interval_var.get())
                except Exception as e:
                    self.status_var.set(f"Error creating agent: {str(e)}")
                    self.agent = None
                    return
                
                # Start agent in a separate thread
                def agent_thread_func():
                    try:
                        self.agent.run_agent()
                    except Exception as e:
                        # Get the full error details
                        import traceback
                        error_msg = f"Agent error: {str(e)}"
                        error_details = traceback.format_exc()
                        print(f"Error details:\n{error_details}")
                        self.status_var.set(error_msg)
                        self.agent_status_var.set("Agent: Error")
                        self.agent = None
                        self.agent_button.configure(text="Start Agent")
                
                self.agent_thread = threading.Thread(target=agent_thread_func)
                self.agent_thread.daemon = True
                self.agent_thread.start()
                
                self.agent_button.configure(text="Stop Agent")
                self.agent_status_var.set("Agent: Running")
            except Exception as e:
                # Get the full error details
                import traceback
                error_msg = f"Error starting agent: {str(e)}"
                error_details = traceback.format_exc()
                print(f"Error details:\n{error_details}")
                self.status_var.set(error_msg)
                self.agent = None
        else:  # Stop agent
            try:
                if self.agent:
                    self.agent.stop_agent()
                    self.agent = None
                    self.agent_button.configure(text="Start Agent")
                    self.agent_status_var.set("Agent: Stopped")
            except Exception as e:
                self.status_var.set(f"Error stopping agent: {str(e)}")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                
                # Load area coordinates
                if "areas" in config and len(config["areas"]) == 4:
                    self.area_vars = config["areas"]
                else:
                    self.area_vars = [
                        [0, 0, 100, 100],
                        [100, 0, 200, 100],
                        [200, 0, 300, 100],
                        [300, 0, 400, 100]
                    ]
                
                # Create variables if they don't exist yet
                if not hasattr(self, 'x1_var'):
                    self.x1_var = tk.IntVar(value=self.area_vars[self.current_area][0])
                if not hasattr(self, 'y1_var'):
                    self.y1_var = tk.IntVar(value=self.area_vars[self.current_area][1])
                if not hasattr(self, 'x2_var'):
                    self.x2_var = tk.IntVar(value=self.area_vars[self.current_area][2])
                if not hasattr(self, 'y2_var'):
                    self.y2_var = tk.IntVar(value=self.area_vars[self.current_area][3])
                if not hasattr(self, 'click_x_var'):
                    self.click_x_var = tk.IntVar(value=50)
                if not hasattr(self, 'click_y_var'):
                    self.click_y_var = tk.IntVar(value=50)
                if not hasattr(self, 'interval_var'):
                    self.interval_var = tk.IntVar(value=15)
                if not hasattr(self, 'model_var'):
                    self.model_var = tk.StringVar(value="vis-openai/gpt-4o-mini")
                
                # Load click coordinates
                if "clicks" in config and len(config["clicks"]) == 4:
                    self.click_lists = config["clicks"]
                    # Update click coordinate variables for the current area
                    if self.current_area > 0 and len(self.click_lists[self.current_area]) > 0:
                        self.click_x_var.set(self.click_lists[self.current_area][0][0])
                        self.click_y_var.set(self.click_lists[self.current_area][0][1])
                else:
                    self.click_lists = [
                        [],  # Area 0 - no clicks
                        [[50, 50]],  # Area 1
                        [[50, 50]],  # Area 2
                        [[50, 50]]   # Area 3
                    ]
                    if self.current_area > 0:
                        self.click_x_var.set(50)
                        self.click_y_var.set(50)
                
                # Update area coordinate variables for the current area
                self.x1_var.set(self.area_vars[self.current_area][0])
                self.y1_var.set(self.area_vars[self.current_area][1])
                self.x2_var.set(self.area_vars[self.current_area][2])
                self.y2_var.set(self.area_vars[self.current_area][3])
                
                # Load interval
                if "interval" in config:
                    self.interval_var.set(config.get("interval", 15))
                
                # Load model
                if "model" in config:
                    self.model_var.set(config.get("model", "vis-openai/gpt-4o-mini"))
                
                # For backward compatibility
                if "click_x" in config and "click_y" in config:
                    # Update the click lists for areas 1-3 with the legacy click coordinates
                    for i in range(1, 4):
                        self.click_lists[i] = [[config["click_x"], config["click_y"]]]
                    
                    # Update the click spinboxes
                    self.click_x_var.set(str(config["click_x"]))
                    self.click_y_var.set(str(config["click_y"]))
                
                self.status_var.set("Configuration loaded")
            else:
                # Set default values
                self.area_vars = [
                    [0, 0, 100, 100],
                    [100, 0, 200, 100],
                    [200, 0, 300, 100],
                    [300, 0, 400, 100]
                ]
                self.click_lists = [
                    [],  # Area 0 - no clicks
                    [[50, 50]],  # Area 1
                    [[50, 50]],  # Area 2
                    [[50, 50]]   # Area 3
                ]
                self.click_x_var.set("50")
                self.click_y_var.set("50")
                if hasattr(self, 'interval_var'):
                    self.interval_var.set("15")
                if hasattr(self, 'model_var'):
                    self.model_var.set("vis-openai/gpt-4o-mini")
                
                self.status_var.set("Using default configuration")
        except Exception as e:
            self.status_var.set(f"Error loading config: {str(e)}")
            
            # Set default values
            self.area_vars = [
                [0, 0, 100, 100],
                [100, 0, 200, 100],
                [200, 0, 300, 100],
                [300, 0, 400, 100]
            ]
            self.click_lists = [
                [],  # Area 0 - no clicks
                [[50, 50]],  # Area 1
                [[50, 50]],  # Area 2
                [[50, 50]]   # Area 3
            ]
            if hasattr(self, 'click_x_var'):
                self.click_x_var.set("50")
            if hasattr(self, 'click_y_var'):
                self.click_y_var.set("50")
            if hasattr(self, 'interval_var'):
                self.interval_var.set("15")
            if hasattr(self, 'model_var'):
                self.model_var.set("vis-openai/gpt-4o-mini")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            # Create a configuration dictionary with the current settings
            config = {
                "areas": self.area_vars,
                "clicks": self.click_lists,
                "interval": int(self.interval_var.get()),
                "model": self.model_var.get()
            }
            
            # Save to file
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
            
            self.status_var.set("Configuration saved")
        except Exception as e:
            self.status_var.set(f"Error saving config: {str(e)}")
            print(f"Error saving config: {e}")
    
    def on_close(self):
        """Handle window close event"""
        self.running = False
        if self.agent:
            self.agent.stop_agent()
        self.root.destroy()


def main():
    """Main function to run the GUI."""
    # Load environment variables from .env file
    load_dotenv()
    root = tk.Tk()
    app = ScreenSpyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 