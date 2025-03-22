"""
ScreenSpyAgent class that ties everything together.
"""

import threading
import time
import os
import traceback
from typing import TypedDict, List, Optional, Dict, Any, Union
from langchain_core.runnables import chain
from langgraph.graph import END, StateGraph

from screen_spy_agent.screenshot_taker import ScreenshotTaker
from screen_spy_agent.image_analyzer import ImageAnalyzer
from screen_spy_agent.mouse_controller import MouseController
from screen_spy_agent.agent_state import AgentState
from screen_spy_agent.agent_node import AgentNode
from screen_spy_agent.cyclic_prompt_manager import CyclicPromptManager

# Thread-local storage for sharing components with nodes
thread_local = threading.local()

# Define the state schema for langgraph
class AgentStateDict(TypedDict):
    detection_history: List[Union[bool, List[bool]]]
    action_history: List[bool]
    current_screenshot: str
    current_screenshots: List[str]
    both_words_detected: bool
    detection_results: List[bool]
    should_click: bool
    vertical_shift: int


class ScreenSpyAgent:
    """
    Main agent class that ties all components together.
    
    Attributes:
        screenshot_takers: List of ScreenshotTaker instances for multiple areas.
        image_analyzer: ImageAnalyzer instance.
        mouse_controller: MouseController instance.
        interval: Interval in seconds between screenshots.
        agent_state: AgentState instance.
        workflow: LangGraph workflow.
        running: Whether the agent is running.
        agent_thread: Thread for the agent loop.
        cyclic_prompt_manager: CyclicPromptManager instance.
        last_activity_time: Timestamp of the last activity detected in Area 2.
        inactivity_threshold: Time in seconds after which to consider Area 2 inactive.
    """
    
    def __init__(self, screenshot_taker, image_analyzer, mouse_controller, interval=15, cyclic_prompt=None):
        """
        Initialize the agent with the given components.
        
        Args:
            screenshot_taker: ScreenshotTaker instance or list of ScreenshotTaker instances.
            image_analyzer: ImageAnalyzer instance.
            mouse_controller: MouseController instance.
            interval: Interval in seconds between screenshots.
            cyclic_prompt: Optional initial cyclic prompt text.
        """
        print("=== INITIALIZING SCREEN SPY AGENT ===")
        
        # Check if screenshot_taker is a list (multiple areas) or a single instance
        if isinstance(screenshot_taker, list):
            self.screenshot_takers = screenshot_taker
            self.num_areas = len(screenshot_taker)
            print(f"Initialized with {self.num_areas} screenshot areas")
        else:
            self.screenshot_takers = [screenshot_taker]
            self.num_areas = 1
            print("Initialized with 1 screenshot area")
        
        self.image_analyzer = image_analyzer
        self.mouse_controller = mouse_controller
        self.interval = interval
        print(f"Screenshot interval set to {interval} seconds")
        
        self.agent_state = AgentState(num_areas=self.num_areas)
        self.running = False
        self.agent_thread = None
        
        # Initialize the cyclic prompt manager
        print(f"Initializing cyclic prompt manager with prompt: '{cyclic_prompt}'")
        self.cyclic_prompt_manager = CyclicPromptManager(cyclic_prompt or "")
        current_prompt = self.cyclic_prompt_manager.get_cyclic_prompt()
        print(f"Cyclic prompt manager initialized. Current prompt: '{current_prompt[:50]}{'...' if len(current_prompt) > 50 else ''}'")
        
        # Initialize variables for tracking inactivity in Area 2
        self.last_activity_time = time.time()
        self.inactivity_threshold = 120  # 2 minutes in seconds
        print(f"Inactivity threshold set to {self.inactivity_threshold} seconds")
        
        # Define the text phrases to detect for each area
        self.detection_phrases = [
            "new chat",       # Area 0
            "reject accept",  # Area 1
            "resume the",     # Area 2
            "try again"       # Area 3
        ]
        print(f"Detection phrases: {self.detection_phrases}")
        
        # Store components in thread_local
        thread_local.image_analyzer = image_analyzer
        thread_local.mouse_controller = mouse_controller
        
        # Set up the workflow
        print("Setting up workflow...")
        self.setup_workflow()
        print("Workflow setup complete")
        
        print("=== SCREEN SPY AGENT INITIALIZATION COMPLETE ===")
    
    def setup_workflow(self):
        """Set up the LangGraph workflow."""
        # Create the workflow
        builder = StateGraph(AgentStateDict)
        
        # Add nodes
        builder.add_node("detect_words", AgentNode.detect_words_in_screenshot)
        builder.add_node("decide_action", AgentNode.decide_action)
        builder.add_node("execute_action", AgentNode.execute_action)
        
        # Add edges
        builder.add_edge("detect_words", "decide_action")
        builder.add_conditional_edges(
            "decide_action",
            lambda state: "execute_action" if state.get("should_click", False) else END
        )
        builder.add_edge("execute_action", END)
        
        # Set the entry point
        builder.set_entry_point("detect_words")
        
        # Compile the workflow
        self.workflow = builder.compile()
    
    def execute_start_sequence(self):
        """
        Execute the start sequence for the cyclic prompt workflow.
        
        This includes:
        1. Clicking at position [1818, 46] (new chat)
        2. Pausing for 2 seconds
        3. Typing the cyclic prompt text
        4. Pausing for 2 seconds
        5. Pressing Enter to send the message
        """
        import time
        import traceback
        
        print("=== START SEQUENCE BEGIN ===")
        print("Executing start sequence for new prompt cycle...")

        # Check if we should continue
        # Check if the stop file exists
        stop_file_path = os.path.expanduser("~/CursorAgent/screen_spy_agent/stop_screen_spy_agent")
        if os.path.exists(stop_file_path):
            print(f"Stop file exists at: {stop_file_path}")
            # Stop the agent as if the stop button was pressed
            print("Stopping agent...")
            self.stop_agent()
            # Remove the stop file
            os.remove(stop_file_path)
            # Set the agent to None to indicate it's fully stopped
            # Return a special value that can be used to update the UI
            return "agent_stopped"
        
        try:
            # Check if we should continue
            if not self.running:
                print("Start sequence cancelled - agent stopped")
                return
                
            # Click to start new chat
            print("Step 1: Clicking 'New Chat' button at coordinates [1818, 46]")
            self.mouse_controller.click_at_coordinates(1818, 46)
            print("✓ Click at 'New Chat' succeeded")
            
            # Short sleep with termination check
            for _ in range(10):  # 1 second in smaller chunks
                if not self.running:
                    print("Start sequence cancelled - agent stopped")
                    return
                time.sleep(0.1)
            
            # Get the prompt text
            print("Step 3: Preparing prompt text")
            prompt_text = self.cyclic_prompt_manager.get_cyclic_prompt()
            print(f"Current prompt text: '{prompt_text[:50]}{'...' if len(prompt_text) > 50 else ''}'")
            
            # Input text via clipboard
            if not self.running:
                print("Start sequence cancelled - agent stopped")
                return
            print("Step 4: Inputting text via clipboard")
            clipboard_success = self.mouse_controller.copy_paste_text(prompt_text)
            
            if clipboard_success:
                print("✓ Text input via clipboard succeeded")
            else:
                print("⚠️ Text input via clipboard failed")
            
            # Extra delay after typing with termination check
            for _ in range(10):  # 1 second in smaller chunks
                if not self.running:
                    print("Start sequence cancelled - agent stopped")
                    return
                time.sleep(0.1)
            
            # Press Enter to send message
            if not self.running:
                print("Start sequence cancelled - agent stopped")
                return
            print("Step 5: Pressing Enter key to send message")
            self.mouse_controller.press_key('enter')
            print("✓ Enter key press succeeded")
            
            print("✓ Start sequence completed successfully")
        except Exception as e:
            print(f"❌ Error during start sequence: {e}")
            print(f"Stack trace: {traceback.format_exc()}")
        finally:
            print("=== START SEQUENCE END ===")
            # Always yield control back to the main thread briefly
            time.sleep(0.1)
            
            # Reset the last activity time for Area 2
            self.last_activity_time = time.time()
    
    def is_area2_inactive(self, screenshot_path):
        """
        Check if Area 2 has been inactive (gray screen) for the inactivity threshold period.
        
        Args:
            screenshot_path: Path to the screenshot of Area 2.
            
        Returns:
            bool: True if Area 2 has been inactive for the threshold period, False otherwise.
        """
        try:
            print(f"Checking Area 2 inactivity with screenshot: {screenshot_path}")
            
            # Check if the screenshot shows an empty/gray screen
            is_empty = self.image_analyzer.detect_empty_screen(screenshot_path)
            print(f"Empty screen detection result: {is_empty}")
            
            current_time = time.time()
            
            if not is_empty:
                # If screen is not empty, update the last activity time
                print(f"Screen is not empty, updating last activity time to {current_time}")
                self.last_activity_time = current_time
                return False
            
            # Calculate time since last activity
            time_since_activity = current_time - self.last_activity_time
            print(f"Screen is empty. Time since last activity: {time_since_activity} seconds (threshold: {self.inactivity_threshold})")
            
            # If inactive for more than the threshold, return True
            is_inactive = time_since_activity >= self.inactivity_threshold
            print(f"Area 2 inactive status: {is_inactive}")
            return is_inactive
        except Exception as e:
            print(f"Error in is_area2_inactive: {e}")
            traceback.print_exc()
            # Don't automatically return True on exceptions
            return False
    
    def agent_loop(self):
        """The agent's main loop."""
        print("Agent started")
        
        # Make sure thread-local storage has the components
        thread_local.image_analyzer = self.image_analyzer
        thread_local.mouse_controller = self.mouse_controller
        
        # Delay the initial start sequence to avoid blocking the UI
        for _ in range(20):  # 2 seconds in smaller chunks
            if not self.running:
                return
            time.sleep(0.1)
        
        # Execute start sequence after a short delay
        if not self.running:
            return
        print("Executing initial start sequence on agent startup...")
        result = self.execute_start_sequence()
        if result == "agent_stopped":
            print("Agent was stopped by external file trigger")
            return
        
        # Reset the last activity time after initial start sequence
        self.last_activity_time = time.time()
        
        while self.running:
            try:
                # Process each screenshot area
                screenshot_paths = []
                detection_results = []
                
                # Initialize verticalShift to 0
                vertical_shift = 0
                
                restart_cycle = False
                
                for i, screenshot_taker in enumerate(self.screenshot_takers):
                    if not self.running:
                        return
                        
                    # Initialize variables with original coordinates first
                    original_x1 = screenshot_taker.x1
                    original_y1 = screenshot_taker.y1
                    original_x2 = screenshot_taker.x2
                    original_y2 = screenshot_taker.y2
                    shifted_y1 = original_y1
                    shifted_y2 = original_y2

                    # If this is not the first area, apply the vertical shift to the screenshot coordinates
                    if i > 0 and vertical_shift != 0:
                        shifted_y1 = original_y1 + vertical_shift
                        shifted_y2 = original_y2 + vertical_shift
                        print(f"Applied vertical shift {vertical_shift} to area {i}: ({original_x1}, {original_y1}) -> ({original_x1}, {shifted_y1})")
                        print(f"Applied vertical shift {vertical_shift} to area {i}: ({original_x2}, {original_y2}) -> ({original_x2}, {shifted_y2})")

                    # Capture a screenshot for this area
                    print(f"Capturing screenshot for area {i}...")
                    screenshot = screenshot_taker.capture_screenshot(original_x1, shifted_y1, original_x2, shifted_y2)
                    screenshot_path = screenshot_taker.save_screenshot(screenshot)
                    
                    # Update the agent state
                    print(f"Screenshot for area {i} saved to {screenshot_path}")
                    
                    if self.num_areas == 1:
                        self.agent_state.set_current_screenshot(screenshot_path)
                    else:
                        self.agent_state.set_current_screenshot_for_area(i, screenshot_path)
                    
                    screenshot_paths.append(screenshot_path)
                    
                    # Analyze the screenshot with the appropriate text phrase
                    print(f"Analyzing screenshot for area {i} looking for \"{self.detection_phrases[i]}\"...")
                    detection_result = self.image_analyzer.detect_text_in_image(
                        screenshot_path, 
                        text_to_detect=self.detection_phrases[i]
                    )
                    
                    # Update the agent state with the detection result
                    if self.num_areas == 1:
                        self.agent_state.update_detection(detection_result)
                    else:
                        self.agent_state.update_detection_for_area(i, detection_result)
                    
                    detection_results.append(detection_result)
                    print(f"Area {i} detection result: {detection_result}")

                    # Check for restart conditions:
                    
                    # Condition 1: Check if "new chat" is detected in Area 0
                    if i == 0 and detection_result:
                        print("\"new chat\" detected in Area 1. Restarting cycle...")
                        restart_cycle = True
                        
                        # Execute start sequence immediately for this condition
                        print("Executing start sequence due to 'new chat' detection in Area 0")
                        result = self.execute_start_sequence()
                        if result == "agent_stopped":
                            print("Agent was stopped by external file trigger")
                            return
                        
                        # Reset the last activity time for Area 2
                        self.last_activity_time = time.time()
                        
                        # No need to continue with other areas after restart
                        break
                    
                    # Condition 2: Check if Area 2 has been inactive (gray screen) for 2 minutes
                    if i == 2:
                        try:
                            is_inactive = self.is_area2_inactive(screenshot_path)
                            print(f"Area 2 inactivity check result: {is_inactive}")
                            if is_inactive:
                                print("Area 2 has been inactive for 2 minutes. Restarting cycle...")
                                restart_cycle = True
                                
                                # Execute start sequence for this condition
                                print("Executing start sequence due to Area 2 inactivity")
                                result = self.execute_start_sequence()
                                if result == "agent_stopped":
                                    print("Agent was stopped by external file trigger")
                                    return
                                
                                # Reset the last activity time for Area 2
                                self.last_activity_time = time.time()
                                
                                # No need to continue with other areas
                                break
                        except Exception as e:
                            print(f"Error checking inactivity: {e}")
                            traceback.print_exc()
                
                # Invoke the workflow with the current state
                workflow_input = {
                    "detection_history": self.agent_state.detection_history,
                    "action_history": self.agent_state.action_history,
                    "current_screenshots": screenshot_paths,
                    "both_words_detected": False,  # Will be determined by the workflow
                    "detection_results": detection_results,
                    "should_click": False,  # Will be determined by the workflow
                    "vertical_shift": vertical_shift
                }
                
                workflow_result = self.workflow.invoke(workflow_input)
                
                # Check for restart conditions and execute start sequence if needed
                if restart_cycle and not any(detection_results[:1]):  # If we didn't already restart for Area 0
                    # Execute the start sequence only if it wasn't executed in the loop
                    print("Final restart condition met - executing start sequence")
                    result = self.execute_start_sequence()
                    if result == "agent_stopped":
                        print("Agent was stopped by external file trigger")
                        return
                    
                    # Reset the last activity time for Area 2
                    self.last_activity_time = time.time()
                else:
                    # Log why we didn't trigger the restart
                    if restart_cycle:
                        print(f"Not executing final start sequence because restart_cycle={restart_cycle}")
                    if any(detection_results[:1]):
                        print(f"Not executing final start sequence because detection_results[:1]={detection_results[:1]}")
                
                # Pause before next iteration
                start_sleep_time = time.time()
                while time.time() - start_sleep_time < self.interval:
                    if not self.running:
                        return
                    time.sleep(0.1)  # Sleep in small chunks to allow for quick termination
                
            except Exception as e:
                print(f"Error in agent loop: {e}")
                traceback.print_exc()
                # Sleep in small chunks for quick termination
                start_sleep_time = time.time()
                while time.time() - start_sleep_time < self.interval:
                    if not self.running:
                        return
                    time.sleep(0.1)
    
    def run_agent(self):
        """
        Start the agent's main loop in a separate thread.
        """
        if not self.running:
            self.running = True
            
            # Create and start the thread with daemon=True to allow program to exit
            self.agent_thread = threading.Thread(target=self.agent_loop)
            self.agent_thread.daemon = True
            self.agent_thread.start()
            
            # Return immediately to avoid blocking the UI
            return True
    
    def stop_agent(self):
        """Stop the agent's main loop."""
        if self.running:
            self.running = False
            print("Agent stop requested")
            # Don't wait for the thread to join - just mark it as stopped
            # The thread will terminate itself at the next checkpoint
            print("Agent stopped")
    
    def create_stop_trigger(self):
        """Create a stop trigger file that will stop the agent on next check."""
        stop_file_path = os.path.expanduser("~/CursorAgent/screen_spy_agent/stop_screen_spy_agent")
        os.makedirs(os.path.dirname(stop_file_path), exist_ok=True)
        with open(stop_file_path, "w") as f:
            f.write("stop")
        print(f"Created stop trigger file at: {stop_file_path}")
        print("Agent will stop at next check")
        return stop_file_path
    
    def set_cyclic_prompt(self, prompt):
        """
        Set the cyclic prompt text and enable cyclic mode if a prompt is provided.
        
        Args:
            prompt (str): The cyclic prompt to use. If empty, cyclic mode will be disabled.
        """
        if self.cyclic_prompt_manager:
            self.cyclic_prompt_manager.set_cyclic_prompt(prompt)
            
            # Enable or disable cyclic mode based on whether a prompt is provided
            self.agent_state.set_cyclic_mode(bool(prompt))
            
            return True
        return False
    
    def get_cyclic_prompt(self):
        """
        Get the current cyclic prompt text.
        
        Returns:
            str: The current cyclic prompt text.
        """
        return self.cyclic_prompt_manager.get_cyclic_prompt() 