# Screen Spy Agent

An autonomous agent that monitors a specific area of the screen for the presence of the words "Accept" and "Reject", and performs a mouse click when both are detected.

## Features

- Takes screenshots of a specific area of the screen at regular intervals
- Analyzes screenshots using OpenAI's vision model to detect text
- Performs a mouse click at a specified location when both "Accept" and "Reject" are detected
- Configurable via command line arguments or environment variables

## Requirements

- Python 3.8+
- OpenAI API key with access to vision models

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/screen-spy-agent.git
   cd screen-spy-agent
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your configuration (see `.env.example` for reference):
   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your OpenAI API key and other settings.

## Usage

### Basic Usage

```
python main.py
```

This will start the agent with the settings from your `.env` file.

### Command Line Arguments

You can override the settings from the `.env` file with command line arguments:

```
python main.py --x1 100 --y1 200 --x2 300 --y2 400 --click-x 150 --click-y 250 --interval 10
```

### Available Arguments

- `--x1`, `--y1`, `--x2`, `--y2`: Coordinates of the screen area to monitor
- `--click-x`, `--click-y`: Coordinates where to click when both words are detected
- `--interval`: Interval in seconds between screenshots
- `--api-key`: OpenAI API key
- `--api-base`: OpenAI API base URL
- `--model`: Model to use for image analysis

## How It Works

1. The agent takes a screenshot of the specified area every `interval` seconds
2. The screenshot is saved to the current directory with a timestamp
3. The screenshot is sent to the OpenAI vision model for analysis
4. If both "Accept" and "Reject" are detected in the image, the agent performs a mouse click at the specified coordinates
5. The process repeats until the agent is stopped

## Development

### Running Tests

```
python -m pytest
```

### Project Structure

- `screen_spy_agent/`: Main package
  - `screenshot_taker.py`: Module for taking screenshots
  - `image_analyzer.py`: Module for analyzing images with OpenAI
  - `mouse_controller.py`: Module for controlling the mouse
  - `agent_state.py`: Module for maintaining agent state
  - `agent_node.py`: Module defining agent workflow nodes
  - `screen_spy_agent.py`: Main agent class
- `tests/`: Test directory
- `main.py`: Entry point script
- `.env.example`: Example environment variables
- `requirements.txt`: Required packages

## License

MIT 