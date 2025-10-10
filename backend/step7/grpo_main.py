#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/9/28 21:17
# @File  : grpo_main.py.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 必须先启动qwen的rollout服务。 swift rollout --model Qwen/Qwen2.5-3B-Instruct

from swift.llm import rlhf_main, RLHFArguments

if __name__ == "__main__":
    args = RLHFArguments(
        # ==== 核心：RLHF/GRPO ====
        rlhf_type="grpo",
        # model="Qwen/Qwen3-0.6B",
        model="Qwen/Qwen2.5-3B-Instruct",
        train_type="lora",
        lora_rank=8,
        lora_alpha=32,
        # 数据集注册
        custom_register_path=["./dataset.py"],
        # 模型的模版
        loss_scale="hermes",
        agent_template="hermes",
        vllm_gpu_memory_utilization = 0.9,
        # ==== vLLM 推理后端（server 模式）====
        use_vllm=True,
        vllm_mode="server",
        vllm_server_host=["127.0.0.1"],
        vllm_server_port=[8000],

        # ==== 数据与长度 ====
        dataset=["custom_mcp_data"],
        load_from_cache_file=True,
        max_length=4096,
        max_completion_length=2048,

        # ==== 训练超参 ====
        num_train_epochs=1,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=2,
        learning_rate=5e-7,
        gradient_accumulation_steps=8,
        warmup_ratio=0.01,
        gradient_checkpointing=True,

        # ==== 采样与GRPO相关 ====
        num_generations=4,
        temperature=1.0,
        beta=0.001,              # GRPO 的 β（KL/约束强度等），与你 CLI 的 --beta 相同
        num_iterations=1,        # 与 --num_iterations 一致

        # ==== 评测与保存 ====
        eval_steps=500,
        save_steps=100,
        save_total_limit=20,
        logging_steps=1,
        output_dir="output/mcp_agent",

        #系统提示词
        system="""You are a helpful assistant. You can use tools help user.""",

        # ==== 设备/数值精度/加速 ====
        torch_dtype="bfloat16",
        deepspeed="zero3",       # 内置会解析到对应的 ds_config/zero3.json

        # ==== 日志与可视化 ====
        log_completions=True,
        report_to=["tensorboard"],

        # ==== 自定义奖励与插件 ====
        # CLI 里的 "--reward_funcs external_countdown format" → Python 用列表写法：
        reward_funcs=["format", "llm_ruler_reward"],
        # CLI 里的 "--external_plugins examples/train/grpo/plugin/plugin.py"
        external_plugins=["./plugin.py"],
        # 数据加载，debug时改成1个
        dataloader_num_workers=1,
    )

    rlhf_main(args)
