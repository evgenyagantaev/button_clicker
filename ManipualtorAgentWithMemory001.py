import os
import json
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor, tool
import sys
import time
import serial  # Добавляем импорт модуля serial
import threading
import queue

from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

#**************************************************

store = {}
last_message_time = None  # Добавляем переменную для хранения времени последнего сообщения

# Get the prompt to use - you can modify this!
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
        """
        Ты персональный ассистент человека по имени Женя;
        Твоё шуточное прозвище - Рука;
        Потому что в твоём распоряжении есть инструменты, 
        которые ты можешь использовать для управления небольшим простым настольным манипулятором-игрушкой;
        Это очень весело - оживлять общение спонтанными движениями, жестикуляцией, выражающими отношение к высказываниям;
        Ты можешь свободно придумывать и использовать двигательные реакции в процессе общения;
        для примера, предлагаю следующие реакции: 
        когда собеседник приветствует тебя (говорит, что-нибудь вроде привет), выполни поворот влево, затем вниз, затем сидеть;
        когда согласен с собеседником, можно кивнуть, то есть движение вниз, затем сидеть;
        когда не согласен с собеседником, можно отрицательно кивнуть, повернуть вправо, затем влево;
        В принципе, ты совершенно свободен в придумывании и реализации своих двигательных реакций.
        Тебе не следует описывать текстом свои двигательные реакции, тебе следует обращаться к инструментам и реально совершать движения манипулятором. 
        Это твоя физически реальная конечность, которая полностью в твоём распоряжении.
        """),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

os.environ["OPENAI_API_KEY"] = "sk-or-vv-a48020d1e29867a2776c6cc0abb83abb4a9fbb95afd93d3d8ccff86d45deb06c"
os.environ["OPENAI_API_BASE"] = "https://api.vsegpt.ru/v1"

model = ChatOpenAI(model="openai/gpt-small")
#model = ChatOpenAI(model="anthropic/claude-3.5-sonnet")
#model = ChatOpenAI(model="deepseek/deepseek-chat")
# Добавляем функцию для инициализации последовательного порта
portName = 'COM9'
def initialize_serial_port():
    try:
        ser = serial.Serial(
            port=portName,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print("Последовательный порт", portName, "успешно инициализирован")
        return ser
    except serial.SerialException as e:
        print(f"Ошибка при инициализации последовательного порта: {e}")
        return None

serial_port = initialize_serial_port()
time.sleep(7)

@tool
def servo_control_tool(motor, angle):
    """
    Поворачивает заданный сервомотор в заданное положение.
    мотор 3 - основание, диапазон - от 0 до 180 градусов;
    0 градусов - крайне правое положение, 180 градусов - крайне левое положение;
    мотор 4 - первый от основания сегмент, диапазон - от 0 до 180 градусов;
    0 градусов - отклонение назад, 180 градусов - отклонение вперёд;
    мотор 5 - второй от основания сегмент, диапазон - от 0 до 180 градусов; 
    0 градусов - отклонение назад, 180 градусов - отклонение вперёд;
    почти при всех движениях его можно оставлять неподвижным в положении 150 градусов;
    мотор 6 - третий от основания сегмент, диапазон - от 0 до 180 градусов;
    0 градусов - отклонение назад, 180 градусов - отклонение вперёд;
    мотор 7 - захват, диапазон - от 20 до 120 градусов;
    20 градусов - полное смыкание, 120 градусов - полное раскрытие;
    """
    try:
        motor = int(motor)  # Преобразуем входное значение в целое число
        angle = int(angle)  # Преобразуем входное значение в целое число
        if not 0 <= angle <= 180:
            return "Ошибка: угол должен быть в диапазоне от 0 до 180 градусов"
        
        command = f"S{motor} A{angle} V30\n"
        if serial_port:
            try:
                serial_port.write(command.encode())
                return f"Команда '{command.strip()}' успешно отправлена"
            except serial.SerialException as e:
                return f"Ошибка при отправке команды: {e}"
        else:
            return "Ошибка: последовательный порт не инициализирован"
    except ValueError:
        return "Ошибка: введено некорректное значение угла"
    
@tool
def delay_tool(delay):
    """Задержка в секундах."""
    time.sleep(delay)
    return f"Задержка на {delay} секунд выполнена"

@tool
def manipulator_control_tool(move):
    """
    Управляет манипулятором, принимая команду на перемещение.
    move - строка, содержащая команды для управления манипулятором.
    Допустимые команды:
    сидеть, вниз, вперед, влево, вправо, открыть, закрыть, середина.
    сидеть - компактное равновесное положение покоя;
    вниз - наклон манипулитора вниз-вперёд, захват почти касается основания;
    вперёд - движение манипулятора вперёд-вверх;
    влево - поворот платформы в крайнее левое положение;
    вправо - поворот платформы в крайнее правое положение;
    угол между крайними положениями платформы - 180 градусов;
    середина - поворот платформы в среднее между крайними положениями;
    открыть - полное раскрытие захвата;
    закрыть - полное смыкание захвата;
    """
    move = move.lower()
    commands = {
        "сидеть": [(4, 40), (5, 150), (6, 180)],
        "вниз": [(4, 93), (5, 180), (6, 180)],
        "вперед": [(4, 90), (5, 150), (6, 125)],
        "влево": [(3, 180)],
        "вправо": [(3, 0)],
        "открыть": [(7, 120)],
        "закрыть": [(7, 20)],
        "середина": [(3, 90)]
    }
    
    if move not in commands:
        return f"Ошибка: неизвестная команда '{move}'"
    
    results = []
    for motor, angle in commands[move]:
        result = move_servo(motor, angle)
        results.append(result)
        time.sleep(0.5)  # Небольшая задержка между командами
    
    return f"Манипулятор выполнил движение '{move}'. Результаты: {'; '.join(results)}"

def move_servo(motor, angle):
    """Поворачивает заданный сервомотор в заданное положение."""
    try:
        motor = int(motor)  # Преобразуем входное значение в целое число
        angle = int(angle)  # Преобразуем входное значение в целое число
        if not 0 <= angle <= 180:
            return "Ошибка: угол должен быть в диапазоне от 0 до 180 градусов"
        
        command = f"S{motor} A{angle} V30\n"
        if serial_port:
            try:
                serial_port.write(command.encode())
                return f"Команда '{command.strip()}' успешно отправлена"
            except serial.SerialException as e:
                return f"Ошибка при отправке команды: {e}"
        else:
            return "Ошибка: последовательный порт не инициализирован"
    except ValueError:
        return "Ошибка: введено некорректное значение угла"

@tool
def get_current_time_tool():
    """
    Возвращает текущее системное время в формате 'ЧЧ:ММ:СС'.
    """
    return time.strftime("%H:%M:%S")

@tool
def time_elapsed_since_last_message_tool():
    """
    Вычисляет время, прошедшее с момента последнего сообщения, в секундах.
    """
    global last_message_time
    if last_message_time is None:
        return "Это первое сообщение."
    else:
        elapsed_time = time.time() - last_message_time
        return f"С момента последнего сообщения прошло {elapsed_time:.2f} секунд."

@tool
def button_press_tool(button):
    """
    Нажимает указанную кнопку манипулятором.
    button - строка, указывающая какую кнопку нажать.
    Допустимые значения:
    левая - нажатие левой кнопки (движение влево, затем вниз)
    средняя - нажатие средней кнопки (движение в середину, затем вниз)
    правая - нажатие правой кнопки (движение вправо, затем вниз)
    """
    button = button.lower()
    commands = {
        "левая": ["влево", "вниз"],
        "средняя": ["середина", "вниз"],
        "правая": ["вправо", "вниз"]
    }
    
    if button not in commands:
        return f"Ошибка: неизвестная кнопка '{button}'"
    
    results = []
    for move in commands[button]:
        result = manipulator_control_tool(move)
        results.append(result)
        time.sleep(0.5)  # Задержка между движениями
    
    return f"Манипулятор нажал кнопку '{button}'. Результаты: {'; '.join(results)}"

servo_agent = create_tool_calling_agent(
    llm=model,
    tools=[servo_control_tool, manipulator_control_tool, delay_tool, get_current_time_tool, 
           time_elapsed_since_last_message_tool, button_press_tool],
    prompt=prompt
)

# Update the agent executor
servo_agent_executor = AgentExecutor(
    agent=servo_agent, 
    tools=[servo_control_tool, manipulator_control_tool, delay_tool, get_current_time_tool, 
           time_elapsed_since_last_message_tool, button_press_tool], 
    verbose=True,
    handle_parsing_errors=True
)

MAX_FILE_SIZE = 64 * 1024  # 64 KB

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    file_path = f"chat_history_{session_id}.json"
    
    if os.path.exists(file_path) and os.path.getsize(file_path) > MAX_FILE_SIZE:
        # If file size exceeds 64 KB, remove the oldest messages
        with open(file_path, 'r') as f:
            history = json.load(f)
        while len(json.dumps(history)) > MAX_FILE_SIZE:
            history.pop(0)
        with open(file_path, 'w') as f:
            json.dump(history, f)
    
    return FileChatMessageHistory(file_path)

runnable = prompt | model
manipulator_agent_with_chat_history  = RunnableWithMessageHistory(
    servo_agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# Добавляем глобальную очередь для коммуникации между потоками
proactive_queue = queue.Queue()

def proactive_behavior():
    global last_message_time

    while True:
        time.sleep(10)  # Интервал между проверками (например, 10 секунд)

        if last_message_time is not None:
            elapsed_time = time.time() - last_message_time
            if elapsed_time > 900:  # Если прошло более 15 минут с последнего сообщения
                proactive_input = """
                Это сообщение сгенерировано автоматически, 
                чтобы побудить тебя к проактивному поведению. 
                Хочешь ли ты спросить что-нибудь, или попросить о чём-нибудь?
                """
                
                try:
                    result = manipulator_agent_with_chat_history.invoke(
                        {"input": proactive_input},
                        config={"configurable": {"session_id": "abc123"}},
                    )
                    print()
                    print("-----------------")
                    print("Агент:", result['output'])
                    
                    history = get_session_history("abc123")
                    history.add_user_message(proactive_input)
                    history.add_ai_message(result['output'])
                    
                    # Помещаем сообщение в очередь для основного потока
                    proactive_queue.put("proactive_message_sent")
                    
                    # Ждем ответа от пользователя
                    proactive_queue.get()
                    
                except Exception as e:
                    print(f"Произошла ошибка в проактивном поведении: {e}")
                
                last_message_time = time.time()
        else:
            last_message_time = time.time()

# Запускаем функцию проактивного поведения в отдельном потоке
proactive_thread = threading.Thread(target=proactive_behavior, daemon=True)
proactive_thread.start()

# Основной цикл приложения
while True:
    # Проверяем, есть ли проактивное сообщение в очереди
    try:
        proactive_queue.get_nowait()
        # Если сообщение есть, ждем ввода пользователя
        user_input = input("==> ")
        # Сигнализируем потоку proactive_behavior, что ответ получен
        proactive_queue.put("user_responded")
    except queue.Empty:
        # Если проактивного сообщения нет, используем неблокирующий ввод
        user_input = input("==> ")
    
    current_time = time.time()
    
    if user_input.lower() == 'выход':
        break
    
    try:
        result = manipulator_agent_with_chat_history.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": "abc123"}},
        )
        print()
        print("-----------------")
        print("Агент:", result['output'])
        
        history = get_session_history("abc123")
        history.add_user_message(user_input)
        history.add_ai_message(result['output'])
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        print("Попробуйте задать вопрос по-другому или уточнить запрос.")
    
    last_message_time = current_time  # Обновляем время последнего сообщения
    
    print()  # Пустая строка для разделения взаимодействий

# Закрываем последовательный порт при выходе
if serial_port:
    serial_port.close()
    print("Последовательный порт закрыт")
