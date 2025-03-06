from setuptools import setup, find_packages

setup(
    name="screen_spy_agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-core>=0.1.10",
        "langchain-openai>=0.0.5",
        "langchain-community>=0.0.13",
        "langgraph>=0.0.20",
        "openai>=1.10.0",
        "pillow>=10.0.0",
        "pyautogui>=0.9.54",
        "pynput>=1.7.6",
        "pytest>=7.4.0",
        "pytest-mock>=3.11.1",
        "python-dotenv>=1.0.0"
    ],
) 