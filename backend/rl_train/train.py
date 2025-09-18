#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/8/27
# @File  : train_query_agent.py
# @Author: johnson
# @Desc  : 训练一个“查询”ReAct Agent（ART + LangGraph，GRPO），从 questions.txt 读取问题
#          工具：检索/计算等来自 MCP 服务器；return_final_answer_tool 使用本地工具以便训练阶段读取 final_answer。

import logging
logging.basicConfig(level=logging.INFO)
import os
import json
import uuid
import time
import asyncio
import dotenv
import wandb
from dataclasses import dataclass
from textwrap import dedent
from typing import List, Dict, Any, Optional

import art
from art.langgraph import init_chat_model, wrap_rollout
from art.utils import iterate_dataset
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import Tool, tool
from pydantic import BaseModel, ValidationError
import prompt
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp_config_load import load_mcp_servers
from transformers import AutoTokenizer
from my_ruler import ruler_score_group
dotenv.load_dotenv()

# ---------------- 运行配置 ----------------
NAME = os.getenv("ART_NAME", "query-agent")
MODEL_NAME = os.getenv("ART_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
PROJECT_NAME = os.getenv("ART_PROJECT", "content-training")
USE_LOCAL_BACKEND = os.getenv("ART_BACKEND", "local").lower() == "local"

WANDB_PROJECT = os.getenv("WANDB_PROJECT", PROJECT_NAME)
WANDB_ENTITY = os.getenv("WANDB_ENTITY")  # 可空
WANDB_RUN_NAME = os.getenv("WANDB_RUN_NAME", f"{NAME}-{time.strftime('%Y%m%d-%H%M%S')}")
MCP_CONFIG = os.getenv("MCP_CONFIG", "mcp_config.json")
USE_RULER = os.getenv("USE_RULER", "true").lower() == "true"
MAX_SEQ_LEN = int(os.getenv("MAX_SEQ_LEN", 4096))
# RULER 评估模型（可选；需相应 API Key）
RULER_MODEL = os.getenv("RULER_MODEL", "openai/o4-mini")
RULER_API_KEY = os.getenv("RULER_API_KEY")
RULER_API_BASE = os.getenv("RULER_API_BASE")
WANDB_BASE_URL = os.getenv("WANDB_BASE_URL", "N/A")


print(f"项目名称: {NAME} - {MODEL_NAME} - {PROJECT_NAME} - WANDB: {WANDB_BASE_URL} - 很关键的USE_RULER: {USE_RULER}")
print(f"训练时传入的最大序列长度: {MAX_SEQ_LEN}")
print(f"使用MCP的配置文件: {MCP_CONFIG}")


tok = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

# --- 用于裁剪Context，当长度比较长的时候
def _msg_text(m):
    """将各种消息对象（dict / LangChain Message / OpenAI Choice / 其它）统一成 'role: content' 文本。"""
    # 1) dict 消息：用 dict.get
    if isinstance(m, dict):
        role = m.get("role", "") or m.get("type", "")
        content = m.get("content", "") or ""
        return f"{role or 'msg'}: {content}"

    # 2) OpenAI ChatCompletion Choice（或类似对象）：有 message 且 message.content
    #    采用鸭子类型判断，避免显式依赖 openai 的类型
    if hasattr(m, "message") and hasattr(getattr(m, "message"), "content"):
        role = "assistant"
        content = getattr(getattr(m, "message"), "content", "") or ""
        return f"{role}: {content}"

    # 3) 其它（如 LangChain 的 HumanMessage/SystemMessage 等）
    role = getattr(m, "type", None) or getattr(m, "role", "") or ""
    content = getattr(m, "content", "") or ""
    return f"{role or 'msg'}: {content}"

def _tokens_len(text: str) -> int:
    return len(tok(text, add_special_tokens=False, return_attention_mask=False)["input_ids"])

def clip_traj_inplace(traj, max_tokens=MAX_SEQ_LEN):
    # 对rollout的轨迹进行裁剪，保留一定长度即可，裁剪单条轨迹
    if not getattr(traj, "messages_and_choices", None):
        return
    msgs = list(traj.messages_and_choices)
    print(f"裁剪前有信息：{len(msgs)} 条")
    # 永远保留第一个 system（如有）
    keep_head = []
    if msgs and ("system" in _msg_text(msgs[0]).lower()):
        keep_head.append(msgs.pop(0))

    # 从“最近”往回累加，超出则停止
    kept_tail = []
    for m in reversed(msgs):
        candidate = keep_head + list(reversed(kept_tail + [m]))
        text = "\n".join(_msg_text(x) for x in candidate)
        if _tokens_len(text) <= max_tokens:
            kept_tail.append(m)
        else:
            break

    traj.messages_and_choices = keep_head + list(reversed(kept_tail))


# 在 finished / judged 生成之后、train 之前
def clip_group(g, max_tokens=MAX_SEQ_LEN):
    return art.TrajectoryGroup(
        (clip_traj_inplace(t, max_tokens) or t) for t in list(g)
    )

# ----------------- 数据结构 -----------------
class FinalQAResult(BaseModel):
    task: List[Dict[str, Any]]

@dataclass
class QueryScenario:
    id: str
    question: str
    input_task: List[Dict[str, Any]]

class ProjectTrajectory(art.Trajectory):
    final: Optional[FinalQAResult] = None

# =========================
# MCP: 发现与调用
# =========================
def _parse_json_obj_loose(s: Any) -> Optional[Dict[str, Any]]:
    """宽松解析：输入可以是 dict / JSON 字符串 / ```json fenced。"""
    if isinstance(s, dict):
        return s
    if not isinstance(s, str):
        return None
    t = s.strip()
    if t.startswith("```") and t.endswith("```"):
        inner = t.strip("`")
        # 去掉可能的语言标签
        for tag in ("json", "jsonc", "javascript", "js", "txt"):
            if inner.lower().startswith(tag):
                inner = inner[len(tag):].strip()
                break
        t = inner
    try:
        obj = json.loads(t)
        return obj if isinstance(obj, dict) else None
    except Exception:
        import re
        m = re.search(r"\{(?:.|\s)*\}", t)
        if m:
            try:
                obj = json.loads(m.group(0))
                return obj if isinstance(obj, dict) else None
            except Exception:
                return None
    return None

# ----------------- 从文件加载问题 -----------------
def _default_questions_path() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    question_path = os.path.abspath(os.path.join(here, "..", "questions.txt"))
    return question_path

def load_questions(path: Optional[str] = None) -> List[str]:
    qpath = path or os.getenv("QUESTIONS_PATH") or _default_questions_path()
    print(f"开始加载训练问题：{qpath}")
    if not os.path.exists(qpath):
        raise FileNotFoundError(f"questions.txt 未找到：{qpath}")
    questions: List[str] = []
    with open(qpath, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                continue
            questions.append(s)
    if not questions:
        raise ValueError("questions.txt 为空或没有有效问题行。")
    return questions

# ----------------- rollout（核心）：LangGraph + MCP 工具 + 本地 return_final_answer_tool -----------------
async def rollout(model: art.Model, scenario: QueryScenario) -> ProjectTrajectory:
    MAX_TURNS = 16
    traj = ProjectTrajectory(
        reward=0.0,
        messages_and_choices=[],
        metadata={"scenario_id": scenario.id}
    )

    # === 使用 MultiServerMCPClient：与生产一致 ===
    if not os.path.exists(MCP_CONFIG):
        raise FileNotFoundError(f"MCP配置文件不存在: {MCP_CONFIG}")
    mcp_servers = load_mcp_servers(MCP_CONFIG)
    mcp_client = MultiServerMCPClient(mcp_servers)

    # 拿到 LangChain Tool 对象（已带各自的 JSON Schema）
    mcp_tools = await mcp_client.get_tools()

    # 过滤掉服务端的 return_final_answer_tool（训练阶段使用本地版本）
    filtered_mcp_tools = [t for t in mcp_tools if getattr(t, "name", "") != "return_final_answer_tool"]

    # 本地：return_final_answer_tool（用于训练阶段保存最终 JSON）
    final: Optional[FinalQAResult] = None

    @tool
    def return_final_answer_tool(task: List[Dict[str, Any]]) -> dict:
        """返回最终 JSON：保持原格式的 task。"""
        nonlocal final
        try:
            final = FinalQAResult(task=task)
            return final.model_dump()
        except ValidationError as e:
            return {"error": f"ValidationError: {str(e)}"}

    lc_tools: List[Tool] = []
    lc_tools.extend(filtered_mcp_tools)  # 直接使用原生工具对象
    lc_tools.append(return_final_answer_tool)

    if not lc_tools:
        raise RuntimeError("未从 MCP 发现任何可用工具，请先启动 MCP 服务器并检查配置。")

    # ====== 提示词（同步生产：不再宣称只有一个 input 参数）======
    tool_names_for_prompt = [getattr(t, "name", str(t)) for t in filtered_mcp_tools] + ["return_final_answer_tool"]
    tools_json_note = f"已发现 MCP 工具：{tool_names_for_prompt}（按各自 JSON Schema 传参）"

    system_prompt = prompt.ROLLOUT_SYSTEM_PROMPT.format(tools_json_note=tools_json_note)

    chat_model = init_chat_model(model=model.name, temperature=0.8)
    agent = create_react_agent(chat_model, tools=lc_tools)

    # ====== 执行 Agent ======
    user_msg = prompt.ROLLOUT_USER_PROMPT.format(question=scenario.question)

    await agent.ainvoke(
        {"messages": [SystemMessage(content=system_prompt),
                      HumanMessage(content=user_msg)]},
        config={"configurable": {"thread_id": str(uuid.uuid4())},
                "recursion_limit": MAX_TURNS},
    )

    # ====== 计算奖励 ======
    if final:
        traj.final = final

        # 这里可以加一些自定义的奖励
        fr = 1.0  # 这里，有final，就给reward
        # try:
        #     fr = format_reward(scenario.input_task, final.task)
        # except Exception:
        #     fr = 0.0
        traj.reward = fr
        traj.metrics["format_reward"] = fr
    else:
        # 未返回最终 JSON，给最低奖励
        traj.reward = 0.0
        traj.metrics["format_reward"] = 0.0

    return traj

# ---------------- wandb: 日志封装 ----------------
def _log_batch_to_wandb(*, batch, finished_groups, use_ruler: bool):
    print("_log_batch_to_wandb: 记录批次信息到wandb")
    trajectories = []
    for g in finished_groups:
        if hasattr(g, "trajectories"):
            trajectories.extend(getattr(g, "trajectories"))
        else:
            try:
                trajectories.extend(list(g))
            except Exception:
                pass

    table = wandb.Table(columns=["scenario_id", "format_reward", "total_reward"])
    for t in trajectories[:50]:
        sid = (getattr(t, "metadata", {}) or {}).get("scenario_id", "")
        fr = (getattr(t, "metrics", {}) or {}).get("format_reward", 0.0)
        rw = getattr(t, "reward", 0.0)
        table.add_data(sid, fr, rw)

    wandb.log({
        "train/step": batch.step,
        "train/epoch": batch.epoch,
        "ruler/enabled": int(bool(use_ruler)),
        "samples/trajectories": table
    }, step=batch.step)

# ----------------- 构造训练集 -----------------
def build_scenarios_from_questions(questions: List[str]) -> List[QueryScenario]:
    """
    把每一条问题行转换为单元素 task：
    [{"type": "qa", "data": {"question": <q>, "text": ""}}]
    """
    scenarios: List[QueryScenario] = []
    for i, question in enumerate(questions, start=1):
        task = [{"type": "qa", "data": {"question": question, "text": ""}}]
        sid = f"q_{i}"
        scenarios.append(QueryScenario(id=sid, question=question, input_task=task))
    return scenarios

# ----------------- 主训练循环 -----------------
async def main():
    # wandb
    wandb.init(
        project=WANDB_PROJECT,
        entity=WANDB_ENTITY if WANDB_ENTITY else None,
        name=WANDB_RUN_NAME,
        config={
            "art_project": PROJECT_NAME,
            "art_name": NAME,
            "base_model": MODEL_NAME,
            "backend": "local" if USE_LOCAL_BACKEND else "skypilot",
            "ruler_model": RULER_MODEL,
        },
        settings=wandb.Settings(start_method="thread"),
    )
    wandb.define_metric("*", step_metric="train/step")

    # Backend
    if USE_LOCAL_BACKEND:
        from art.local.backend import LocalBackend
        backend = LocalBackend()
    else:
        from art.skypilot.backend import SkyPilotBackend
        backend = await SkyPilotBackend.initialize_cluster(
            cluster_name=os.getenv("ART_SKYPILOT_CLUSTER", "art-cluster"),
            gpu=os.getenv("ART_GPU", "A100"),
        )

    model = art.TrainableModel(name=NAME, project=PROJECT_NAME, base_model=MODEL_NAME,
                               _internal_config=art.dev.InternalModelConfig(
                                   init_args=art.dev.InitArgs(gpu_memory_utilization=0.8, max_seq_length=MAX_SEQ_LEN),
                                   trainer_args=art.dev.TrainerArgs(max_grad_norm=0.1),
                               ),
                    )
    await model.register(backend)

    # 从 questions.txt 加载问题并构造场景
    questions = load_questions()
    scenarios = build_scenarios_from_questions(questions)

    training_config = {
        "groups_per_step": 2,
        "num_epochs": int(os.environ.get("NUM_EPOCHS", "2")),
        "rollouts_per_group": 3,
        "learning_rate": 1e-5,
        "max_steps": int(os.environ.get("MAX_STEPS", 10)),
    }
    wandb.config.update(training_config)

    # wandb 数据概览
    try:
        scen_table = wandb.Table(columns=["id", "topic"])
        for s in scenarios:
            scen_table.add_data(s.id, s.question)
        wandb.log({"data/training_scenarios": scen_table}, step=0)
    except Exception:
        pass

    # 数据迭代器
    it = iterate_dataset(
        scenarios,
        groups_per_step=training_config["groups_per_step"],
        num_epochs=training_config["num_epochs"],
        initial_step=await model.get_step(),
    )

    for batch in it:
        print(f"[train] step={batch.step} epoch={batch.epoch}")

        # 组装 TrajectoryGroup：每个样本 rollout 多条轨迹
        groups = []
        for one_item in batch.items:
            groups.append(
                art.TrajectoryGroup(
                    wrap_rollout(model, rollout)(model, one_item)
                    for _ in range(training_config["rollouts_per_group"])
                )
            )

        # 收集轨迹
        finished = await art.gather_trajectory_groups(
            groups, pbar_desc="gather",
            max_exceptions=training_config["rollouts_per_group"] * len(batch.items),
        )

        _log_batch_to_wandb(batch=batch, finished_groups=finished, use_ruler=USE_RULER)

        if USE_RULER:
            print(f"USE_RULER已经开启，使用RULER进行打分")
            assert RULER_API_KEY, "RULER_API_KEY not set"
            assert RULER_API_BASE, "RULER_API_BASE not set"
            extra_litellm_params = {"api_base": RULER_API_BASE, "api_key": RULER_API_KEY}
            judged = []
            for g in finished:
                t_list = list(g)
                completed = [t for t in t_list if getattr(t, "final", None)]
                try:
                    # 完成数如果太少，那么就使用原始的reward打分结果
                    if len(completed) >= 2:
                        jg = await ruler_score_group(
                            art.TrajectoryGroup(completed),
                            RULER_MODEL,
                            extra_litellm_params=extra_litellm_params,
                            debug=True
                        )
                        judged.append(jg)
                    else:
                        # 完成数太少：直接用原始（含你在 rollout 里设的 reward）
                        judged.append(art.TrajectoryGroup(t_list))
                except Exception:
                    # RULER 失效/异常时，退回无裁判训练
                    judged.append(art.TrajectoryGroup(t_list))
            # judged = [clip_group(g, MAX_SEQ_LEN) for g in judged]
            await model.train(
                trajectory_groups=judged,
                config=art.TrainConfig(learning_rate=training_config["learning_rate"]),
                _config={"logprob_calculation_chunk_size": 1024},
            )
            wandb.log({"train/used_judged_groups": 1}, step=batch.step)
        else:
            print("USE_RULER未开启，使用原始数据进行训练")
            # finished = [clip_group(g, MAX_SEQ_LEN) for g in finished]
            await model.train(
                trajectory_groups=finished,
                config=art.TrainConfig(learning_rate=training_config["learning_rate"]),
            )
            wandb.log({"train/used_judged_groups": 0}, step=batch.step)

        if batch.step >= training_config["max_steps"]:
            break

    wandb.finish()

if __name__ == "__main__":
    asyncio.run(main())
