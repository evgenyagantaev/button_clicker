#!/usr/bin/env python
"""
Manual Test Script for UI Interaction with Screen Spy Agent

This script provides guidance and helper functions for manual testing of the
cyclic prompt feature and its integration with the Screen Spy Agent system.
"""

import os
import sys
import time
import pyautogui
import logging
from pathlib import Path

# Add the parent directory to the path to import from the project
sys.path.append(str(Path(__file__).parent.parent))

from screen_spy_agent.screen_spy_agent import ScreenSpyAgent
from screen_spy_agent.cyclic_prompt_manager import CyclicPromptManager
from gui_integration import launch_gui

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("manual_test_results.log")
    ]
)
logger = logging.getLogger("manual_testing")

class ManualTester:
    """Helper class for manual testing of the Screen Spy Agent UI interaction"""
    
    def __init__(self):
        self.agent = None
        self.gui_process = None
        
    def setup(self):
        """Setup the testing environment"""
        logger.info("Setting up test environment...")
        # This function is intentionally left minimal as the GUI should be
        # started separately for manual testing
        
    def test_cyclic_prompt_feature(self):
        """
        Test the full cycle with actual screen captures
        
        Steps:
        1. Launch the GUI
        2. Enter a test cyclic prompt
        3. Configure areas for monitoring
        4. Start the agent
        5. Observe the agent performing the start sequence
        6. Monitor for restart conditions
        7. Verify the agent restarts properly
        """
        logger.info("=== CYCLIC PROMPT FEATURE MANUAL TEST ===")
        logger.info("Follow these steps carefully:")
        
        print("\n=== CYCLIC PROMPT FEATURE MANUAL TEST ===")
        print("This test requires manual observation and verification.")
        print("\nTest Steps:")
        print("1. Launch the GUI application using 'python run_gui.py'")
        print("2. In the GUI:")
        print("   a. Enter a test cyclic prompt in the multi-line text field")
        print("   b. Configure Area 1 to monitor for 'new chat' text")
        print("   c. Configure Area 2 to monitor for activity/gray background")
        print("   d. Set up the click positions for the start sequence")
        print("3. Start the agent by clicking 'Start Agent'")
        print("4. Observe the following:")
        print("   a. The agent performs the start sequence with clicks and pauses")
        print("   b. The cyclic prompt is copied and pasted into the target application")
        print("   c. The agent monitors both areas for restart conditions")
        
        input("\nPress Enter when you're ready to begin testing...")
        
        # Record test results
        print("\nTest Verification:")
        self._verify_test_step("Did the agent successfully perform the start sequence?")
        self._verify_test_step("Was the cyclic prompt correctly copied and pasted?")
        self._verify_test_step("Did the agent properly restart when 'new chat' was detected in Area 1?")
        self._verify_test_step("Did the agent restart after 2 minutes of inactivity in Area 2?")
        self._verify_test_step("Did the UI update properly during the cycle (showing current state)?")
        
        print("\nTest completed. Check manual_test_results.log for detailed results.")
        
    def _verify_test_step(self, question):
        """Helper method to verify a test step with user input"""
        while True:
            response = input(f"{question} (y/n): ").lower()
            if response in ['y', 'n']:
                logger.info(f"Test step: {question} - {'PASSED' if response == 'y' else 'FAILED'}")
                
                if response == 'n':
                    details = input("Please provide details about the failure: ")
                    logger.error(f"Failure details: {details}")
                
                return response == 'y'
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    def take_screenshot(self, name):
        """Take a screenshot for documentation purposes"""
        filename = f"test_screenshot_{name}_{int(time.time())}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        logger.info(f"Screenshot saved to {filename}")
        print(f"Screenshot saved to {filename}")
        return filename
    
    def cleanup(self):
        """Clean up after testing"""
        logger.info("Cleaning up test environment...")
        if self.agent:
            # Stop the agent if it's running
            self.agent.stop()
        
        print("\nTest cleanup completed.")

def main():
    """Main function to run the manual tests"""
    tester = ManualTester()
    try:
        tester.setup()
        tester.test_cyclic_prompt_feature()
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main() 