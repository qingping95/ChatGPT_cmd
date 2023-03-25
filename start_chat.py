from collections import defaultdict
from os import environ, getenv

import httpx
from httpx_socks import SyncProxyTransport

openai_chat_api = "https://api.openai.com/v1/chat/completions"
openai_key = environ['OPENAI_KEY'] # can be found in chatgpt/ai/api_test.ipynb
proxy = getenv('OPENAI_PROXY')

headers = {
    "Authorization": f"Bearer {openai_key}"
}

histories = defaultdict(list)

def get_reply(prompt, history=None):
    transport = SyncProxyTransport.from_url(proxy)
    try:
        if history is None:
            history = []
        history.append({"role": "user", "content": prompt})
        with httpx.Client(transport=transport) as client:
            resp = client.post(openai_chat_api, json={"model": "gpt-3.5-turbo", "messages": history}, headers=headers,
                                     timeout=5 * 60)
            data = resp.json()
            if data.get('choices'):
                reply = data['choices'][0]['message']
                history.append(reply)
                return reply['content']
            else:
                raise Exception("No Response. \n{}".format(data))
    except Exception as e:
        import logging
        logging.exception(e)
        return "请求失败，请重试"

def input_with_enter(hint=''):
    """遇到一个空行返回结果"""
    text = []
    pre_t = input(hint)
    while pre_t != '':
        text.append(pre_t)
        pre_t = input()
    print('<OK>')
    return '\n'.join(text)

def save_history(history, save_path):
    """json line"""
    import json
    import time 
    with open(save_path, 'a') as f:
        f.write(time.strftime('%Y/%m/%d-%H:%M:%S '))
        json.dump(history, f)
        f.write('\n')

def save_and_clear_history(history, instruct='', save_path='chat_history.log'):
    save_history(history, save_path)
    history = [{"role": "system", "content": instruct}]
    print("已经清除历史记录，请重新提问。")
    return history

def start_chat(instruct, multiline_input=True):
    history = [{"role": "system", "content": instruct}]
    try:
        while True:
            print('-'*40+'\n')
            if multiline_input:
                question = input_with_enter("问：")
            else:
                question = input('问：')
            if question == 'clear':
                history = save_and_clear_history(history, instruct)
                continue
            # history = [{"role": "system", "content": instruct}]
            rep = get_reply(question, history)
            print("\nChatGPT：\n", rep)
    except Exception as e:
        save_and_clear_history(history)
        raise e 

def main():
    import sys, argparse
    instruct = "你是一个专业的工作助手，需要回答各种具备专业知识的问题，要求回答严谨、精确。"
    parser = argparse.ArgumentParser()
    parser.add_argument('instruct', default=instruct)
    parser.add_argument('--multi_line', action='store_true')
    args = parser.parse_args()
    start_chat(instruct=args.instruct, multiline_input=args.multi_line)

if __name__ == "__main__":
    main()
