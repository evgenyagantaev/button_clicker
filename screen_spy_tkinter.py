import tkinter as tk
from tkinter import ttk
import time
import threading
import PIL.ImageGrab as ImageGrab
from PIL import Image, ImageTk
import sys
import ctypes

class ScreenSpy:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Spy")
        # Setting a smaller window size similar to screenshot
        self.root.geometry("450x350")
        
        # Initialize status_var
        self.status_var = tk.StringVar()
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Default screenshot area based on the values in the screenshot
        self.x1, self.y1, self.x2, self.y2 = 1760, 880, 1900, 907
        
        # Create control frame
        self.create_control_panel()
        
        # Create image display
        self.image_frame = ttk.Frame(self.root, style="ImageFrame.TFrame")
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.image_label = ttk.Label(self.image_frame, style="Image.TLabel")
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create status bar
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Flag to control screenshot thread
        self.running = True
        
        # Start screenshot thread
        self.screenshot_thread = threading.Thread(target=self.screenshot_loop)
        self.screenshot_thread.daemon = True
        self.screenshot_thread.start()
        
        # Take initial screenshot
        self.take_screenshot()
        
        # Setup window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        # Configure the main theme colors
        bg_color = "#2d2d2d"
        fg_color = "#d4d4d4"
        highlight_color = "#2a7ada"
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
                    self.root.attributes("-alpha", 0.999)  # Small transparency trick that can trigger dark mode
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
                        
        # Create the status bar with the custom style
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                                   style='Status.TLabel', anchor=tk.W)
    
    def create_control_panel(self):
        control_frame = ttk.LabelFrame(self.root, text="Screenshot Area", style='Control.TLabelframe')
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create grid layout
        for i in range(2):
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
    
    def update_coords(self):
        try:
            self.x1 = int(self.x1_var.get())
            self.y1 = int(self.y1_var.get())
            self.x2 = int(self.x2_var.get())
            self.y2 = int(self.y2_var.get())
        except:
            pass
    
    def take_screenshot(self):
        try:
            # Calculate screenshot dimensions
            left = min(self.x1, self.x2)
            top = min(self.y1, self.y2)
            right = max(self.x1, self.x2)
            bottom = max(self.y1, self.y2)
            
            # Ensure we have valid dimensions
            if right <= left or bottom <= top:
                self.status_var.set("Error: Invalid dimensions")
                return
            
            # Take the screenshot
            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
            
            # Resize to fit the label
            img_width, img_height = screenshot.size
            label_width = self.image_label.winfo_width() or 350
            label_height = self.image_label.winfo_height() or 160
            
            # Calculate scale to fit while maintaining aspect ratio
            scale = min(label_width / img_width, label_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image
            if new_width > 0 and new_height > 0:
                resized = screenshot.resize((new_width, new_height), Image.LANCZOS)
                
                # Convert to Tkinter-compatible format
                self.tk_image = ImageTk.PhotoImage(resized)
                
                # Display the screenshot
                self.image_label.config(image=self.tk_image)
                
                timestamp = time.strftime("%H:%M:%S")
                self.status_var.set(f"Screenshot taken at {timestamp}")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def screenshot_loop(self):
        while self.running:
            self.take_screenshot()
            # Sleep for 5 seconds
            time.sleep(5)
    
    def on_close(self):
        self.running = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenSpy(root)
    root.mainloop() 