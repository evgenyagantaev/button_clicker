import tkinter as tk
from tkinter import ttk
import time
import threading
import PIL.ImageGrab as ImageGrab
from PIL import Image, ImageTk
import sys
import ctypes
import pytesseract
import re
import os

class ScreenSpy:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Spy")
        # Setting a smaller window size similar to screenshot
        self.root.geometry("450x350")
        
        # Initialize status_var
        self.status_var = tk.StringVar()
        
        # Initialize text recognition status variables
        self.recognition_enabled = tk.BooleanVar(value=True)
        self.accept_found = tk.BooleanVar(value=False)
        self.reject_found = tk.BooleanVar(value=False)  # New variable to track "reject"
        self.reject_accept_found = tk.BooleanVar(value=False)  # New variable to track both words together
        self.accept_status_var = tk.StringVar(value="No 'accept' found")
        
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
        
        # Create recognition status frame
        self.create_recognition_status()
        
        # Create status bar
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Flag to control screenshot thread
        self.running = True
        
        # Check for Tesseract installation
        self.tesseract_available = self.check_tesseract()
        if not self.tesseract_available:
            self.status_var.set("Warning: Tesseract OCR not found. Using backup detection method.")
            # Keep text recognition enabled even without Tesseract
            # self.recognition_enabled.set(False)  # Commented out to keep enabled
        
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
        
        # Create alert style for when "accept" is found
        style.configure('Alert.TLabel',
                        background=alert_color,
                        foreground="white",
                        relief='sunken',
                        font=('Arial', 9, 'bold'))
                        
        # Create the status bar with the custom style
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                                   style='Status.TLabel', anchor=tk.W)
    
    def create_recognition_status(self):
        """Create a frame to display text recognition status"""
        recognition_frame = ttk.LabelFrame(self.root, text="Text Recognition", style='Control.TLabelframe')
        recognition_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Status indicator (will be red when "accept" is found, otherwise normal)
        self.indicator_label = ttk.Label(recognition_frame, text="STATUS:", style='Status.TLabel')
        self.indicator_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.status_indicator = ttk.Label(recognition_frame, textvariable=self.accept_status_var, 
                                         style='Status.TLabel')
        self.status_indicator.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        # Reset button to clear "accept" detection state
        reset_button = ttk.Button(recognition_frame, text="Reset", 
                                 command=self.reset_detection)
        reset_button.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def reset_detection(self):
        """Reset the detection state"""
        self.accept_found.set(False)
        self.reject_found.set(False)  # Reset reject state
        self.reject_accept_found.set(False)  # Reset combined state
        self.accept_status_var.set("No 'accept' found")
        self.status_indicator.configure(style='Status.TLabel')

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
        
        # Add text recognition toggle
        recog_check = ttk.Checkbutton(control_frame, text="Enable Text Recognition", 
                                     variable=self.recognition_enabled)
        recog_check.grid(row=2, column=0, columnspan=5, padx=5, pady=5, sticky=tk.W)
        # Ensure the checkbox is checked by default
        self.recognition_enabled.set(True)
        # Explicitly select the checkbox
        recog_check.invoke()
        recog_check.invoke()  # Double invoke to ensure it's checked
    
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
            
            # Perform text recognition if enabled, regardless of whether Tesseract is available
            if self.recognition_enabled.get():
                self.recognize_text(screenshot)
            
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
    
    def recognize_text(self, image):
        """Recognize text in the image and check for 'accept'"""
        try:
            # Debug info - display size of image
            width, height = image.size
            print(f"Processing image: {width}x{height}")
            
            # First try with direct OCR if Tesseract is available
            if self.tesseract_available:
                # Prepare image for better OCR - convert to grayscale
                gray_image = image.convert('L')
                
                # Try multiple threshold values to improve detection
                threshold_values = [100, 120, 140, 160, 180]  # Expanded range
                
                # Try multiple PSM modes
                psm_modes = [7, 6, 10, 11, 3]  # Added more page segmentation modes
                
                # Enhanced attempts list with various preprocessing techniques
                attempts = []
                
                # Add thresholded images
                for threshold in threshold_values:
                    # Standard threshold (dark text on light background)
                    binary = gray_image.point(lambda p: 0 if p < threshold else 255)
                    attempts.append((binary, f"binary-{threshold}"))
                    
                    # Inverted threshold (light text on dark background)
                    inverted = gray_image.point(lambda p: 255 if p < threshold else 0)
                    attempts.append((inverted, f"inverted-{threshold}"))
                    
                    # Scaled versions
                    scaled_binary = binary.resize((width*2, height*2), Image.LANCZOS)
                    attempts.append((scaled_binary, f"scaled-binary-{threshold}"))
                    
                    scaled_inverted = inverted.resize((width*2, height*2), Image.LANCZOS)
                    attempts.append((scaled_inverted, f"scaled-inverted-{threshold}"))
                
                # Also add original images
                attempts.append((gray_image, "grayscale"))
                attempts.append((image, "original"))
                scaled_gray = gray_image.resize((width*2, height*2), Image.LANCZOS)
                attempts.append((scaled_gray, "scaled-grayscale"))
                scaled_original = image.resize((width*2, height*2), Image.LANCZOS)
                attempts.append((scaled_original, "scaled-original"))
                
                # Try with various combinations of image processing and OCR settings
                for img, method in attempts:
                    for psm in psm_modes:
                        try:
                            # Try with different OCR configurations
                            # PSM 7 - Treat the image as a single text line
                            # PSM 6 - Assume a single uniform block of text
                            # PSM 10 - Treat the image as a single character
                            # PSM 11 - Sparse text. Find as much text as possible in no particular order
                            # PSM 3 - Fully automatic page segmentation (default)
                            
                            # Allow more characters but optimize for "accept"
                            custom_config = f'--oem 3 --psm {psm} -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                            
                            # Convert image to text
                            text = pytesseract.image_to_string(img, config=custom_config)
                            print(f"OCR result (method: {method}, psm: {psm}): '{text.strip()}'")
                            
                            # Check for both "reject" and "accept" in the same text
                            has_accept = re.search(r'ac+e*p*t|acc?e?pt|accept', text, re.IGNORECASE) is not None
                            has_reject = re.search(r'rej+e*c*t|reje?c?t|reject', text, re.IGNORECASE) is not None
                            
                            # Check for partial matches for accept
                            if not has_accept:
                                has_accept = (re.search(r'acc', text, re.IGNORECASE) or 
                                            re.search(r'cept', text, re.IGNORECASE) or
                                            re.search(r'ac+.?pt', text, re.IGNORECASE)) is not None
                            
                            # Check for partial matches for reject
                            if not has_reject:
                                has_reject = (re.search(r'rej', text, re.IGNORECASE) or 
                                            re.search(r'jec', text, re.IGNORECASE) or
                                            re.search(r're.?ct', text, re.IGNORECASE)) is not None
                            
                            # Update states based on what we found
                            if has_accept:
                                self.accept_found.set(True)
                            
                            if has_reject:
                                self.reject_found.set(True)
                            
                            # If both are found, set the combined state
                            if has_accept and has_reject:
                                self.reject_accept_found.set(True)
                                self.accept_status_var.set("'reject accept' FOUND TOGETHER!")
                                self.status_indicator.configure(style='Alert.TLabel')
                                self.root.bell()
                                self.root.attributes('-topmost', True)
                                self.root.update()
                                self.root.attributes('-topmost', False)
                                return
                            # If only accept is found but combined state is not activated yet
                            elif has_accept and not self.reject_accept_found.get():
                                self.accept_status_var.set("'accept' FOUND!")
                                self.status_indicator.configure(style='Alert.TLabel')
                            # If only reject is found but combined state is not activated yet
                            elif has_reject and not self.reject_accept_found.get():
                                self.accept_status_var.set("'reject' FOUND!")
                                self.status_indicator.configure(style='Alert.TLabel')
                                
                        except Exception as e:
                            print(f"OCR attempt failed (method: {method}, psm: {psm}): {str(e)}")
                            continue
            
            # If we get here, try pattern matching as backup
            # This is simplified image analysis that works without Tesseract
            # Convert to grayscale for simplicity
            gray = image.convert('L')
            
            # Get pixel data
            pixels = list(gray.getdata())
            avg_brightness = sum(pixels) / len(pixels)
            
            # This is a very simplified backup method - looking for bright text on dark background
            # It's not as accurate as OCR but can serve as a fallback
            # Specifically checking for patterns that could indicate "accept" text
            if avg_brightness < 100:  # Dark background with light text (like the screenshot)
                # Count bright pixels - in a pattern consistent with text
                bright_pixels = sum(1 for p in pixels if p > 200)
                bright_ratio = bright_pixels / len(pixels)
                
                print(f"Backup detection - Avg brightness: {avg_brightness}, Bright ratio: {bright_ratio}")
                
                # If we have a significant number of bright pixels (potential text)
                if 0.01 < bright_ratio < 0.5:  # Adjusted to be more permissive
                    print("Potential text detected by backup method")
                    
                    # Since we can't do precise OCR without Tesseract, just assume there might be "reject accept"
                    # This is a very simplistic approach, but better than nothing for backup
                    if not self.reject_accept_found.get():
                        # Set all detection states as potentials
                        self.accept_found.set(True)
                        self.reject_found.set(True)
                        self.reject_accept_found.set(True)
                        self.accept_status_var.set("Potential 'reject accept' detected!")
                        self.status_indicator.configure(style='Alert.TLabel')
                        self.root.bell()
                        self.root.attributes('-topmost', True)
                        self.root.update()
                        self.root.attributes('-topmost', False)
                
        except Exception as e:
            self.status_var.set(f"Text recognition error: {str(e)}")
            print(f"OCR Error: {str(e)}")
    
    def screenshot_loop(self):
        while self.running:
            self.take_screenshot()
            # Sleep for 5 seconds
            time.sleep(5)
    
    def on_close(self):
        self.running = False
        self.root.destroy()

    def check_tesseract(self):
        """Check if Tesseract OCR is installed and available"""
        try:
            # First try to get tesseract version
            version = pytesseract.get_tesseract_version()
            print(f"Tesseract version: {version}")
            return True
        except Exception as e:
            print(f"Error with Tesseract: {str(e)}")
            
            # Define possible paths where Tesseract might be installed
            # This is especially important on Windows where it's often not in PATH
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\evgeny\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',  # Common user install path
                r'/usr/bin/tesseract',
                r'/usr/local/bin/tesseract'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"Found Tesseract at: {path}")
                    pytesseract.pytesseract.tesseract_cmd = path
                    try:
                        version = pytesseract.get_tesseract_version()
                        print(f"Tesseract version after path fix: {version}")
                        return True
                    except:
                        continue
            
            print("Tesseract OCR not found or not correctly installed")
            print("Please install it from: https://github.com/UB-Mannheim/tesseract/wiki")
            
            # Last resort - try to use alternative OCR methods
            # If we got here, we'll try to do basic text detection without Tesseract
            # by using a simple pattern matching approach for the word "accept"
            print("Enabling backup detection method")
            return False
            

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenSpy(root)
    root.mainloop() 