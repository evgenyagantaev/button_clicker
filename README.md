# Screen Spy Agent

An intelligent agent that monitors multiple areas of your screen, detects specific text patterns, and performs automated mouse clicks when target conditions are met.

## Features

- **Multi-Area Monitoring**: Monitors up to 4 distinct screen areas simultaneously
- **AI-Powered Text Detection**: Uses OpenAI vision models to recognize text in screenshots
- **Customizable Click Actions**: Configures specific click sequences for each detected area
- **Adaptive Position Adjustment**: Automatically adjusts click positions based on UI changes
- **User-Friendly GUI**: Dark-themed interface for easy configuration and monitoring
- **Flexible Deployment**: Runs in GUI or command-line mode
- **Configuration Persistence**: Saves settings for future use

## Architecture

The application is built using a modern agent-based architecture with LangChain and LangGraph:

- **LangGraph Workflow**: Implements a structured decision workflow for screenshot analysis
- **Component-Based Design**: Separates concerns into specialized modules
- **Thread-Safe Operation**: Runs monitoring in background threads for responsive UI
- **Configurable via Multiple Methods**: Command line, environment variables, or GUI

## Requirements

- Python 3.8+
- OpenAI API key with access to vision models
- Dependencies:
  - langchain, langchain-core, langchain-openai, langchain-community
  - langgraph
  - openai
  - pillow
  - pyautogui
  - pynput
  - python-dotenv

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/screen-spy-agent.git
   cd screen-spy-agent
   ```

2. Install the package and dependencies:
   ```
   pip install -e .
   ```
   
   Or manually install the requirements:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables in a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_API_BASE=your_api_base_url_here
   OPENAI_MODEL=vis-openai/gpt-4o-mini
   ```

## Usage

### GUI Mode (Recommended)

```
python run_gui.py
```

or

```
python main.py --gui
```

This launches the configuration interface where you can:
- Define screen areas to monitor
- Set click positions for each area
- Configure detection phrases
- Preview the screenshot areas in real-time
- Start/stop the agent
- Save your configuration

### Command Line Mode

```
python main.py
```

### Command-Line Arguments

```
python main.py [options]
```

Options:
- `--gui`: Run in GUI mode
- `--x1-1 VALUE`, `--y1-1 VALUE`, `--x2-1 VALUE`, `--y2-1 VALUE`: Coordinates for area 1
- `--x1-2 VALUE`, `--y1-2 VALUE`, `--x2-2 VALUE`, `--y2-2 VALUE`: Coordinates for area 2
- `--x1-3 VALUE`, `--y1-3 VALUE`, `--x2-3 VALUE`, `--y2-3 VALUE`: Coordinates for area 3
- `--x1-4 VALUE`, `--y1-4 VALUE`, `--x2-4 VALUE`, `--y2-4 VALUE`: Coordinates for area 4
- `--click-x VALUE`, `--click-y VALUE`: Click position coordinates
- `--interval VALUE`: Screenshot interval in seconds (default: 15)
- `--api-key VALUE`: OpenAI API key
- `--api-base VALUE`: OpenAI API base URL
- `--model VALUE`: Vision model to use

For backward compatibility, single-area mode is also supported:
- `--x1 VALUE`, `--y1 VALUE`, `--x2 VALUE`, `--y2 VALUE`: Area coordinates

## How It Works

1. The agent simultaneously monitors multiple screen areas defined by the user
2. Each area is assigned a specific text pattern to look for:
   - Area 1: "new chat"
   - Area 2: "reject accept"
   - Area 3: "resume the"
   - Area 4: "try again"
3. Screenshots are captured at regular intervals and analyzed using OpenAI's vision model
4. When specified text is detected in a particular area, the associated click action is triggered
5. The agent can adaptively adjust vertical positioning based on detected UI changes

## Project Structure

- `screen_spy_agent/`: Main package
  - `screenshot_taker.py`: Takes screenshots of specified areas
  - `image_analyzer.py`: Analyzes images using OpenAI's vision models
  - `mouse_controller.py`: Controls mouse positioning and clicking
  - `agent_state.py`: Maintains agent state during operation
  - `agent_node.py`: Defines LangGraph workflow nodes
  - `screen_spy_agent.py`: Core agent implementation
- `main.py`: Command-line entry point
- `run_gui.py`: Simplified GUI launcher
- `gui_integration.py`: GUI implementation with Tkinter
- `tests/`: Unit tests
- `setup.py`: Package installation configuration

## Development

### Running Tests

```
pytest
```

### Creating a Standalone Distribution

```
pip install pyinstaller
pyinstaller standalone_gui/screen_spy_agent.spec
```

## License

MIT