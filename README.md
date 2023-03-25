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
OPENAI_KEY=<YOUR_OPENAI_KEY> python start_chat.py <SYSTEM_INSTRUCT> <ARGUMENTS>
```
For example:
```
export OPENAI_PROXY=localhost:6006
OPENAI_KEY=<YOUR_OPENAI_KEY> python start_chat.py "You are a professional assistant"
```

# Argument 
- `--multi_line` supports multi-lines input. You need press two `ENTER` keys to end the input and get a reply.

# Other
- You can input `clear` to clear the context and start a new conversation.
- The history of conversation will be saved into `./chat_history.log` in jsonline format.
