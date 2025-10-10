# 显卡2用于训练时的推理，自动同步参数, 不同的模型Qwen/Qwen2.5-3B-Instruct
export CUDA_VISIBLE_DEVICES=2 \
swift rollout \
    --model Qwen/Qwen2.5-3B-Instruct
其它模型
Qwen/Qwen3-4B-Instruct-2507

# 显卡1用于训练, cd ms-swift目录下，然后运行GRPO， 使用lora训练, train_type 可以用full，表示完全微调
export CUDA_VISIBLE_DEVICES=1
swift rlhf \
    --rlhf_type grpo \
    --model Qwen/Qwen3-4B-Instruct-2507 \
    --external_plugins examples/train/grpo/plugin/plugin.py \
    --reward_funcs external_countdown format \
    --use_vllm true \
    --vllm_mode server \
    --vllm_server_host 127.0.0.1 \
    --vllm_server_port 8000 \
    --train_type lora \
    --lora_rank 8 \
    --lora_alpha 32 \
    --torch_dtype bfloat16 \
    --dataset 'zouxuhong/Countdown-Tasks-3to4#50000' \
    --load_from_cache_file true \
    --max_length 2048 \
    --max_completion_length 1024 \
    --num_train_epochs 1 \
    --per_device_train_batch_size 4 \
    --per_device_eval_batch_size 8 \
    --learning_rate 5e-7 \
    --gradient_accumulation_steps 8 \
    --eval_steps 500 \
    --save_steps 100 \
    --save_total_limit 20 \
    --logging_steps 1 \
    --output_dir output/GRPO_COUNTDOWN \
    --warmup_ratio 0.01 \
    --dataloader_num_workers 4 \
    --num_generations 8 \
    --temperature 1.0 \
    --system 'You are a helpful assistant. You first thinks about the reasoning process in the mind and then provides the user with the answer.' \
    --deepspeed zero3 \
    --log_completions true \
    --report_to tensorboard \
    --beta 0.001 \
    --num_iterations 1


# 数据对应的数据处理
ms-swift/swift/llm/dataset/dataset/llm.py

class CoundownTaskPreprocessor(ResponsePreprocessor):

    def preprocess(self, row: Dict[str, Any]) -> Dict[str, Any]:
        numbers = row['nums']
        target = row.pop('response', None)
        query = (f'Using the numbers {numbers}, create an equation that equals {target}.\n'
                 'You can use basic arithmetic operations (+, -, *, /) and each number can only be used once.\n'
                 'Show your work in <think> </think> tags. And return the final equation and answer '
                 'in <answer> </answer> tags, for example <answer> (1 + 2) / 3 * 4 = 4 </answer>.')
        row.update({'target': target, 'query': query})
        return super().preprocess(row)


register_dataset(
    DatasetMeta(
        ms_dataset_id='zouxuhong/Countdown-Tasks-3to4',
        subsets=['default'],
        preprocess_func=CoundownTaskPreprocessor(),
        tags=['math']))

