#!/usr/bin/env python
"""
Convenience script to run the Screen Spy Agent in GUI mode.
"""

import sys
import os

if __name__ == "__main__":
    try:
        # Add the current directory to the Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import and run the GUI directly
        from gui_integration import main
        main()
    except ImportError as e:
        print(f"Error loading GUI: {e}")
        print("Please make sure you have all required dependencies installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 