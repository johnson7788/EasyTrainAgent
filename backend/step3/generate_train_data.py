import argparse
import logging
from typing import Any, Dict, List
from uuid import uuid4
import json
import os

import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import AgentCard, MessageSendParams, SendStreamingMessageRequest
from mcp_client import get_mcp_tools


PUBLIC_AGENT_CARD_PATH = "/.well-known/agent.json"
EXTENDED_AGENT_CARD_PATH = "/agent/authenticatedExtendedCard"


def _normalize_tool(tool: Dict[str, Any]) -> Dict[str, Any]:
    """
    将 MCP 返回的工具规格规范化为：
    {"type": "function", "function": {...}}
    如果原本已经是该结构，则直接返回。
    """
    if tool is None:
        return tool
    if isinstance(tool, dict) and "type" in tool and tool.get("type") == "function" and "function" in tool:
        return tool

    # 常见的扁平结构：{"name": "...", "description": "...", "parameters": {...}}
    if isinstance(tool, dict) and {"name", "description"} & set(tool.keys()):
        fn = {
            "name": tool.get("name"),
            "description": tool.get("description", ""),
            "parameters": tool.get("parameters") or {
                "type": "object",
                "properties": {},
            },
        }
        return {"type": "function", "function": fn}

    # 兜底：包一层放到 function 字段里
    return {"type": "function", "function": tool}


async def get_agent_response(client: A2AClient, question: str) -> List[Dict[str, Any]]:
    """
    发送问题给 Agent，返回按要求的新 messages 序列：
    [{"role":"user"}, {"role":"tool_call"}, {"role":"tool_response"}, {"role":"assistant"}, ...]
    """
    messages: List[Dict[str, str]] = []
    # 首条 user
    messages.append({"role": "user", "content": question})

    # 准备并发起流式请求
    parts = [{"kind": "text", "text": question}]
    multiturn_first: Dict[str, Any] = {
        "message": {
            "role": "user",
            "parts": parts,
            "messageId": uuid4().hex,
            "metadata": {"language": "English", "user_id": 123456},
        },
    }
    streaming_request = SendStreamingMessageRequest(
        id=str(uuid4()), params=MessageSendParams(**multiturn_first)
    )
    stream_response = client.send_message_streaming(streaming_request)

    # 聚合 agent 的自然语言响应（可能多段）
    text_buffer = ""

    async for chunk in stream_response:
        chunk_data = chunk.model_dump(mode="json", exclude_none=True)

        result = chunk_data.get("result")
        if not result or result.get("kind") != "status-update":
            continue

        status = result.get("status")
        if not status:
            continue

        message = status.get("message")
        if not message:
            continue

        parts = message.get("parts")
        if not parts:
            continue

        for part in parts:
            kind = part.get("kind")
            if kind == "data":
                data1 = part.get("data")
                if data1 and data1.get("data"):
                    for item in data1.get("data"):
                        # 工具调用（function call）
                        if item and item.get("type") == "function":
                            function_call = item.get("function") or {}
                            # 只保留 name + arguments 字段，JSON 字符串写进 content
                            tool_call_payload = {
                                "name": function_call.get("name"),
                                "arguments": function_call.get("arguments", {}),
                            }
                            messages.append(
                                {
                                    "role": "tool_call",
                                    "content": json.dumps(tool_call_payload, ensure_ascii=False),
                                }
                            )

                        # 工具返回（observation / tool_output）
                        if item and item.get("tool_output") is not None:
                            tool_output = item.get("tool_output")
                            # 确保 content 是 JSON 字符串
                            content_str: str
                            try:
                                parsed = json.loads(tool_output)
                                # 已是 JSON 字符串
                                if isinstance(parsed, (dict, list, str, int, float, bool)) or parsed is None:
                                    content_str = tool_output if isinstance(tool_output, str) else json.dumps(parsed, ensure_ascii=False)
                                else:
                                    content_str = json.dumps({"result": parsed}, ensure_ascii=False)
                            except (json.JSONDecodeError, TypeError):
                                content_str = json.dumps({"result": tool_output}, ensure_ascii=False)

                            messages.append({"role": "tool_response", "content": content_str})

            elif kind == "text":
                text = part.get("text")
                if text:
                    text_buffer += text

    # 将累计的自然语言响应写入 assistant
    if text_buffer.strip():
        messages.append({"role": "assistant", "content": text_buffer.strip()})

    return messages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="从问题文件逐条提问 Agent，收集对话与工具信息，写入 JSONL（符合 messages + tools 字段格式）。"
    )
    parser.add_argument(
        "-q",
        "--questions-file",
        default="./questions.txt",
        help="输入问题文件路径（每行一个问题）。默认：./questions.txt",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        default="train.jsonl",
        help="输出 JSONL 文件路径。默认：train.jsonl",
    )
    parser.add_argument(
        "--mcp-config",
        default="./mcp_config.json",
        help="MCP 配置文件路径。默认：./mcp_config.json",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("A2A_BASE_URL", "http://localhost:10066"),
        help="Agent 服务 Base URL。可用环境变量 A2A_BASE_URL 覆盖。默认：http://localhost:10066",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # 读取 MCP 配置
    try:
        with open(args.mcp_config, "r", encoding="utf-8") as f:
            mcp_config = json.load(f)
    except FileNotFoundError:
        logger.error(f"MCP 配置文件不存在，请检查 {args.mcp_config}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"MCP 配置文件不是合法 JSON：{e}")
        return

    mcp_servers = mcp_config.get("mcpServers", {})
    all_tools_raw: List[Dict[str, Any]] = []
    for server_name, server_info in mcp_servers.items():
        if not server_info.get("disabled"):
            url = server_info.get("url")
            if url:
                logger.info(f"Fetching tools from '{server_name}' at {url}...")
                server_tools = await get_mcp_tools(url)
                if isinstance(server_tools, list):
                    all_tools_raw.extend(server_tools)

    logger.info(f"发现 {len(all_tools_raw)} 个工具通过读取 MCP 的 Server 端")

    # 规范化工具，并转为 JSON 字符串（符合你的目标格式要求）
    normalized_tools = [_normalize_tool(t) for t in all_tools_raw]
    tools_as_string = json.dumps(normalized_tools, ensure_ascii=False)

    # 校验输入问题文件
    if not os.path.exists(args.questions_file):
        logger.error(f"问题文件不存在：{args.questions_file}")
        return

    async with httpx.AsyncClient(timeout=60) as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=args.base_url)
        final_agent_card_to_use: AgentCard | None = None

        try:
            logger.info(f"尝试获取 Agent 配置信息: {args.base_url}{PUBLIC_AGENT_CARD_PATH}")
            _public_card = await resolver.get_agent_card()
            final_agent_card_to_use = _public_card

            if _public_card.supportsAuthenticatedExtendedCard:
                try:
                    auth_headers_dict = {"Authorization": "Bearer dummy-token-for-extended-card"}
                    _extended_card = await resolver.get_agent_card(
                        relative_card_path=EXTENDED_AGENT_CARD_PATH,
                        http_kwargs={"headers": auth_headers_dict},
                    )
                    final_agent_card_to_use = _extended_card
                except Exception as e_extended:
                    logger.warning(f"Failed to get extended card: {e_extended}", exc_info=True)
        except Exception as e:
            logger.error(f"Failed to get AgentCard: {e}", exc_info=True)
            raise RuntimeError("Cannot get agent card, cannot continue.") from e

        client = A2AClient(httpx_client=httpx_client, agent_card=final_agent_card_to_use)
        logger.info("A2AClient 初始化完成.")

        # 读取问题并生成训练数据（每行一个样本）
        with open(args.questions_file, "r", encoding="utf-8") as f_in, open(
            args.output_file, "w", encoding="utf-8"
        ) as f_out:
            questions = [line.strip() for line in f_in if line.strip()]
            if not questions:
                logger.warning("问题文件为空，没有可处理的问题。")

            for question in questions:
                logger.info(f"Processing question: {question}")
                messages = await get_agent_response(client, question)

                # >>> 写入符合指定格式的 JSON 行
                # tools 字段是 JSON 字符串；messages 是数组
                training_entry = {
                    "tools": tools_as_string,
                    "messages": messages,
                }
                print(f"问题的输出结果是: {training_entry}")
                f_out.write(json.dumps(training_entry, ensure_ascii=False) + "\n")
                logger.info(f"处理完成问题并保存: {question}")

        logger.info(f"成功保存SFT训练数据到目录中: {args.output_file}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
