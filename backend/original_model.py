#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 本地模型评测版（Ollama + MCP）：使用 MCP 服务器发现的工具进行通用 QueryAgent 测试
#
# 依赖:
#   pip install python-dotenv langgraph langchain-core langchain-ollama langchain-mcp-adapters
# 运行前准备:
#   1) 安装和启动 Ollama 并拉取模型
#      curl -fsSL https://ollama.com/install.sh | sh
#      ollama pull qwen3:4b
#   2) 准备 MCP 配置文件（默认 mcp_config.json），并启动对应 MCP 服务器
#   3) 在 .env 中设置:
#      OLLAMA_MODEL=qwen3:4b
#      OLLAMA_BASE_URL=http://localhost:11434
#      MCP_CONFIG=mcp_config.json
#      QUESTION=现在的日期与时间分别是多少？
#   4) prompt 模块沿用训练时的 rl_train/prompt.py（含 ROLLOUT_SYSTEM_PROMPT / ROLLOUT_USER_PROMPT）

import os
import uuid
import asyncio
from typing import Optional, List

import dotenv
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

# === MCP: 与训练/推理保持一致 ===
from langchain_mcp_adapters.client import MultiServerMCPClient
from rl_train.mcp_config_load import load_mcp_servers
# 提示词沿用训练阶段
from rl_train import prompt

dotenv.load_dotenv()

MCP_CONFIG = os.getenv("MCP_CONFIG", "mcp_config.json")

async def run_agent_eval(question: str):
    """
    使用本地 Ollama 模型 + MCP 工具执行一次 ReAct 推理，输出完整轨迹与最终答案。
    """
    # 1) 发现 MCP 工具
    if not os.path.exists(MCP_CONFIG):
        raise FileNotFoundError(f"MCP 配置文件不存在: {MCP_CONFIG}")
    mcp_servers = load_mcp_servers(MCP_CONFIG)
    mcp_client = MultiServerMCPClient(mcp_servers)
    lc_tools = await mcp_client.get_tools()

    if not lc_tools:
        raise RuntimeError("未从 MCP 发现任何可用工具，请先启动 MCP 服务器并检查配置。")

    # 2) 将已发现的工具名注入系统提示（与训练保持一致）
    tool_names_for_prompt: List[str] = [getattr(t, "name", str(t)) for t in lc_tools]
    tools_json_note = f"已发现 MCP 工具：{tool_names_for_prompt}（按各自 JSON Schema 传参）"

    system_prompt = prompt.ROLLOUT_SYSTEM_PROMPT.format(tools_json_note=tools_json_note)

    # 用户提示：优先使用 {question}，否则回退到 {topic}
    try:
        user_msg = prompt.ROLLOUT_USER_PROMPT.format(question=question)
    except Exception:
        user_msg = prompt.ROLLOUT_USER_PROMPT.format(topic=question)

    # 3) 本地 Ollama 聊天模型
    chat_model = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen3:4b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.3,
    )

    # 4) 构建 ReAct Agent（仅使用 MCP 工具，不再注入任何自定义工具）
    agent = create_react_agent(chat_model, tools=lc_tools)

    # 5) 推理
    res = await agent.ainvoke(
        {
            "messages": [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_msg),
            ]
        },
        config={
            "configurable": {"thread_id": str(uuid.uuid4())},
            "recursion_limit": 16,
        },
    )

    print("====== 推理返回（含工具轨迹） ======")
    print(res)

    # 6) 提取并打印最终答案（与 rl_train/model_test.py 一致的鲁棒逻辑）
    print("====== 最终答案（assistant 消息） ======")
    final_text: Optional[str] = None
    try:
        msgs = res.get("messages", []) if isinstance(res, dict) else []
        if msgs:
            for m in reversed(msgs):
                if getattr(m, "type", "") == "ai" or getattr(m, "role", "") == "assistant":
                    final_text = getattr(m, "content", None)
                    if final_text:
                        break
        if not final_text and isinstance(res, dict):
            final_text = res.get("output_text") or res.get("final_answer")
    except Exception:
        pass

    if final_text:
        print(final_text)

    print("[EVAL] local model + MCP tools test finished.")


async def main():
    # 从环境读取问题，保持与训练脚本一致的语义
    question = (
        os.getenv("QUESTION")
        or os.getenv("TEST_QUESTION")
        or "现在的日期与时间分别是多少？"
    )
    await run_agent_eval(question)


if __name__ == "__main__":
    asyncio.run(main())
