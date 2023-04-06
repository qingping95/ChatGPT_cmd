# chatgpt_cmd

A simple cmd tool for chatting with ChatGPT.
It supports proxy.

You can make some predefined instructs in `default_instructs.yaml` or another `.yaml`, and use them by setting instruct key in `--instruct=<INSTRUCT_KEY>`.
There are three default instructions: `latex_en2cn`, `en2cn`, and `cn2en`.

## Installation
```
pip install -r requirements.txt
```

## Usage
```
export OPENAI_PROXY=<YOUR_PROXY>
export OPENAI_KEY=<YOUR_OPENAI_KEY> 
python start_chat.py [OPTIONS]
```
For example:
```
export OPENAI_PROXY=localhost:6006
export OPENAI_KEY=<YOUR_OPENAI_KEY> 
python start_chat.py --instruct="You are a professional assistant"
```
or
```
python start_chat.py --instruct=en2cn
```

## Options
- `--instruct=<INSTRUCT_CONTENT_OR_KEY>` An instruct key of a predefined instruct or a sentence content of a new instruct.
- `--instructs_path` User defined instructs path.
- `--multi_line` Supports multi-lines input. You need to press two `ENTER` keys to end the input and get a reply.
                                                     
## Other                                             
- You can input `clear` to clear the context and start a new conversation.
- The history of the conversation will be saved into `./chat_history.log` in jsonline format and `./chat_history.log.readable` in a human-readable format.
