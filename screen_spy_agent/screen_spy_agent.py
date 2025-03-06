"""
ScreenSpyAgent class that ties everything together.
"""

import threading
import time
import os
import traceback
from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.runnables import chain
from langgraph.graph import END, StateGraph

from screen_spy_agent.screenshot_taker import ScreenshotTaker
from screen_spy_agent.image_analyzer import ImageAnalyzer
from screen_spy_agent.mouse_controller import MouseController
from screen_spy_agent.agent_state import AgentState
from screen_spy_agent.agent_node import AgentNode

# Thread-local storage for sharing components with nodes
thread_local = threading.local()

# Define the state schema for langgraph
class AgentStateDict(TypedDict):
    detection_history: List[bool]
    action_history: List[bool]
    current_screenshot: str
    both_words_detected: bool
    should_click: bool


class ScreenSpyAgent:
    """
    Main agent class that ties all components together.
    
    Attributes:
        screenshot_taker: ScreenshotTaker instance.
        image_analyzer: ImageAnalyzer instance.
        mouse_controller: MouseController instance.
        interval: Interval in seconds between screenshots.
        agent_state: AgentState instance.
        workflow: LangGraph workflow.
        running: Whether the agent is running.
        agent_thread: Thread for the agent loop.
    """
    
    def __init__(self, screenshot_taker, image_analyzer, mouse_controller, interval=15):
        """
        Initialize the agent with the given components.
        
        Args:
            screenshot_taker: ScreenshotTaker instance.
            image_analyzer: ImageAnalyzer instance.
            mouse_controller: MouseController instance.
            interval: Interval in seconds between screenshots.
        """
        self.screenshot_taker = screenshot_taker
        self.image_analyzer = image_analyzer
        self.mouse_controller = mouse_controller
        self.interval = interval
        self.agent_state = AgentState()
        self.running = False
        self.agent_thread = None
        
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
    
    def agent_loop(self):
        """The agent's main loop."""
        print("Agent started")
        
        # Make sure thread-local storage has the components
        thread_local.image_analyzer = self.image_analyzer
        thread_local.mouse_controller = self.mouse_controller
        
        while self.running:
            try:
                # Capture a screenshot
                print("Capturing screenshot...")
                screenshot = self.screenshot_taker.capture_screenshot()
                screenshot_path = self.screenshot_taker.save_screenshot(screenshot)
                
                # Update the agent state
                print(f"Screenshot saved to {screenshot_path}")
                self.agent_state.set_current_screenshot(screenshot_path)
                
                # Run the workflow
                print("Running workflow...")
                state_dict = self.agent_state.get_state()
                result_dict = self.workflow.invoke(state_dict)
                
                # Update the agent state from the result dictionary
                self.agent_state.detection_history = result_dict.get("detection_history", [])
                self.agent_state.action_history = result_dict.get("action_history", [])
                self.agent_state.current_screenshot = result_dict.get("current_screenshot", "")
                self.agent_state.both_words_detected = result_dict.get("both_words_detected", False)
                self.agent_state.should_click = result_dict.get("should_click", False)
                
                print(f"Words detected: {self.agent_state.both_words_detected}")
                print(f"Should click: {self.agent_state.should_click}")
                
                # Wait for the next interval
                if self.running:
                    print(f"Waiting for {self.interval} seconds...")
                    time.sleep(self.interval)
            
            except Exception as e:
                print("Error in agent loop: ")
                print(traceback.format_exc())
                time.sleep(5)  # Wait a bit before retrying
    
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