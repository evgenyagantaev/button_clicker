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
        # Check if screenshot_taker is a list (multiple areas) or a single instance
        if isinstance(screenshot_taker, list):
            self.screenshot_takers = screenshot_taker
            self.num_areas = len(screenshot_taker)
        else:
            self.screenshot_takers = [screenshot_taker]
            self.num_areas = 1
        
        self.image_analyzer = image_analyzer
        self.mouse_controller = mouse_controller
        self.interval = interval
        self.agent_state = AgentState(num_areas=self.num_areas)
        self.running = False
        self.agent_thread = None
        
        # Initialize the cyclic prompt manager
        self.cyclic_prompt_manager = CyclicPromptManager(cyclic_prompt or "")
        
        # Initialize variables for tracking inactivity in Area 2
        self.last_activity_time = time.time()
        self.inactivity_threshold = 120  # 2 minutes in seconds
        
        # Define the text phrases to detect for each area
        self.detection_phrases = [
            "new chat",       # Area 0
            "reject accept",  # Area 1
            "resume the",     # Area 2
            "try again"       # Area 3
        ]
        
        # Store components in thread_local
        thread_local.image_analyzer = image_analyzer
        thread_local.mouse_controller = mouse_controller
        
        # Set up the workflow
        self.setup_workflow()
    
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
        3. Clicking at position [1419, 108] (focus prompt field)
        4. Pausing for 2 seconds
        5. Copying the cyclic prompt to clipboard
        6. Pasting to the focused field
        7. Pausing for 2 seconds
        8. Clicking at position [1874, 141] (send button)
        """
        print("Executing start sequence for new prompt cycle...")
        
        # Delegate to the CyclicPromptManager's implementation
        self.cyclic_prompt_manager.execute_start_sequence(self.mouse_controller)
    
    def is_area2_inactive(self, screenshot_path):
        """
        Check if Area 2 has been inactive (gray screen) for the inactivity threshold period.
        
        Args:
            screenshot_path: Path to the screenshot of Area 2.
            
        Returns:
            bool: True if Area 2 has been inactive for the threshold period, False otherwise.
        """
        # Check if the screenshot shows an empty/gray screen
        is_empty = self.image_analyzer.detect_empty_screen(screenshot_path)
        
        current_time = time.time()
        
        if not is_empty:
            # If screen is not empty, update the last activity time
            self.last_activity_time = current_time
            return False
        
        # Calculate time since last activity
        time_since_activity = current_time - self.last_activity_time
        
        # If inactive for more than the threshold, return True
        return time_since_activity >= self.inactivity_threshold
    
    def agent_loop(self):
        """The agent's main loop."""
        print("Agent started")
        
        # Make sure thread-local storage has the components
        thread_local.image_analyzer = self.image_analyzer
        thread_local.mouse_controller = self.mouse_controller
        
        # Execute the start sequence only at the beginning if in cyclic mode
        if self.cyclic_prompt_manager and self.cyclic_prompt_manager.get_cyclic_prompt():
            self.execute_start_sequence()
        
        while self.running:
            try:
                # Process each screenshot area
                screenshot_paths = []
                detection_results = []
                
                # Initialize verticalShift to 0
                vertical_shift = 0
                
                restart_cycle = False
                
                for i, screenshot_taker in enumerate(self.screenshot_takers):
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
                        
                    # Condition 2: Check if Area 2 has been inactive (gray screen) for 2 minutes
                    if i == 2:
                        is_inactive = self.is_area2_inactive(screenshot_path)
                        if is_inactive:
                            print("Area 2 has been inactive for 2 minutes. Restarting cycle...")
                            restart_cycle = True
                
                # Detect vertical shift if no clicks were made on the current cycle
                # This is unchanged from the original implementation
                try:
                    # Set vertical shift based on relative positions of text detections
                    if vertical_shift == 0 and self.num_areas > 1:
                        # Calculate the vertical shift
                        # This part is application-specific; we're essentially
                        # determining how much the UI has shifted vertically
                        # based on the position of detected elements
                        
                        # For simplicity, we use a hardcoded shift value in this example
                        # In a real app, you'd calculate this based on your text detections
                        vertical_shift = -23  # Example shift value
                        print(f"Vertical shift set to: {vertical_shift}")
                except Exception as e:
                    print(f"Error detecting vertical shift: {e}")
                
                # Restart the cycle if conditions are met
                if restart_cycle:
                    # Execute the start sequence to begin a new cycle
                    self.execute_start_sequence()
                    # Continue to next iteration (skip the LangGraph workflow)
                    continue
                
                # Create the state dictionary for LangGraph
                state = {
                    "detection_history": self.agent_state.detection_history,
                    "action_history": self.agent_state.action_history,
                    "both_words_detected": False,
                    "detection_results": detection_results,
                    "should_click": False,
                    "vertical_shift": vertical_shift
                }
                
                # Add screenshot info based on mode (single area vs multiple areas)
                if self.agent_state.num_areas == 1:
                    state["current_screenshot"] = self.agent_state.current_screenshot
                    state["current_screenshots"] = []
                else:
                    state["current_screenshots"] = self.agent_state.current_screenshots
                    state["current_screenshot"] = ""
                
                # Run the workflow
                print("Running workflow...")
                result = self.workflow.invoke(state)
                print(f"Workflow result: {result}")
                
                # Sleep for the interval
                time.sleep(self.interval)
            except Exception as e:
                print(f"Error in agent loop: {e}")
                traceback.print_exc()
                time.sleep(5)  # Sleep briefly before trying again
    
    def run_agent(self):
        """Start the agent's main loop in a separate thread."""
        if not self.running:
            self.running = True
            self.agent_thread = threading.Thread(target=self.agent_loop)
            self.agent_thread.daemon = True
            self.agent_thread.start()
    
    def stop_agent(self):
        """Stop the agent's main loop."""
        if self.running:
            self.running = False
            if self.agent_thread:
                self.agent_thread.join(timeout=10)
            print("Agent stopped")
    
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