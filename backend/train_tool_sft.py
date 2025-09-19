#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script:
- logs to Weights & Biases (optional)
- authenticates to Hugging Face (optional)
- loads "unsloth/Qwen3-4B-Instruct-2507" (default)
- formats *local* glaive_toolcall.jsonl into chat template tokens (tool-calling aware)
- runs SFT with LoRA via Unsloth
- saves LoRA adapters and (optionally) a merged 16-bit checkpoint for vLLM

Usage example:
python train_tool_sft.py --data_path ./glaive_toolcall.jsonl --epochs 3 --lr 2e-4 --batch_size 8 --grad_accum 2 --wandb_project toolsft

Environment variables expected (if using these services):
- WANDB_API_KEY
- HUGGINGFACE_TOKEN

References:
- Unsloth docs: https://docs.unsloth.ai
"""
import os
import json
import argparse
from typing import Dict, Any, List, Optional
from unsloth import FastModel
from dataclasses import dataclass
import torch
from datasets import load_dataset
from huggingface_hub import login
from transformers import TrainingArguments
# Unsloth imports
from trl import SFTConfig, SFTTrainer
from unsloth.chat_templates import get_chat_template

def maybe_login_wandb(project: str = None, run: str = None):
    """Initialize Weights & Biases logging if a project is provided."""
    if not project:
        print("[W&B] Skipping W&B init (no project provided).")
        return
    try:
        import wandb  # local import so it's optional
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("WANDB_API_KEY")
        if not api_key:
            raise EnvironmentError("WANDB_API_KEY is not set in the environment variables.")
        wandb.login(key=api_key)
        os.environ["WANDB_LOG_MODEL"] = "checkpoint"
        os.environ["WANDB_WATCH"] = "all"
        os.environ["WANDB_SILENT"] = "true"
        wandb.init(project=project, name=run or "train_function_model")
        print(f"[W&B] Initialized: project={project} run={run}")
    except Exception as e:
        print(f"[W&B] Could not initialize W&B: {e}")


def maybe_login_hf():
    """Login to Hugging Face Hub if HUGGINGFACE_TOKEN is present."""
    token = os.getenv("HUGGINGFACE_TOKEN")
    if token:
        try:
            login(token)
            print("[HF] Logged in to Hugging Face Hub.")
        except Exception as e:
            print(f"[HF] Login failed: {e}")
    else:
        print("[HF] HUGGINGFACE_TOKEN not set; skipping hub login.")


@dataclass
class TrainConfig:
    model_name: str = "unsloth/Qwen3-4B-Instruct-2507"
    # "unsloth/Meta-Llama-3.1-8B-Instruct" 和 unsloth/Qwen3-4B-Instruct-2507
    #"llama-3" 或者"qwen-3"
    # chat_template= "qwen-3"
    chat_template= "qwen-3"
    enable_thinking: bool = False  # Qwen3 Instruct 建议显式关闭
    # 数据集
    data_path: str = "glaive_toolcall.jsonl"
    subset_size: int = 0  # 0 or negative means full

    # Output
    out_dir: str = "outputs"
    lora_dir: str = "lora_model"
    merged_dir: str = "merged_model_16bit"
    hf_username: str = ""
    push_to_hub: bool = False
    save_merged: bool = False

    # LoRA / Unsloth
    max_seq_len: int = 2048
    lora_r: int = 16
    lora_alpha: int = 16
    lora_dropout: float = 0.0
    use_rslora: bool = False
    use_4bit: bool = False
    dtype: str = "auto"  # "auto" -> None for FastLanguageModel

    # Training
    batch_size: int = 8
    grad_accum: int = 2
    epochs: int = 3
    lr: float = 2e-4
    warmup_steps: int = 5
    seed: int = 3407
    weight_decay: float = 0.01
    scheduler: str = "linear"
    optim: str = "adamw_8bit"  # requires bitsandbytes

    # Logging
    wandb_project: str = ""
    wandb_run: str = ""


def build_argparser():
    p = argparse.ArgumentParser(description="Fine-tune Qwen3 Instruct for function calling via LoRA (Unsloth) on local Glaive jsonl.")
    p.add_argument("--model_name", default=TrainConfig.model_name)

    # chat template & thinking
    p.add_argument("--chat_template", default=TrainConfig.chat_template, help='e.g. "qwen-3" or "qwen-2.5"')
    p.add_argument("--enable_thinking", action="store_true",help="Enable Qwen3 thinking tags <think>...</think>. Default off for Instruct.")

    # local data
    p.add_argument("--data_path", default=TrainConfig.data_path, help="Path to glaive_toolcall.jsonl")
    p.add_argument("--subset_size", type=int, default=TrainConfig.subset_size, help="Use first N samples (0 = full).")

    # outputs
    p.add_argument("--out_dir", default=TrainConfig.out_dir)
    p.add_argument("--lora_dir", default=TrainConfig.lora_dir)
    p.add_argument("--merged_dir", default=TrainConfig.merged_dir)
    p.add_argument("--hf_username", default=TrainConfig.hf_username)
    p.add_argument("--push_to_hub", action="store_true")
    p.add_argument("--save_merged", action="store_true")

    # LoRA / dtype
    p.add_argument("--max_seq_len", type=int, default=TrainConfig.max_seq_len)
    p.add_argument("--lora_r", type=int, default=TrainConfig.lora_r)
    p.add_argument("--lora_alpha", type=int, default=TrainConfig.lora_alpha)
    p.add_argument("--lora_dropout", type=float, default=TrainConfig.lora_dropout)
    p.add_argument("--use_rslora", action="store_true")
    p.add_argument("--use_4bit", action="store_true")
    p.add_argument("--dtype", default=TrainConfig.dtype, help='Use "auto" for automatic dtype.')

    # training
    p.add_argument("--batch_size", type=int, default=TrainConfig.batch_size)
    p.add_argument("--grad_accum", type=int, default=TrainConfig.grad_accum)
    p.add_argument("--epochs", type=int, default=TrainConfig.epochs)
    p.add_argument("--lr", type=float, default=TrainConfig.lr)
    p.add_argument("--warmup_steps", type=int, default=TrainConfig.warmup_steps)
    p.add_argument("--seed", type=int, default=TrainConfig.seed)
    p.add_argument("--weight_decay", type=float, default=TrainConfig.weight_decay)
    p.add_argument("--scheduler", default=TrainConfig.scheduler)
    p.add_argument("--optim", default=TrainConfig.optim)

    # logging
    p.add_argument("--wandb_project", default=TrainConfig.wandb_project)
    p.add_argument("--wandb_run", default=TrainConfig.wandb_run)
    return p


def _tools_to_system_text(tools: Optional[List[Dict[str, Any]]]) -> str:
    if not tools:
        return "你是一个可以进行函数调用的助手。"
    return "你是一个可以进行函数调用的助手。可用工具如下（JSON Schema）：\n" + \
           json.dumps(tools, ensure_ascii=False, indent=2)


def _convert_conversations_glaive(conversations: List[Dict[str, Any]],
                                  tools: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Convert Glaive-style conversation list into OpenAI/llama3 tool-calling schema:
    - human -> user
    - gpt -> assistant (natural text)
    - function_call -> assistant with tool_calls
    - observation -> tool (tool result)
    """
    messages: List[Dict[str, Any]] = []
    # 1) System with tool list
    messages.append({"role": "system", "content": _tools_to_system_text(tools)})

    call_counter = 1
    last_call_id: Optional[str] = None
    last_func_name: Optional[str] = None

    for turn in conversations:
        role = turn.get("from")
        value = turn.get("value", "")

        if role == "human":
            messages.append({"role": "user", "content": str(value)})

        elif role == "gpt":
            messages.append({"role": "assistant", "content": str(value)})

        elif role == "function_call":
            try:
                fc = json.loads(value)
                name = fc.get("name", "")
                args = fc.get("arguments", {})
            except Exception:
                # 若出现非 JSON，尽量兜底为字符串参数
                name, args = "unknown_function", {"raw": str(value)}
            call_id = f"call_{call_counter}"
            call_counter += 1
            last_call_id = call_id
            last_func_name = name
            messages.append({
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {
                            "name": name,
                            "arguments": json.dumps(args, ensure_ascii=False),
                        },
                    }
                ],
            })

        elif role == "observation":
            # 工具输出内容直接作为 tool 消息；若没有上一个 function_call，则降级为 system 附注。
            if last_call_id and last_func_name:
                messages.append({
                    "role": "tool",
                    "tool_call_id": last_call_id,
                    "name": last_func_name,
                    "content": str(value),
                })
            else:
                messages.append({
                    "role": "system",
                    "content": f"（工具返回）{value}",
                })

        else:
            # 未知角色，写入系统注释，避免丢样本
            messages.append({"role": "system", "content": f"（未识别角色 {role}）{value}"})

    return messages


def format_glaive_dataset(tokenizer, dataset, chat_template: str, enable_thinking: bool):
    """
    Build Unsloth chat template Qwen (qwen-3; fallback qwen-2.5)  without role mapping (we already converted to OpenAI schema).
    """
    tokenizer = get_chat_template(
        tokenizer,
        chat_template=chat_template,
        map_eos_token=False,
    )

    def _format_batch(examples: Dict[str, List[Any]]):
        texts = []
        conv_batches = examples["conversations"]
        tools_batches = examples.get("tools", [None] * len(conv_batches))

        for conv, tools in zip(conv_batches, tools_batches):
            msgs = _convert_conversations_glaive(conv, tools)
            text = tokenizer.apply_chat_template(
                msgs,
                tokenize=False,
                add_generation_prompt=False,
            )
            texts.append(text)
        return {"text": texts}

    return tokenizer, dataset.map(_format_batch, batched=True, desc="Formatting Glaive to chat template")


def main():
    args = build_argparser().parse_args()

    # Init logging/auth
    maybe_login_wandb(args.wandb_project, args.wandb_run)
    maybe_login_hf()

    torch.manual_seed(args.seed)

    # Load base model
    dtype = None if args.dtype == "auto" else getattr(torch, args.dtype)
    model, tokenizer = FastModel.from_pretrained(
        model_name=args.model_name,
        max_seq_length=args.max_seq_len,
        load_in_4bit=args.use_4bit,
        load_in_8bit=False,
        full_finetuning=False,
        dtype=dtype,
    )

    # Configure LoRA PEFT
    model = FastModel.get_peft_model(
        model,
        r=args.lora_r,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=args.seed,
        use_rslora=args.use_rslora,
        loftq_config=None,
    )

    # Load local dataset
    if not os.path.exists(args.data_path):
        raise FileNotFoundError(f"[Data] Could not find file: {args.data_path}")
    dataset = load_dataset("json", data_files=args.data_path, split="train")
    if args.subset_size and args.subset_size > 0:
        dataset = dataset.select(range(min(args.subset_size, len(dataset))))
        print(f"[Data] Using subset of {len(dataset)} samples.")
    else:
        print(f"[Data] Using full dataset of {len(dataset)} samples.")

    # Tokenize/format
    tokenizer, dataset = format_glaive_dataset(tokenizer, dataset, args.chat_template, args.enable_thinking)

    sft_args = SFTConfig(
        # === 训练超参（你的 TrainingArguments 原样迁移）===
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        warmup_steps=args.warmup_steps,
        learning_rate=args.lr,
        num_train_epochs=args.epochs,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        optim=args.optim,
        weight_decay=args.weight_decay,
        lr_scheduler_type=args.scheduler,
        seed=args.seed,
        output_dir=args.out_dir,
        report_to=("wandb" if args.wandb_project else "none"),
        logging_steps=1,
        logging_strategy="steps",
        save_strategy="no",
        load_best_model_at_end=False,
        save_only_model=False,
        # === 数据相关（新版在 SFTConfig 里）===
        dataset_text_field="text",  # 可省略；默认就是 "text"
        dataset_num_proc=2,
        max_length=args.max_seq_len,  # 注意：字段名是 max_length（不是 max_seq_length）
        packing=False,
    )

    # Trainer
    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=dataset,
        args=sft_args,
    )

    # Memory stats (optional)
    if torch.cuda.is_available():
        gpu_stats = torch.cuda.get_device_properties(0)
        start_gpu_mem = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
        max_mem = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
        print(f"[GPU] {gpu_stats.name}. Max memory = {max_mem} GB. Reserved at start = {start_gpu_mem} GB.")

    # Train
    stats = trainer.train()
    print(stats)

    # Final memory
    if torch.cuda.is_available():
        used_mem = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
        start_gpu_mem = locals().get("start_gpu_mem", 0.0)
        used_for_lora = round(used_mem - start_gpu_mem, 3)
        gpu_stats = torch.cuda.get_device_properties(0)
        max_mem = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
        used_pct = round(used_mem / max_mem * 100, 3)
        lora_pct = round(used_for_lora / max_mem * 100, 3)
        print(f"[Train] Runtime (s): {stats.metrics.get('train_runtime', 'NA')}")
        print(f"[Mem] Peak reserved = {used_mem} GB ({used_pct}%). For training = {used_for_lora} GB ({lora_pct}%).")

    # Save LoRA adapters
    os.makedirs(args.lora_dir, exist_ok=True)
    model.save_pretrained(args.lora_dir)
    tokenizer.save_pretrained(args.lora_dir)
    print(f"[Save] LoRA adapters 保存模型到: {args.lora_dir}")

    # Push LoRA to hub
    if args.push_to_hub and args.hf_username:
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        repo = f"{args.hf_username}/{os.path.basename(os.path.abspath(args.lora_dir))}"
        model.push_to_hub(repo, token=hf_token)
        tokenizer.push_to_hub(repo, token=hf_token)
        print(f"[Hub] Pushed LoRA adapters to: {repo}")

    # Optionally merge to a 16-bit full model for vLLM
    if args.save_merged:
        os.makedirs(args.merged_dir, exist_ok=True)
        model.save_pretrained_merged(args.merged_dir, tokenizer, save_method="merged_16bit")
        print(f"[Save] Merged 16-bit model saved to: {args.merged_dir}")
        if args.push_to_hub and args.hf_username:
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            repo = f"{args.hf_username}/{os.path.basename(os.path.abspath(args.merged_dir))}"
            model.push_to_hub_merged(repo, tokenizer, save_method="merged_16bit", token=hf_token)
            print(f"[Hub] Pushed merged 16-bit model to: {repo}")

    # Close W&B run if any
    if args.wandb_project:
        try:
            import wandb
            wandb.finish()
        except Exception:
            pass


if __name__ == "__main__":
    main()
