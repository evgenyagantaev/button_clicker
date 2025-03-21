## Task specification

Нужно добавить следующий функционал:
в гуи интерфейс нужно добавить текстовое многострочное поле ввода;
в этом поле ввода будет вводиться и храниться циклический промпт;
после запуска агента производятся следующие действия (стартовая последовательность, запускаем выполнение задачи):
****************************** 
клик в позиции [1818, 46] (начать новый чат);
пауза 2 секунды;
клик в позиции [1419, 108] (передача фокуса в поле ввода промпта);
пауза 2 секунды;
копирование циклического промпта в буфер обмена;
вставка промпта из буфера обмена (в поле ввода);
пауза 2 секунды;
клик в позиции [1874, 141] (нажатие кнопки "send", начало работы)
******************************
после запуска агента работает уже реализованный цикл распознаваний и кликов, до тех пор, 
пока, либо: 
в Area 1 не будет распознано словосочетание "new chat";
как только это случится, цикл прерывается и возобновляется со стартовой последовательности;
либо:
в течение 2 минут подряд в Area 2 нет совсем никаких слов и символов,
только однородный серый фон;
это означает, что текущая подзадача завершена, 
цикл прерывается и возобновляется со стартовой последовательности (запускаем новую подзадачу);

## Implementation Plan

### Part 1: Writing/Modifying Unit Tests

- [x] 1. Run all existing unit tests to check current system functionality
    ```
    pytest tests/
    ```

- [x] 2. Create a new test file for CyclicPromptManager class
    ```
    tests/test_cyclic_prompt_manager.py
    ```
    - [x] a. Test initialization with default values
    - [x] b. Test setting and getting the cyclic prompt
    - [x] c. Test clipboard operations (copy/paste)

- [x] 3. Modify ScreenSpyAgent tests to include new functionality
    ```
    tests/test_screen_spy_agent.py
    ```
    - [x] a. Create tests for the new start sequence method
    - [x] b. Test the condition monitoring logic (detect "new chat" in Area 1)
    - [x] c. Test the inactivity detection in Area 2 (gray background for 2 minutes)
    - [x] d. Test the cyclic behavior by mocking the conditions

- [x] 4. Update GUI tests to include new UI elements
    ```
    tests/test_gui_integration.py  
    ```
    - [x] a. Test the new multi-line text input field
    - [x] b. Test saving and loading cyclic prompt from configuration
    - [x] c. Test integration with the agent system

### Part 2: Implementing Code Changes

- [x] 1. Create a new CyclicPromptManager class
    ```
    screen_spy_agent/cyclic_prompt_manager.py
    ```
    - [x] a. Implement storage for the cyclic prompt
    - [x] b. Add clipboard integration (pyperclip or equivalent)
    - [x] c. Create method for executing the start sequence actions

- [x] 2. Update the ScreenSpyAgent class
    ```
    screen_spy_agent/screen_spy_agent.py
    ```
    - [x] a. Add a new field for the CyclicPromptManager
    - [x] b. Modify the agent_loop method to check for restart conditions
    - [x] c. Implement the start sequence with specific clicks and pauses
    - [x] d. Add timer functionality to track inactivity in Area 2
    - [x] e. Add logic to detect empty/gray screen in Area 2

- [x] 3. Modify the AgentState class to include new state tracking
    ```
    screen_spy_agent/agent_state.py
    ```
    - [x] a. Add timestamp tracking for inactivity detection
    - [x] b. Add state flags for the cyclic workflow

- [x] 4. Update the GUI Integration
    ```
    gui_integration.py
    ```
    - [x] a. Add a multi-line text area for the cyclic prompt
    - [x] b. Update the layout to accommodate the new field
    - [x] c. Modify the save/load configuration methods to include the prompt
    - [x] d. Update the agent toggle function to use the new workflow

- [x] 5. Add functionality to detect gray background in Area 2
    ```
    screen_spy_agent/image_analyzer.py
    ```
    - [x] a. Create a method to detect empty/gray screens
    - [x] b. Add parameter for tolerance/threshold of detection

### Part 3: Final Testing

- [x] 1. Run all unit tests to verify implementation; modify code and tests while they are all pass;
    ```
    pytest tests/
    ```

- [ ] 2. Test with real UI interaction
    - [ ] a. Manual test of the full cycle with actual screen captures
    - [ ] b. Verify the restart conditions work correctly
    - [ ] c. Check that the UI updates properly during the cycle

## Implementation Summary

The implementation adds a cyclic prompt feature to the Screen Spy Agent. Users will be able to enter a multi-line prompt in the GUI that will be automatically entered into the target application when the agent runs. The agent will follow a predefined sequence of clicks and pauses to start a new conversation, then monitor for either "new chat" appearance in Area 1 or 2 minutes of inactivity in Area 2 to restart the cycle.

This feature enhances automation capabilities by allowing continuous processing of tasks without manual intervention. The implementation follows TDD methodology to ensure reliability and maintainability.

