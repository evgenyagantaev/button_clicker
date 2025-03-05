import tkinter as tk
import subprocess
import sys
import os
import threading
import time
from tkinter import ttk, messagebox
import traceback

try:
    # Try to import required modules
    import PIL.ImageGrab
    from PIL import Image, ImageTk
    
    # Import the ScreenSpy class from the main file
    from screen_spy_tkinter import ScreenSpy
    
    # Run the application directly without showing console
    if __name__ == "__main__":
        try:
            root = tk.Tk()
            app = ScreenSpy(root)
            root.mainloop()
        except Exception as e:
            # If an error occurs during runtime, show it in a dialog
            error_msg = f"Error running application:\n{str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror("Application Error", error_msg)
            
            # Create a log file with the error
            with open("error_log.txt", "w") as f:
                f.write(error_msg)
                
except ImportError as e:
    # If import fails, create a simple GUI to show the error
    root = tk.Tk()
    root.title("Import Error")
    root.geometry("600x400")
    
    error_msg = f"Missing required module: {str(e)}\n\nPlease install it using:\npip install -r requirements.txt"
    
    # Create a log file with the error
    with open("error_log.txt", "w") as f:
        f.write(f"Import Error: {str(e)}\n\n{traceback.format_exc()}")
    
    label = tk.Label(root, text=error_msg, padx=20, pady=20, justify=tk.LEFT)
    label.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop() 