#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/9/12 15:40
# @File  : generate_topic.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  :  生成一些questions问题
"""
----------
1) Install
   pip install openai-agents pydantic

2) Run
   读取MCP的server端，根据可以使用的工具，调用大模型，生成一些问题，这些问题可以使用这些工具解决
   python generate_questions.py -n 20 -f mcpserver/energy_services.py -o questions.txt --lang zh
"""
from __future__ import annotations

import argparse
import json
import sys
import dotenv
from pathlib import Path
from typing import List, Set
from pydantic import BaseModel, Field
from agents import Agent, Runner
dotenv.load_dotenv()

# ---------- Structured output schema ----------
class QuestionsOutput(BaseModel):
    """Structured output for the agent."""
    questions: List[str] = Field(
        description="List of natural-language questions in the requested language; each question should be solvable by one or more of the provided tools."
    )


# ---------- Agent factory ----------
def build_agent(language: str, server_source: str) -> Agent:
    lang_prompt = {"zh": "中文", "en": "English"}.get(language, language)

    instructions = f"""
你是“工具感知的问题生成器”。
下面是一个 MCP server 的完整 Python 源码，其中包含若干工具函数（通过 @mcp.tool 定义）：

-------------------- 源码开始 --------------------
{server_source}
-------------------- 源码结束 --------------------

任务：基于以上源码，生成 N 个自然语言问题，这些问题都应该可以通过调用文件中定义的工具来解答。
要求：
- 输出语言：{lang_prompt}。
- 每个问题要具体、可操作，不要笼统模糊。
- 问题必须是用户可能真实会问的，而不是直接问“调用哪个函数”。
- 每个问题一行，不要编号，不要解释。
- 输出时严格遵循 structured outputs（只返回 questions 列表）。
"""

    return Agent(
        name="ToolQuestionAgent",
        instructions=instructions.strip(),
        output_type=QuestionsOutput,
        model="gpt-4.1",
    )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate tool-solvable questions from MCP server source file.")
    parser.add_argument("-n", "--num", type=int, default=20)
    parser.add_argument("-f", "--file", type=Path, required=True)
    parser.add_argument("-o", "--out", type=Path, default=Path("questions.txt"))
    parser.add_argument("--lang", choices=["zh","en"], default="zh")

    args = parser.parse_args(argv)

    # 1. 读取 server 文件源码
    if not args.file.exists():
        parser.error(f"--file not found: {args.file}")
    server_source = args.file.read_text(encoding="utf-8")

    # 2. 构建 Agent
    agent = build_agent(args.lang, server_source)

    # 3. 调用大模型生成问题
    prompt = f"请生成 {args.num} 个问题。"
    result = Runner.run_sync(agent, prompt)
    questions = result.final_output.questions  # type: ignore[attr-defined]

    # 4. 输出
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.suffix.lower() == ".txt":
        args.out.write_text("\n".join(questions), encoding="utf-8")
    else:
        payload = {"language": args.lang, "count": len(questions), "questions": questions}
        args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ Wrote {len(questions)} questions to: {args.out}")

if __name__ == "__main__":
    raise SystemExit(main())
