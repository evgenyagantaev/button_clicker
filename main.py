"""
Main script to run the Screen Spy Agent.
"""

import os
import argparse
import time
from dotenv import load_dotenv
from screen_spy_agent.screenshot_taker import ScreenshotTaker
from screen_spy_agent.image_analyzer import ImageAnalyzer
from screen_spy_agent.mouse_controller import MouseController
from screen_spy_agent.screen_spy_agent import ScreenSpyAgent


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Screen Spy Agent")
    
    # Screenshot area coordinates for multiple areas
    for i in range(1, 5):  # 4 areas
        parser.add_argument(f"--x1-{i}", type=int, help=f"Left coordinate of the screen area {i}")
        parser.add_argument(f"--y1-{i}", type=int, help=f"Top coordinate of the screen area {i}")
        parser.add_argument(f"--x2-{i}", type=int, help=f"Right coordinate of the screen area {i}")
        parser.add_argument(f"--y2-{i}", type=int, help=f"Bottom coordinate of the screen area {i}")
    
    # For backward compatibility
    parser.add_argument("--x1", type=int, help="Left coordinate of the screen area (legacy)")
    parser.add_argument("--y1", type=int, help="Top coordinate of the screen area (legacy)")
    parser.add_argument("--x2", type=int, help="Right coordinate of the screen area (legacy)")
    parser.add_argument("--y2", type=int, help="Bottom coordinate of the screen area (legacy)")
    
    # Mouse click coordinates
    parser.add_argument("--click-x", type=int, help="X coordinate to click at")
    parser.add_argument("--click-y", type=int, help="Y coordinate to click at")
    
    # Interval
    parser.add_argument("--interval", type=int, help="Interval in seconds between screenshots")
    
    # API settings
    parser.add_argument("--api-key", type=str, help="OpenAI API key")
    parser.add_argument("--api-base", type=str, help="OpenAI API base URL")
    parser.add_argument("--model", type=str, help="Model to use for image analysis")
    
    # GUI mode flag
    parser.add_argument("--gui", action="store_true", help="Run with GUI interface")
    
    return parser.parse_args()


def main():
    """Main function."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    args = parse_args()
    
    # Check if GUI mode is enabled
    if args.gui:
        try:
            # Import here to avoid dependency issues if tkinter is not available
            from gui_integration import main as gui_main
            gui_main()
            return
        except ImportError as e:
            print(f"Error loading GUI: {e}")
            print("Running in command line mode instead.")
    
    # Get API credentials from environment variables or command line arguments
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY", "")
    api_base = args.api_base or os.environ.get("OPENAI_API_BASE", "")
    model = args.model or os.environ.get("OPENAI_MODEL", "vis-openai/gpt-4o-mini")
    
    # Get interval from environment variables or command line arguments
    interval = args.interval if args.interval is not None else int(os.environ.get("INTERVAL", "15"))
    
    # Get mouse click coordinates from environment variables or command line arguments
    click_x = args.click_x if args.click_x is not None else int(os.environ.get("CLICK_X", "50"))
    click_y = args.click_y if args.click_y is not None else int(os.environ.get("CLICK_Y", "50"))
    
    if not api_key:
        raise ValueError("API key is required. Set it with --api-key or OPENAI_API_KEY environment variable.")
    
    if not api_base:
        raise ValueError("API base URL is required. Set it with --api-base or OPENAI_API_BASE environment variable.")
    
    # Create screenshot takers for multiple areas
    screenshot_takers = []
    
    # Check if legacy coordinates are provided
    if args.x1 is not None or args.y1 is not None or args.x2 is not None or args.y2 is not None:
        # Use legacy coordinates for the first area
        x1 = args.x1 if args.x1 is not None else int(os.environ.get("SCREENSHOT_X1", "0"))
        y1 = args.y1 if args.y1 is not None else int(os.environ.get("SCREENSHOT_Y1", "0"))
        x2 = args.x2 if args.x2 is not None else int(os.environ.get("SCREENSHOT_X2", "100"))
        y2 = args.y2 if args.y2 is not None else int(os.environ.get("SCREENSHOT_Y2", "100"))
        
        screenshot_takers.append(ScreenshotTaker(x1, y1, x2, y2, interval))
        
        # Use default values for the other areas
        for i in range(2, 5):
            x1 = int(os.environ.get(f"SCREENSHOT_X1_{i}", str(100 * (i-1))))
            y1 = int(os.environ.get(f"SCREENSHOT_Y1_{i}", "0"))
            x2 = int(os.environ.get(f"SCREENSHOT_X2_{i}", str(100 * i)))
            y2 = int(os.environ.get(f"SCREENSHOT_Y2_{i}", "100"))
            
            screenshot_takers.append(ScreenshotTaker(x1, y1, x2, y2, interval))
    else:
        # Use the new coordinates for all areas
        for i in range(1, 5):
            x1_arg = getattr(args, f"x1_{i}")
            y1_arg = getattr(args, f"y1_{i}")
            x2_arg = getattr(args, f"x2_{i}")
            y2_arg = getattr(args, f"y2_{i}")
            
            x1 = x1_arg if x1_arg is not None else int(os.environ.get(f"SCREENSHOT_X1_{i}", str(100 * (i-1))))
            y1 = y1_arg if y1_arg is not None else int(os.environ.get(f"SCREENSHOT_Y1_{i}", "0"))
            x2 = x2_arg if x2_arg is not None else int(os.environ.get(f"SCREENSHOT_X2_{i}", str(100 * i)))
            y2 = y2_arg if y2_arg is not None else int(os.environ.get(f"SCREENSHOT_Y2_{i}", "100"))
            
            screenshot_takers.append(ScreenshotTaker(x1, y1, x2, y2, interval))
    
    # Create components
    image_analyzer = ImageAnalyzer(api_key, api_base, model)
    mouse_controller = MouseController(click_x, click_y)
    
    # Create and run agent
    agent = ScreenSpyAgent(screenshot_takers, image_analyzer, mouse_controller, interval)
    
    print(f"Starting Screen Spy Agent with the following settings:")
    for i, taker in enumerate(screenshot_takers):
        print(f"  Screenshot area {i+1}: ({taker.x1}, {taker.y1}) to ({taker.x2}, {taker.y2})")
    print(f"  Click position: ({click_x}, {click_y})")
    print(f"  Interval: {interval} seconds")
    print(f"  Model: {model}")
    
    try:
        agent.run_agent()
        
        # Keep the main thread running
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nStopping agent...")
        agent.stop_agent()
        print("Agent stopped.")


if __name__ == "__main__":
    main() 