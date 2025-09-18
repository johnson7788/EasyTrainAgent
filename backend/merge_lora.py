#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/9/4 20:55
# @File  : merge_lora.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : Merge LoRA adapter into base model

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_id = "unsloth/qwen2.5-7b-instruct-unsloth-bnb-4bit"  # base 模型
lora_dir = "/workspace/verl/ART/.art/content-training/models/ppt-content06/checkpoints/0002"  # LoRA 目录
out_dir = "./qwen2.5-7b-contentmodel"                    # 输出目录

print(f"[INFO] 加载 tokenizer 和 base 模型: {base_id}，确保显卡有足够的显存")
tok = AutoTokenizer.from_pretrained(base_id, use_fast=True)
base = AutoModelForCausalLM.from_pretrained(
    base_id,
    torch_dtype=torch.float16,
    device_map="auto"
)
print("[INFO] Base 模型加载完成")

print(f"[INFO] 加载 LoRA adapter: {lora_dir}")
peft_model = PeftModel.from_pretrained(base, lora_dir)
print("[INFO] LoRA adapter 挂载完成")

print("[INFO] 开始合并 LoRA 到 base 模型 (merge_and_unload)...")
merged = peft_model.merge_and_unload(safe_merge=True)
print("[INFO] 合并完成，得到纯 base+LoRA 模型")

print(f"[INFO] 保存合并后的模型到: {out_dir}")
merged.save_pretrained(out_dir, safe_serialization=True)
tok.save_pretrained(out_dir)
print("[INFO] 模型和 tokenizer 保存完成")
