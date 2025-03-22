#!/usr/bin/env python
"""
Simple script to stop the running ScreenSpyAgent
"""

import os
import sys
import time
from screen_spy_agent.screen_spy_agent import ScreenSpyAgent

def main():
    """Create a stop trigger file to stop the running agent"""
    print("Creating stop trigger for ScreenSpyAgent...")
    
    # Create a minimal agent instance just to access the create_stop_trigger method
    dummy_agent = ScreenSpyAgent(None, None, None)
    stop_file_path = dummy_agent.create_stop_trigger()
    
    print(f"Stop trigger created at: {stop_file_path}")
    print("The agent will stop at its next check cycle")
    print("Waiting 5 seconds to ensure stop file is detected...")
    time.sleep(5)
    
    # Check if the file was removed, which indicates the agent processed it
    if not os.path.exists(stop_file_path):
        print("Stop file was processed by the agent")
    else:
        print("Stop file still exists - agent may not be running or hasn't checked yet")

if __name__ == "__main__":
    main()
    print("Script complete. Agent should be stopped.") 