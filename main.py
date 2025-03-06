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
    
    # Screenshot area coordinates
    parser.add_argument("--x1", type=int, help="Left coordinate of the screen area")
    parser.add_argument("--y1", type=int, help="Top coordinate of the screen area")
    parser.add_argument("--x2", type=int, help="Right coordinate of the screen area")
    parser.add_argument("--y2", type=int, help="Bottom coordinate of the screen area")
    
    # Mouse click coordinates
    parser.add_argument("--click-x", type=int, help="X coordinate to click at")
    parser.add_argument("--click-y", type=int, help="Y coordinate to click at")
    
    # Interval
    parser.add_argument("--interval", type=int, help="Interval in seconds between screenshots")
    
    # API settings
    parser.add_argument("--api-key", type=str, help="OpenAI API key")
    parser.add_argument("--api-base", type=str, help="OpenAI API base URL")
    parser.add_argument("--model", type=str, help="Model to use for image analysis")
    
    return parser.parse_args()


def main():
    """Main function."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    args = parse_args()
    
    # Get API credentials from environment variables or command line arguments
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY", "")
    api_base = args.api_base or os.environ.get("OPENAI_API_BASE", "")
    model = args.model or os.environ.get("OPENAI_MODEL", "vis-openai/gpt-4o-mini")
    
    # Get screenshot area coordinates from environment variables or command line arguments
    x1 = args.x1 if args.x1 is not None else int(os.environ.get("SCREENSHOT_X1", "0"))
    y1 = args.y1 if args.y1 is not None else int(os.environ.get("SCREENSHOT_Y1", "0"))
    x2 = args.x2 if args.x2 is not None else int(os.environ.get("SCREENSHOT_X2", "100"))
    y2 = args.y2 if args.y2 is not None else int(os.environ.get("SCREENSHOT_Y2", "100"))
    
    # Get mouse click coordinates from environment variables or command line arguments
    click_x = args.click_x if args.click_x is not None else int(os.environ.get("CLICK_X", "50"))
    click_y = args.click_y if args.click_y is not None else int(os.environ.get("CLICK_Y", "50"))
    
    # Get interval from environment variables or command line arguments
    interval = args.interval if args.interval is not None else int(os.environ.get("INTERVAL", "15"))
    
    if not api_key:
        raise ValueError("API key is required. Set it with --api-key or OPENAI_API_KEY environment variable.")
    
    if not api_base:
        raise ValueError("API base URL is required. Set it with --api-base or OPENAI_API_BASE environment variable.")
    
    # Create components
    screenshot_taker = ScreenshotTaker(x1, y1, x2, y2, interval)
    image_analyzer = ImageAnalyzer(api_key, api_base, model)
    mouse_controller = MouseController(click_x, click_y)
    
    # Create and run agent
    agent = ScreenSpyAgent(screenshot_taker, image_analyzer, mouse_controller, interval)
    
    print(f"Starting Screen Spy Agent with the following settings:")
    print(f"  Screenshot area: ({x1}, {y1}) to ({x2}, {y2})")
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