#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/9/26 16:20
# @File  : openai_client.py.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 兼容openai的方式进行测试


from openai import OpenAI

client = OpenAI(
    api_key='EMPTY',
    base_url=f'http://127.0.0.1:8000/v1',
)
models = [model.id for model in client.models.list().data]
print(f'models: {models}')

query = 'who are you?'
messages = [{'role': 'user', 'content': query}]

resp = client.chat.completions.create(model=models[0], messages=messages, max_tokens=512, temperature=0)
query = messages[0]['content']
response = resp.choices[0].message.content
print(f'query: {query}')
print(f'response: {response}')
