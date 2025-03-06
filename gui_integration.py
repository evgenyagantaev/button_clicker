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
        self.root.geometry("550x500")
        
        # Initialize variables
        self.status_var = tk.StringVar(value="Ready")
        self.agent_status_var = tk.StringVar(value="Agent: Idle")
        self.agent_thread = None
        self.agent = None
        self.screenshot_thread = None
        self.running = True
        
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
        
        # Configure labelframe (group boxes)
        style.configure('TLabelframe', 
                        background=bg_color, 
                        foreground=fg_color,
                        bordercolor="#3a3a3a")
        
        style.configure('TLabelframe.Label',
                        background=bg_color,
                        foreground=fg_color,
                        font=('Arial', 9, 'bold'))
        
        # Create a specific style for the control panel
        style.configure('Control.TLabelframe', 
                        background=input_bg_color, 
                        foreground=fg_color,
                        bordercolor="#3a3a3a")
        
        style.configure('Control.TLabelframe.Label',
                        background=input_bg_color,
                        foreground=fg_color,
                        font=('Arial', 9, 'bold'))
        
        # Set specific style for status bar
        style.configure('Status.TLabel',
                        background=input_bg_color,
                        foreground=fg_color,
                        relief='sunken')
        
        # Set specific style for agent status bar
        style.configure('AgentStatus.TLabel',
                        background=highlight_color,
                        foreground="white",
                        relief='sunken',
                        font=('Arial', 9, 'bold'))
    
    def create_control_panel(self):
        # Screenshot area settings
        control_frame = ttk.LabelFrame(self.root, text="Screenshot Area", style='Control.TLabelframe')
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create grid layout
        for i in range(4):
            control_frame.columnconfigure(i, weight=1)
        
        # X1 control
        ttk.Label(control_frame, text="X1:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.x1_var = tk.IntVar(value=self.x1)
        x1_spin = ttk.Spinbox(control_frame, from_=0, to=3000, textvariable=self.x1_var, width=10)
        x1_spin.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.x1_var.trace_add("write", lambda *args: self.update_coords())
        
        # Y1 control
        ttk.Label(control_frame, text="Y1:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.y1_var = tk.IntVar(value=self.y1)
        y1_spin = ttk.Spinbox(control_frame, from_=0, to=3000, textvariable=self.y1_var, width=10)
        y1_spin.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        self.y1_var.trace_add("write", lambda *args: self.update_coords())
        
        # X2 control
        ttk.Label(control_frame, text="X2:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.x2_var = tk.IntVar(value=self.x2)
        x2_spin = ttk.Spinbox(control_frame, from_=0, to=3000, textvariable=self.x2_var, width=10)
        x2_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.x2_var.trace_add("write", lambda *args: self.update_coords())
        
        # Y2 control
        ttk.Label(control_frame, text="Y2:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.y2_var = tk.IntVar(value=self.y2)
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
        self.click_x_var = tk.IntVar(value=self.click_x)
        click_x_spin = ttk.Spinbox(agent_frame, from_=0, to=3000, textvariable=self.click_x_var, width=10)
        click_x_spin.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.click_x_var.trace_add("write", lambda *args: self.update_click_pos())
        
        ttk.Label(agent_frame, text="Click Y:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.click_y_var = tk.IntVar(value=self.click_y)
        click_y_spin = ttk.Spinbox(agent_frame, from_=0, to=3000, textvariable=self.click_y_var, width=10)
        click_y_spin.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        self.click_y_var.trace_add("write", lambda *args: self.update_click_pos())
        
        # Interval
        ttk.Label(agent_frame, text="Interval (seconds):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.interval_var = tk.IntVar(value=self.interval)
        interval_spin = ttk.Spinbox(agent_frame, from_=1, to=60, textvariable=self.interval_var, width=10)
        interval_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.interval_var.trace_add("write", lambda *args: self.update_interval())
        
        # Model
        ttk.Label(agent_frame, text="Model:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.model_var = tk.StringVar(value=self.model)
        model_entry = ttk.Entry(agent_frame, textvariable=self.model_var, width=25)
        model_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        self.model_var.trace_add("write", lambda *args: self.update_model())
        
        # Add start/stop agent button
        self.agent_button = ttk.Button(agent_frame, text="Start Agent", command=self.toggle_agent)
        self.agent_button.grid(row=0, column=4, rowspan=2, padx=10, pady=5)
    
    def update_coords(self):
        try:
            self.x1 = int(self.x1_var.get())
            self.y1 = int(self.y1_var.get())
            self.x2 = int(self.x2_var.get())
            self.y2 = int(self.y2_var.get())
            self.save_config()
        except:
            pass
    
    def update_click_pos(self):
        try:
            self.click_x = int(self.click_x_var.get())
            self.click_y = int(self.click_y_var.get())
            self.save_config()
        except:
            pass
    
    def update_interval(self):
        try:
            self.interval = int(self.interval_var.get())
            self.save_config()
        except:
            pass
    
    def update_model(self):
        self.model = self.model_var.get()
        self.save_config()
    
    def take_screenshot(self):
        try:
            # Ensure valid coordinates (x1 < x2, y1 < y2)
            left = min(self.x1, self.x2)
            top = min(self.y1, self.y2)
            right = max(self.x1, self.x2)
            bottom = max(self.y1, self.y2)
            
            # Ensure valid dimensions
            if right <= left or bottom <= top:
                self.status_var.set("Error: Invalid dimensions")
                return
            
            # Take the screenshot
            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
            
            # Save the screenshot
            screenshot.save("current_screenshot.jpg")
            
            # Resize to fit the label
            img_width, img_height = screenshot.size
            label_width = self.image_label.winfo_width() or 450
            label_height = self.image_label.winfo_height() or 300
            
            # Calculate scale to fit while maintaining aspect ratio
            scale = min(label_width / img_width, label_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image
            if new_width > 0 and new_height > 0:
                resized = screenshot.resize((new_width, new_height), Image.LANCZOS)
                
                # Convert to Tkinter-compatible format
                self.tk_image = ImageTk.PhotoImage(resized)
                
                # Update the label with the new image
                self.image_label.configure(image=self.tk_image)
                
                self.status_var.set(f"Screenshot taken: {img_width}x{img_height} pixels")
            
        except Exception as e:
            self.status_var.set(f"Error taking screenshot: {str(e)}")
    
    def screenshot_loop(self):
        """Thread function to update the screenshot at regular intervals"""
        while self.running:
            self.take_screenshot()
            time.sleep(3)  # Update every second for the preview
    
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
                model = self.model
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
                    screenshot_taker = ScreenshotTaker(
                        min(self.x1, self.x2), 
                        min(self.y1, self.y2), 
                        max(self.x1, self.x2), 
                        max(self.y1, self.y2), 
                        self.interval
                    )
                except Exception as e:
                    self.status_var.set(f"Error creating screenshot taker: {str(e)}")
                    return
                    
                try:
                    # Use the clean model name
                    image_analyzer = ImageAnalyzer(api_key, api_base, clean_model)
                except Exception as e:
                    self.status_var.set(f"Error creating image analyzer: {str(e)}")
                    return
                    
                try:
                    mouse_controller = MouseController(self.click_x, self.click_y)
                except Exception as e:
                    self.status_var.set(f"Error creating mouse controller: {str(e)}")
                    return
                
                # Create agent
                try:
                    self.agent = ScreenSpyAgent(screenshot_taker, image_analyzer, mouse_controller, self.interval)
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
        """Load configuration from file if available"""
        # Default values
        self.x1 = 0
        self.y1 = 0
        self.x2 = 100
        self.y2 = 100
        self.click_x = 50
        self.click_y = 50
        self.interval = 15
        self.model = "vis-openai/gpt-4o-mini"
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.x1 = config.get('x1', self.x1)
                    self.y1 = config.get('y1', self.y1)
                    self.x2 = config.get('x2', self.x2)
                    self.y2 = config.get('y2', self.y2)
                    self.click_x = config.get('click_x', self.click_x)
                    self.click_y = config.get('click_y', self.click_y)
                    self.interval = config.get('interval', self.interval)
                    self.model = config.get('model', self.model)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'x1': self.x1,
                'y1': self.y1,
                'x2': self.x2,
                'y2': self.y2,
                'click_x': self.click_x,
                'click_y': self.click_y,
                'interval': self.interval,
                'model': self.model
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
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