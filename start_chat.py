from collections import defaultdict
from os import environ, getenv

import httpx
from fastapi import FastAPI, Form
from httpx_socks import SyncProxyTransport, AsyncProxyTransport
from typing import Optional

openai_chat_api = "https://api.openai.com/v1/chat/completions"
openai_key = environ['OPENAI_KEY'] # can be found in chatgpt/ai/api_test.ipynb
proxy = getenv('OPENAI_SOCKS5_PROXY')

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

def start_chat(instruct, multiline_input=False):
    history = [{"role": "system", "content": instruct}]
    while True:
        print('-'*40+'\n')
        if multiline_input:
            question = input_with_enter("问：")
        else:
            question = input('问：')
        if question == 'clear':
            history = [{"role": "system", "content": instruct}]
            print("已经清除历史记录，请重新提问。")
            continue
        rep = get_reply(question, history)
        print("\nChatGPT：\n", rep)

def main():
    import sys
    instruct = "你是一个专业的工作助手，需要回答各种具备专业知识的问题，要求回答严谨、精确。"
    if len(sys.argv) > 1:
        instruct = sys.argv[1]
    start_chat(instruct=instruct)

if __name__ == "__main__":
    main()
