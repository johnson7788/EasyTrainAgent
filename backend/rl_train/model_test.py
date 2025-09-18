#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/8/27 11:41
# @File  : model_test.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 基于 LangGraph + ART 的 QueryAgent 测试脚本（工具从 MCP 服务器发现并调用）

import os
import uuid
import asyncio
from typing import Optional, List

import dotenv
import art
import prompt
from art.langgraph import init_chat_model, wrap_rollout
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage

# === MCP: 与训练/推理保持一致 ===
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp_config_load import load_mcp_servers

dotenv.load_dotenv()

# ---------- 与训练保持一致 ----------
NAME = os.getenv("ART_NAME", "query-agent")
MODEL_NAME = os.getenv("ART_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
PROJECT_NAME = os.getenv("ART_PROJECT", "content-training")
USE_LOCAL_BACKEND = os.getenv("ART_BACKEND", "local").lower() == "local"
MCP_CONFIG = os.getenv("MCP_CONFIG", "mcp_config.json")

async def run_agent_test(model: art.Model, question: str):
    """
    基于训练好的同名模型，使用 MCP 工具对问题进行 ReAct 推理并返回答案。
    """
    # === 发现 MCP 工具 ===
    if not os.path.exists(MCP_CONFIG):
        raise FileNotFoundError(f"MCP 配置文件不存在: {MCP_CONFIG}")
    mcp_servers = load_mcp_servers(MCP_CONFIG)
    mcp_client = MultiServerMCPClient(mcp_servers)
    lc_tools = await mcp_client.get_tools()

    if not lc_tools:
        raise RuntimeError("未从 MCP 发现任何可用工具，请先启动 MCP 服务器并检查配置。")

    # 提示词：注入已发现的工具名（与训练一致）
    tool_names_for_prompt: List[str] = [getattr(t, "name", str(t)) for t in lc_tools]
    tools_json_note = f"已发现 MCP 工具：{tool_names_for_prompt}（按各自 JSON Schema 传参）"
    system_prompt = prompt.ROLLOUT_SYSTEM_PROMPT.format(tools_json_note=tools_json_note)
    user_msg = prompt.ROLLOUT_USER_PROMPT.format(question=question)

    # 用 ART 的 init_chat_model 获取可用的聊天模型（后端会加载最近训练好的 LoRA）
    chat_model = init_chat_model(model, temperature=0.3)
    agent = create_react_agent(chat_model, tools=lc_tools)

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
    print("====== 最终答案（assistant 消息） ======")
    try:
        # langgraph 返回字典时常见结构：{"messages": [...]} 或含 "output_text"
        msgs = res.get("messages", []) if isinstance(res, dict) else []
        final_text: Optional[str] = None
        if msgs:
            # 最后一条 assistant
            for m in reversed(msgs):
                if getattr(m, "type", "") == "ai" or getattr(m, "role", "") == "assistant":
                    final_text = getattr(m, "content", None)
                    if final_text:
                        break
        if not final_text and isinstance(res, dict):
            final_text = res.get("output_text") or res.get("final_answer")
        if final_text:
            print(final_text)
    except Exception:
        pass

    print("[TEST] agent finished. See backend logs / tracing for details.")

async def main():
    # 连接与注册后端
    if USE_LOCAL_BACKEND:
        from art.local.backend import LocalBackend
        backend = LocalBackend()
    else:
        from art.skypilot.backend import SkyPilotBackend
        backend = await SkyPilotBackend.initialize_cluster(
            cluster_name=os.getenv("ART_SKYPILOT_CLUSTER", "art-cluster"),
            gpu=os.getenv("ART_GPU", "A100"),
        )

    model = art.TrainableModel(name=NAME, project=PROJECT_NAME, base_model=MODEL_NAME)
    await model.register(backend)

    # 与 QueryAgent 语义一致：从 env 读取问题
    question = (
        os.getenv("QUESTION")
        or os.getenv("TEST_QUESTION")
        or "现在的日期与时间分别是多少？"
    )

    # 用 wrap_rollout 包装，确保 ART 上下文正确设置
    wrapped_test_func = wrap_rollout(model, run_agent_test)
    await wrapped_test_func(model, question)

if __name__ == "__main__":
    asyncio.run(main())
