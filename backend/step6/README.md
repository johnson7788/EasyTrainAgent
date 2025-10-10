# 合并SFT之后的lora模型
swift export \
  --model Qwen/Qwen3-4B-Instruct-2507 \
  --adapters output/v1-20250927-221821/checkpoint-2 \
  --merge_lora true \
  --output_dir output/merged_qwen3