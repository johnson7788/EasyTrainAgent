#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/9/29 11:13
# @File  : mcp_cal_plugin_test.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 测试下mcp_call_scheduler是否可用

import json
from swift.llm.infer.protocol import ChatCompletionResponseChoice
from swift.llm import RolloutInferRequest
from plugin import multi_turns


# 模拟一个工具调用请求
def simulate_tool_call():
    # 假设你的MCP服务工具可以做一些简单的计算
    response_choice = ChatCompletionResponseChoice(
        index=0,  # Example index, you can change this as per your use case
        message={'role': 'user', 'content': 'What is 3 + 5?'},
        finish_reason='stop',  # Example finish_reason, you can set it to 'stop', 'length', or None
        token_ids=[101, 202, 303],  # Example token
    )

    # 模拟一个 RolloutInferRequest
    infer_request = RolloutInferRequest(messages=[{'role': 'user', 'content': 'What is 3 + 5?'}])

    # MCPCallScheduler
    mcp_scheduler = multi_turns['mcp_call_scheduler'](max_turns=5)

    # 调用 `step` 方法，模拟工具调用
    result = mcp_scheduler.step(infer_request, response_choice, current_turn=1)

    # 输出调度器返回的结果
    print("Test result:")
    print(f"Infer Request Messages: {infer_request.messages}")
    print(f"Response Token IDs: {result['response_token_ids']}")
    print(f"Response Loss Mask: {result['response_loss_mask']}")
    print(f"Rollout Infos: {result['rollout_infos']}")

if __name__ == '__main__':
    # 运行测试
    simulate_tool_call()
