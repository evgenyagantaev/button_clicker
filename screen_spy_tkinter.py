import tkinter as tk
from tkinter import ttk
import time
import threading
import PIL.ImageGrab as ImageGrab
from PIL import Image, ImageTk

class ScreenSpy:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Spy")
        # Setting a smaller window size similar to screenshot
        self.root.geometry("400x300")
        
        # Default screenshot area based on the values in the screenshot
        self.x1, self.y1, self.x2, self.y2 = 1830, 865, 1900, 885
        
        # Create control frame
        self.create_control_panel()
        
        # Create image display
        self.image_frame = ttk.Frame(self.root)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
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
    
    def create_control_panel(self):
        control_frame = ttk.LabelFrame(self.root, text="Screenshot Area")
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
        
        # Add refresh button
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