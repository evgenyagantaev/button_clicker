# Macro Recorder

A Python application for recording and playing back mouse clicks.

## Features

- Record sequences of left mouse clicks
- Save macros with unique names
- Play back recorded macros with 3-second pauses between clicks
- Manage a list of saved macros (load, delete)
- Persistent storage of macros in JSON format

## Requirements

- Python 3.6+
- PyQt5
- pyautogui
- pynput
- numpy

## Installation

1. Clone or download this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python macrorecorder.py
```

### Recording a Macro

1. Click the "Record" button to start recording
2. Perform the mouse clicks you want to record
3. Click the "Stop" button when finished
4. Enter a name for your macro in the "Macro Name" field
5. Click "Save Macro" to save it

### Playing a Macro

1. Select a macro from the list on the left
2. Click the "Play Macro" button
3. Confirm that you want to play the macro
4. The application will simulate the recorded mouse clicks with a 3-second pause between each click

### Managing Macros

- Macros are automatically saved to a file named `macros.json` in the same directory as the application
- To delete a macro, select it and click the "Delete Macro" button
- To update a macro, select it, record a new sequence, and save it with the same name

## Notes

- The application records the absolute screen coordinates of mouse clicks
- Make sure the screen elements are in the same positions during playback as they were during recording
- A confirmation dialog will appear before playing back a macro to prevent unintended actions

## License

MIT 