#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
评估一个经过微调的函数调用模型（兼容 Qwen3，支持 LoRA），
工具由 MCP 服务器动态发现并执行。

支持两种推理引擎：
1) Unsloth 运行时（默认）：可加载完整模型，或在基础模型上加载 LoRA 适配器
2) vLLM 运行时（可选）：需要合并后的完整模型（不能直接使用原始 LoRA 目录）

与原始版本相比的变化：
- ❗工具通过 JSON 配置（默认: a2a_agent/mcp_config.json）中定义的 MCP 服务器加载，
  并通过调用对应 MCP 服务器工具来执行。
- 🧭 如果多个服务器暴露了相同的工具名，将使用第一个发现的（会打印警告）。
- 🛡️ 调用工具时的错误会被捕获，并在第二轮推理中反馈给模型。

使用示例：
python inference_tool_sft.py \
  --model ./lora_model \
  --base_model unsloth/Qwen3-4B-Instruct-2507 \
  --engine unsloth \
  --query "今天的日期是？" \
  --chat_template qwen-3 \
  --load_in_4bit \
  --mcp_config a2a_agent/mcp_config.json

使用 vLLM（合并模型）示例：
python inference_tool_sft.py --model your-hf/merged_model_16bit --engine vllm \
  --query "北京现在天气如何？把 23 摄氏度转为华氏度" \
  --mcp_config a2a_agent/mcp_config.json
"""

from __future__ import annotations
import os
import re
import json
import argparse
import hashlib
import random
from typing import Any, Dict, List, Tuple
from datetime import datetime

import torch
from unsloth import FastModel
from transformers import AutoTokenizer, TextStreamer
from peft import PeftModel
from unsloth.chat_templates import get_chat_template as _get_chat_template
from vllm import LLM
from vllm.sampling_params import SamplingParams

# NEW: MCP imports
import asyncio
from fastmcp import Client  # pip install fastmcp
from rl_train.mcp_client import tool_definition_to_dict  # reuse existing util

# =========================
# Utility
# =========================

def parse_bool_env(name: str, default: bool = False) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes", "y", "on"}


# =========================
# Robust JSON parsing for function calls
# =========================

def parse_function_calls(text: str):
    """Extract a JSON list/object from text.
    - Accepts raw JSON, or fenced code blocks (```json ... ``` / ``` ... ```)
    - Prefers first JSON array; falls back to first JSON object
    Returns a Python object or None.
    """
    if not isinstance(text, str):
        return None

    t = text.strip()
    # Remove surrounding code fences if present
    if t.startswith("```") and t.endswith("```"):
        inner = t.strip("`")
        # remove optional language tag at the start
        inner = re.sub(r"^(json|jsonc|javascript|js|txt)\s+", "", inner, flags=re.IGNORECASE)
        t = inner

    # Try direct JSON first
    try:
        return json.loads(t)
    except Exception:
        pass

    # Find first JSON array
    m = re.search(r"\[(?:.|\s)*\]", t)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass

    # Find first JSON object
    m = re.search(r"\{(?:.|\s)*\}", t)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass

    return None


# =========================
# MCP: discovery + execution
# =========================

class MCPRegistry:
    """Holds discovered MCP tools (JSON Schemas) and a name->server map."""

    def __init__(self):
        self.tools_schema: List[Dict[str, Any]] = []
        self.name_to_server: Dict[str, str] = {}

    def tools_schema_json(self) -> str:
        return json.dumps(self.tools_schema, ensure_ascii=False, indent=2)

    def find_server(self, tool_name: str) -> str | None:
        return self.name_to_server.get(tool_name)


async def discover_mcp_tools(config_path: str) -> MCPRegistry:
    """Read MCP servers from config and list their tools.

    Config schema expected (subset):
    {
      "mcpServers": {
        "server_key": {"url": "http://localhost:10001", "disabled": false},
        ...
      }
    }
    """
    registry = MCPRegistry()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            mcp_config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"MCP配置文件不存在: {config_path}")

    mcp_servers = (mcp_config or {}).get("mcpServers", {})
    if not mcp_servers:
        return registry

    for server_name, server_info in mcp_servers.items():
        if server_info.get("disabled"):
            continue
        url = server_info.get("url")
        if not url:
            continue

        try:
            client = Client(url)
            async with client:
                tools = await client.list_tools()
        except Exception as e:
            print(f"⚠️  无法从 '{server_name}' ({url}) 获取工具: {e}")
            continue

        for t in tools:
            try:
                d = tool_definition_to_dict(t)  # {name, description, parameters}
            except Exception:
                # Fallback minimal shape
                d = {"name": getattr(t, "name", ""), "description": getattr(t, "description", None)}

            name = d.get("name")
            if not name:
                continue

            if name in registry.name_to_server:
                # Prefer the first one, but warn once
                # (you can change policy here if needed)
                print(f"⚠️  工具名冲突: '{name}' 在多个服务器中发现，仍将使用先发现的服务器 {registry.name_to_server[name]}")
            else:
                registry.name_to_server[name] = url

            # Ensure JSON-Schema-like shape
            if "parameters" not in d or d["parameters"] is None:
                d["parameters"] = {"type": "object", "properties": {}, "required": []}

            registry.tools_schema.append(d)

    return registry


async def mcp_call_tool(server_url: str, tool_name: str, arguments: Dict[str, Any] | None) -> Any:
    """Call a tool on a given MCP server and return a JSON-serializable result."""
    arguments = arguments or {}
    client = Client(server_url)
    try:
        async with client:
            try:
                result = await client.call_tool(tool_name, arguments)
            except AttributeError:
                # Older fastmcp versions may use `call` as the method name
                result = await client.call(tool_name, arguments)
    except Exception as e:
        return {"error": f"调用工具失败: {e}"}

    # Normalize to JSON-serializable
    def _normalize(x: Any) -> Any:
        try:
            if hasattr(x, "model_dump"):
                x = x.model_dump()
        except Exception:
            pass
        try:
            json.dumps(x, ensure_ascii=False)
            return x
        except TypeError:
            return repr(x)

    return _normalize(result)


# =========================
# Loading (Unsloth + LoRA)
# =========================

def _file_exists(d: str, name: str) -> bool:
    return os.path.isfile(os.path.join(d, name))


def _is_lora_dir(path: str) -> bool:
    return _file_exists(path, "adapter_config.json") or _file_exists(path, "adapter_model.safetensors")


def _has_full_model(path: str) -> bool:
    if not _file_exists(path, "config.json"):
        return False
    for fname in [
        "model.safetensors", "model.safetensors.index.json",
        "pytorch_model.bin", "pytorch_model.bin.index.json",
    ]:
        if _file_exists(path, fname):
            return True
    return False


def _load_tokenizer(model_dir: str, base_model: str | None, chat_template: str | None):
    tok_dir = model_dir if (_file_exists(model_dir, "tokenizer.json") or _file_exists(model_dir, "tokenizer_config.json")) else (base_model or model_dir)
    tokenizer = AutoTokenizer.from_pretrained(tok_dir, use_fast=True)
    # Optionally force a chat template (e.g., qwen_1_5)
    if chat_template:
        tokenizer = _get_chat_template(tokenizer, chat_template=chat_template)
    return tokenizer


def _ensure_pad_token(tokenizer):
    if getattr(tokenizer, "pad_token_id", None) is None:
        tokenizer.pad_token = tokenizer.eos_token


def _load_model_unsloth(model_path: str, base_model: str | None, max_seq_length: int, load_in_4bit: bool, load_in_8bit: bool):
    if _is_lora_dir(model_path):
        if not base_model:
            raise ValueError("--model points to a LoRA adapter directory; please provide --base_model.")
        base, _ = FastModel.from_pretrained(
            model_name=base_model,
            max_seq_length=max_seq_length,
            load_in_4bit=load_in_4bit,
            load_in_8bit=load_in_8bit,
            full_finetuning=False,
            token=None,
        )
        model = PeftModel.from_pretrained(base, model_path)
    elif _has_full_model(model_path):
        model, _ = FastModel.from_pretrained(
            model_name=model_path,
            max_seq_length=max_seq_length,
            load_in_4bit=load_in_4bit,
            load_in_8bit=load_in_8bit,
            full_finetuning=False,
            token=None,
        )
    else:
        raise ValueError(f"Cannot recognize {model_path} as a full model or a LoRA adapter directory.")

    try:
        model.eval()
    except Exception:
        pass

    # Move to CUDA if available
    if torch is not None and torch.cuda.is_available():
        try:
            model.to("cuda")
        except Exception:
            pass
    return model


# =========================
# Inference passes (now parameterized by MCP tools)
# =========================

def _apply_template(tokenizer, messages: List[Dict[str, str]], add_generation_prompt: bool = True, tokenize: bool = True):
    return tokenizer.apply_chat_template(
        messages,
        tokenize=tokenize,
        add_generation_prompt=add_generation_prompt,
        return_tensors="pt" if tokenize else None,
    )


def _first_pass_system_prompt(tools_json: str) -> str:
    if tools_json.strip() == "[]":
        # No tools — still ask for JSON, but make it clear there are none
        return (
            "当前没有可用的工具。\n"
            "如果需要，请直接回答；若你仍要调用工具，请输出空列表 []。"
        )
    return (
        "你可以调用下列工具（以 JSON Schema 描述）。\n"
        "请先输出一段仅包含 JSON 的内容，格式为一个列表，每个元素是：\n"
        '{"name": "<函数名>", "arguments": {<参数>}}\n'
        "不要输出解释文字或额外内容。\n"
        "工具列表如下：\n" + tools_json
    )


def first_pass_generate_unsloth(model, tokenizer, query: str, max_new_tokens: int, tools_json: str) -> str:
    sys_prompt = _first_pass_system_prompt(tools_json)
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": query},
    ]

    prompt_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt_text, return_tensors="pt")
    if hasattr(model, "device"):
        try:
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
        except Exception:
            pass

    gen_kwargs = dict(max_new_tokens=max_new_tokens, use_cache=True, pad_token_id=tokenizer.eos_token_id)
    out = model.generate(**inputs, **gen_kwargs)
    decoded = tokenizer.decode(out[0], skip_special_tokens=False)
    return decoded[len(prompt_text):]


def second_pass_generate_unsloth(model, tokenizer, query: str, tool_results: List[Dict[str, Any]], max_new_tokens: int):
    synthesis_system = (
        "你是一个严谨的助理。请仅基于提供的工具结果，给出中文答案，包含关键数值与单位。"
    )
    synthesis_user = (
        f"用户提问：{query}\n\n"
        f"工具调用与返回：\n{json.dumps(tool_results, ensure_ascii=False, indent=2)}\n\n"
        "请给出最终回答。"
    )
    messages = [
        {"role": "system", "content": synthesis_system},
        {"role": "user", "content": synthesis_user},
    ]

    prompt_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt_text, return_tensors="pt")
    if hasattr(model, "device"):
        try:
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
        except Exception:
            pass

    streamer = TextStreamer(tokenizer, skip_prompt=True)
    gen_kwargs = dict(max_new_tokens=max_new_tokens, use_cache=True, pad_token_id=tokenizer.eos_token_id)
    _ = model.generate(**inputs, streamer=streamer, **gen_kwargs)


# vLLM versions

def _ensure_tokenizer_for_prompt_only(chat_template: str | None, model_or_repo: str):
    # We only need tokenizer for producing a textual chat-formatted prompt
    tok = AutoTokenizer.from_pretrained(model_or_repo, use_fast=True)
    if chat_template:
        tok = _get_chat_template(tok, chat_template=chat_template)
    return tok


def _vllm_generate_text(llm: LLM, text_prompt: str, max_tokens: int) -> str:
    sp = SamplingParams(max_tokens=max_tokens)
    outputs = llm.generate([text_prompt], sp)
    return outputs[0].outputs[0].text


def first_pass_generate_vllm(model_repo: str, query: str, max_tokens: int, chat_template: str | None, tools_json: str) -> str:
    tok = _ensure_tokenizer_for_prompt_only(chat_template, model_repo)

    sys_prompt = _first_pass_system_prompt(tools_json)
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": query},
    ]
    text_prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    llm = LLM(model=model_repo, max_model_len=2048, tokenizer_mode="auto", tensor_parallel_size=1)
    return _vllm_generate_text(llm, text_prompt, max_tokens)


def second_pass_generate_vllm(model_repo: str, query: str, tool_results: List[Dict[str, Any]], max_tokens: int, chat_template: str | None) -> str:
    tok = _ensure_tokenizer_for_prompt_only(chat_template, model_repo)

    synthesis_system = (
        "你是一个严谨的助理。请仅基于提供的工具结果，给出中文答案，包含关键数值与单位。"
    )
    synthesis_user = (
        f"用户提问：{query}\n\n"
        f"工具调用与返回：\n{json.dumps(tool_results, ensure_ascii=False, indent=2)}\n\n"
        "请给出最终回答。"
    )
    messages = [
        {"role": "system", "content": synthesis_system},
        {"role": "user", "content": synthesis_user},
    ]
    text_prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    llm = LLM(model=model_repo, max_model_len=2048, tokenizer_mode="auto", tensor_parallel_size=1)
    return _vllm_generate_text(llm, text_prompt, max_tokens)


# =========================
# Orchestration
# =========================

def run_unsloth(args):
    # 1) Discover MCP tools
    registry = asyncio.run(discover_mcp_tools(args.mcp_config))
    print(f"🔧 通过 MCP 发现 {len(registry.tools_schema)} 个工具。")

    # 2) Load model/tokenizer
    tokenizer = _load_tokenizer(args.model, args.base_model, args.chat_template)
    _ensure_pad_token(tokenizer)
    model = _load_model_unsloth(
        model_path=args.model,
        base_model=args.base_model,
        max_seq_length=2048,
        load_in_4bit=args.load_in_4bit,
        load_in_8bit=args.load_in_8bit,
    )

    # 3) Pass 1: ask for function calls
    tools_json = registry.tools_schema_json() if registry.tools_schema else "[]"
    first = first_pass_generate_unsloth(model, tokenizer, args.query, args.max_new_tokens, tools_json)
    print("=== Raw function-call block ===\n", first)
    calls = parse_function_calls(first)
    print("=== Parsed function calls ===\n", calls)

    if not calls:
        print("未检测到函数调用 JSON，直接输出：\n" + first)
        return

    # 4) Execute tools via MCP
    items = calls if isinstance(calls, list) else [calls]
    tool_results = []
    for item in items:
        name = (item or {}).get("name")
        args_ = (item or {}).get("arguments") or {}
        if not name:
            res = {"error": "Missing 'name' in function call"}
        else:
            server_url = registry.find_server(name)
            if not server_url:
                res = {"error": f"Unknown tool: {name}"}
            else:
                res = asyncio.run(mcp_call_tool(server_url, name, args_))
        print(f"[Tool:{name}] -> {res}")
        tool_results.append({"name": name, "arguments": args_, "result": res})

    # 5) Pass 2: synthesis
    second_pass_generate_unsloth(model, tokenizer, args.query, tool_results, max_new_tokens=min(512, args.max_new_tokens))


def run_vllm(args):
    # 1) Discover MCP tools
    registry = asyncio.run(discover_mcp_tools(args.mcp_config))
    print(f"🔧 通过 MCP 发现 {len(registry.tools_schema)} 个工具。")

    # 2) vLLM requires merged model
    if _is_lora_dir(args.model):
        raise ValueError("vLLM 不支持直接加载 LoRA 适配器目录；请先 merge 得到完整权重后再用 --engine vllm")

    # 3) Pass 1
    tools_json = registry.tools_schema_json() if registry.tools_schema else "[]"
    text1 = first_pass_generate_vllm(args.model, args.query, max_tokens=min(768, args.max_new_tokens), chat_template=args.chat_template, tools_json=tools_json)
    print("=== vLLM raw output (function calls) ===\n", repr(text1))
    calls = parse_function_calls(text1)
    print("=== Parsed function calls ===\n", calls)

    if not calls:
        print("未检测到函数调用 JSON，直接输出：\n" + text1)
        return

    # 4) Execute tools via MCP
    items = calls if isinstance(calls, list) else [calls]
    tool_results = []
    for item in items:
        name = (item or {}).get("name")
        args_ = (item or {}).get("arguments") or {}
        if not name:
            res = {"error": "Missing 'name' in function call"}
        else:
            server_url = registry.find_server(name)
            if not server_url:
                res = {"error": f"Unknown tool: {name}"}
            else:
                res = asyncio.run(mcp_call_tool(server_url, name, args_))
        print(f"[Tool:{name}] -> {res}")
        tool_results.append({"name": name, "arguments": args_, "result": res})

    # 5) Pass 2
    text2 = second_pass_generate_vllm(args.model, args.query, tool_results, max_tokens=min(512, args.max_new_tokens), chat_template=args.chat_template)
    print("=== vLLM final answer ===\n", text2)


# =========================
# CLI
# =========================

def main():
    ap = argparse.ArgumentParser(description="使用 MCP 工具评估一个支持函数调用的微调模型（Qwen3/Unsloth/LoRA）。首先启动MCP服务器")
    ap.add_argument("--model", required=True, help="模型路径（完整模型目录、LoRA 适配器目录，或 HuggingFace 仓库名）。")
    ap.add_argument("--base_model", default=None,
                    help="当 --model 是 LoRA 目录时需指定基础模型（如 unsloth/Qwen3-4B-Instruct-2507）")
    ap.add_argument("--engine", choices=["unsloth", "vllm"], default="unsloth",
                    help="推理引擎，默认为 unsloth，可选 vllm")
    ap.add_argument("--query", default="旧金山的天气如何？", help="输入查询文本")
    ap.add_argument("--max_new_tokens", type=int, default=1024, help="最大生成 token 数")
    ap.add_argument("--chat_template", default=None, help="强制指定 chat 模板（如 qwen_1_5）。若不指定则使用默认。")
    ap.add_argument("--load_in_4bit", action="store_true", default=False, help="是否以 4bit 加载模型")
    ap.add_argument("--load_in_8bit", action="store_true", default=False,
                    help="是否以 8bit 加载模型（若同时指定 4bit 和 8bit，将优先使用 4bit）")
    ap.add_argument("--mcp_config", default="a2a_agent/mcp_config.json", help="MCP 服务器配置文件路径（JSON 格式）")
    args = ap.parse_args()

    # Boolean adjust: if both are set, prioritize 4bit
    if args.load_in_4bit and args.load_in_8bit:
        args.load_in_8bit = False

    if args.engine == "unsloth":
        run_unsloth(args)
    else:
        run_vllm(args)


if __name__ == "__main__":
    main()
