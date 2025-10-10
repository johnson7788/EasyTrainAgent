#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/9/29 13:08
# @File  : start_rollout.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 启动 Qwen rollout 服务

from swift.llm import rollout_main, RolloutArguments

if __name__ == "__main__":
    args = RolloutArguments(
        # ==== 核心：Rollout ====
        # model="Qwen/Qwen3-0.6B",   # 选择的模型
        model="Qwen/Qwen2.5-3B-Instruct",   # 选择的模型
        external_plugins=["./plugin.py"],
        vllm_max_model_len=8096,
        vllm_gpu_memory_utilization=0.8,
        vllm_use_async_engine=True,          # 使用异步引擎
        multi_turn_scheduler="mcp_call_scheduler",  # 多轮调度器
        max_turns=3,                        # 最大回合数
        log_level="debug",
        verbose=True,
    )
    rollout_main(args)
