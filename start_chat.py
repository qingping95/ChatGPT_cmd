from audioop import mul
from collections import defaultdict
from email.policy import default
import os
from os import environ, getenv
import yaml
import argparse

import httpx
from httpx_socks import SyncProxyTransport

openai_chat_api = "https://api.openai.com/v1/chat/completions"
openai_key = environ['OPENAI_KEY'] # can be found in chatgpt/ai/api_test.ipynb
proxy = getenv('OPENAI_PROXY')

headers = {
    "Authorization": f"Bearer {openai_key}"
}

histories = defaultdict(list)

def insert_before_ext(file_name, insert):
    index = file_name.rindex('.')
    return '{}{}{}'.format(file_name[:index], insert, file_name[index:])

def load_predefined_instructs(instructs_path):
    cfg = yaml.load(open(instructs_path, encoding='utf8'), Loader=yaml.FullLoader)
    return cfg

def get_reply(prompt, history=None):
    transport = SyncProxyTransport.from_url(proxy)
    data = {}
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
                raise Exception("请求失败。\nMessage: {}".format(data))
    except Exception as e:
        return data

def save_history(history, save_path):
    """json line"""
    import json
    import time 
    with open(save_path, 'a') as f:
        f.write(time.strftime('%Y/%m/%d-%H:%M:%S '))
        json.dump(history, f)
        f.write('\n')

def save_history_with_readable_format(history, save_path):
    import time 
    with open(save_path, 'a') as f:
        f.write('>'*20+time.strftime('%Y/%m/%d-%H:%M:%S ') + '\n')
        for comment in history:
            role, content = comment['role'], comment['content']
            f.write(f'{role}: {content}\n\n')
        f.write('\n\n')

def save_and_clear_history(
    history, instruct='', save_path='chat_history.log', message="已开启新的聊天！^_^"
):
    save_history(history, save_path)
    readable_path = insert_before_ext(save_path, '_readable')
    save_history_with_readable_format(history, readable_path)
    history = [{"role": "system", "content": instruct}]
    print(message)
    return history

def input_multi_line(multi_line=False, hint=''):
    """如果multi_line=True，接受到一个空行才返回结果"""
    text = []
    pre_t = input(hint)
    while pre_t != '':
        text.append(pre_t)
        if not multi_line:
            break
        pre_t = input()
    print('<OK>')
    return ('\n'.join(text)).strip()

def input_handler(multi_line=False, hint=''):
    question = input_multi_line(multi_line=multi_line, hint=hint)
    while question == "":
        print('请输入询问内容！')
        question = input_multi_line(multi_line=multi_line, hint=hint)

    if question in {'exit', '退出'}:
        raise KeyboardInterrupt

    return question

def output_handler(reply, history, instruct, history_path):
    print("\nChatGPT：\n")
    if isinstance(reply, str):
        print(reply.strip())

    elif isinstance(reply, dict):
        try:
            if 'error' in reply:
                if reply['error']['code'] == 'context_length_exceeded':
                    history = save_and_clear_history(
                        history, instruct, save_path=history_path, 
                        message="对话超过我的长度限制啦，已为您保存历史聊天，我们开始新的聊天吧~"
                    )
                    return history
                else:
                    raise ValueError
            else:
                raise ValueError
        except ValueError as e:
            print(f"未知错误，请联系管理员。\nChatGPT返回结果：{reply}")

    return history

def start_chat(instruct, multi_line=True, history_path=None):
    history = [{"role": "system", "content": instruct}]
    try:
        while True:
            print('-'*40+'\n')

            question = input_handler(multi_line=multi_line, hint="问：")

            if question == 'clear':
                history = save_and_clear_history(history, instruct, save_path=history_path)
                continue

            rep = get_reply(question, history)
            history = output_handler(rep, history, instruct, history_path)

    except Exception as e:
        save_and_clear_history(history, save_path=history_path)
        raise e 

    except KeyboardInterrupt:
        save_and_clear_history(history, message="\n已退出聊天~", save_path=history_path)

def main():
    default_instruct = "你是一个专业的工作助手，需要回答各种具备专业知识的问题，要求回答严谨、精确。"
    parser = argparse.ArgumentParser()
    parser.add_argument('--instruct', default=default_instruct, type=str)
    parser.add_argument('--instructs_path', default='instructs.yaml', type=str)
    parser.add_argument('--history_path', default='chat_history.log', type=str)
    parser.add_argument('--multi_line', action='store_true')
    args = parser.parse_args()
    
    # Load predefined instructs
    instructs = {}
    default_instructs_path = 'default_instructs.yaml'
    if os.path.exists(default_instructs_path):
        instructs.update(load_predefined_instructs(default_instructs_path))
    if os.path.exists(args.instructs_path):
        instructs.update(load_predefined_instructs(args.instructs_path))
    elif args.instructs_path != 'instructs.yaml':
        print(f"The instructs_path ({args.instructs_path}) you given is not found.")
    print(f'Supported instruct keys: {list(instructs.keys())}')
    
    if args.instruct in instructs:
        print(f'Load predefined instruct of `{args.instruct}` whose content can be ' + \
            f'found in {default_instructs_path} or {args.instructs_path}')
        instruct = instructs[args.instruct]
    else:
        instruct = args.instruct

    start_chat(instruct=instruct, multi_line=args.multi_line, history_path=args.history_path)

if __name__ == "__main__":
    main()
