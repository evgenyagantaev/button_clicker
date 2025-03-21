# Manual Testing Instructions for Cyclic Prompt Feature

This document provides detailed instructions for manually testing the new cyclic prompt feature of the Screen Spy Agent.

## Prerequisites

Before beginning the tests, ensure you have:

1. The latest version of the Screen Spy Agent application installed
2. A target application that can receive text input and display chat-like interfaces
3. Python environment with all dependencies installed:
   ```
   pip install -r requirements.txt
   ```

## Test 1: Full Cycle with Actual Screen Captures

### Setup

1. Launch the GUI application:
   ```
   python run_gui.py
   ```

2. Configure the application:
   - Set up Area 1 to include the region where "new chat" text would appear
   - Set up Area 2 to monitor the main conversation area
   - Configure the following coordinates for the start sequence:
     - New Chat button: [1818, 46]
     - Input field: [1419, 108]
     - Send button: [1874, 141]

3. Enter a test cyclic prompt in the multi-line text area. Example:
   ```
   This is a test of the cyclic prompt feature.
   Please respond with "Test complete" when you receive this message.
   After you respond, I will start a new chat automatically.
   ```

### Test Procedure

1. Start the agent by clicking the "Start Agent" button in the GUI.

2. Observe the agent performing the start sequence:
   - It should click at position [1818, 46] (new chat button)
   - Wait 2 seconds
   - Click at position [1419, 108] (input field)
   - Wait 2 seconds
   - Copy the cyclic prompt to clipboard
   - Paste it into the input field
   - Wait 2 seconds
   - Click at position [1874, 141] (send button)

3. Verify that:
   - The prompt is correctly copied and pasted into the target application
   - The send button is clicked and the message is sent

4. To test restart condition 1:
   - Wait for the target application to display "new chat" in Area 1
   - Verify that the agent detects this and restarts the cycle

5. To test restart condition 2:
   - Ensure Area 2 shows an empty gray background for 2 minutes
   - Verify that the agent detects this inactivity and restarts the cycle

6. During all operations, verify that the GUI properly updates its status and displays current state information.

7. Run the test helper script to document your findings:
   ```
   python tests/manual_test_ui_interaction.py
   ```

### Expected Results

- The agent should successfully execute the start sequence
- The cyclic prompt should be correctly copied and pasted
- The agent should restart when "new chat" is detected in Area 1
- The agent should restart after 2 minutes of inactivity in Area 2
- The UI should update properly during the cycle, showing current state

## Test 2: Restart Conditions Verification

### Setup

Same as Test 1.

### Test Procedure

1. Focus specifically on testing the restart conditions:
   
   a. For "new chat" detection:
   - Start the agent with a cyclic prompt
   - After the prompt is sent, manually trigger the display of "new chat" text in Area 1
   - Measure the response time for the agent to detect this condition
   - Verify that the agent restarts the cycle correctly

   b. For inactivity detection:
   - Start the agent with a cyclic prompt
   - After the prompt is sent, ensure Area 2 remains empty/gray
   - Time how long it takes for the agent to detect 2 minutes of inactivity
   - Verify that the agent restarts the cycle correctly

2. Document the results using the test helper script.

### Expected Results

- The agent should correctly detect the "new chat" text in Area 1
- The agent should accurately measure 2 minutes of inactivity in Area 2
- Both conditions should trigger a proper restart of the cycle

## Test 3: UI Updates Verification

### Setup

Same as Test 1.

### Test Procedure

1. Focus specifically on the UI elements:
   
   a. Monitor the GUI during the entire cycle:
   - Verify that status indicators update correctly
   - Check that any progress or state information is displayed accurately
   - Ensure that error conditions are properly shown if they occur

   b. Test the interaction between the UI and the agent:
   - Stop and restart the agent during a cycle
   - Modify the cyclic prompt while the agent is running
   - Check that configuration changes are properly reflected

2. Document the results using the test helper script.

### Expected Results

- The GUI should accurately reflect the current state of the agent
- Status indicators should update in real-time
- The UI should handle agent stops/starts gracefully
- Configuration changes should be properly applied

## Reporting Issues

If you encounter any issues during testing, please:

1. Take screenshots of the problem
2. Note the exact steps to reproduce
3. Record any error messages or unexpected behaviors
4. Document your findings using the test helper script

## Test Completion

After completing all tests, generate a final test report by running:
```
python tests/manual_test_ui_interaction.py
```

This will create a log file with all your test results and observations. 