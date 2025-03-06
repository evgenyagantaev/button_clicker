import tkinter as tk
import subprocess
import sys
import os
import traceback
from tkinter import messagebox

try:
    # Try to import required modules
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    import pyautogui
    from pynput import mouse
    
    # Import the MacroRecorder class from the main file
    from macrorecorder import MacroRecorder
    
    # Run the application directly without showing console
    if __name__ == "__main__":
        try:
            app = QApplication(sys.argv)
            window = MacroRecorder()
            window.show()
            sys.exit(app.exec_())
        except Exception as e:
            # If an error occurs during runtime, show it in a dialog
            error_msg = f"Error running application:\n{str(e)}\n\n{traceback.format_exc()}"
            
            # Create a log file with the error
            with open("macrorecorder_error_log.txt", "w") as f:
                f.write(error_msg)
            
            # Show error in a tkinter dialog since PyQt might be the source of the error
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Application Error", error_msg)
            root.destroy()
            
except ImportError as e:
    # If import fails, create a simple GUI to show the error
    root = tk.Tk()
    root.title("Import Error")
    root.geometry("600x400")
    
    error_msg = f"Missing required module: {str(e)}\n\nPlease install it using:\npip install -r requirements.txt"
    
    # Create a log file with the error
    with open("macrorecorder_error_log.txt", "w") as f:
        f.write(f"Import Error: {str(e)}\n\n{traceback.format_exc()}")
    
    label = tk.Label(root, text=error_msg, padx=20, pady=20, justify=tk.LEFT)
    label.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop() 