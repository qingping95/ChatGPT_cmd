# chatgpt_cmd

A simple cmd tool for chatting with ChatGPT.
It supports proxy.

# Installation
```
pip install -r requirements.txt
```

# Usage
```
export OPENAI_PROXY=<YOUR_PROXY>
OPENAI_KEY=<YOUR_OPENAI_KEY> python start_chat.py <SYSTEM_INSTRUCT>
```
For example:
```
export OPENAI_PROXY=localhost:6006
OPENAI_KEY=<YOUR_OPENAI_KEY> python start_chat.py "You are a professional assistant"
```
