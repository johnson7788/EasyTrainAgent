# 简单微调
https://swift.readthedocs.io/zh-cn/latest/GetStarted/%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B.html

swift sft \
    --model Qwen/Qwen2.5-7B-Instruct \
    --train_type lora \
    --dataset 'AI-ModelScope/alpaca-gpt4-data-zh#500' \
              'AI-ModelScope/alpaca-gpt4-data-en#500' \
              'swift/self-cognition#500' \
    --torch_dtype bfloat16 \
    --num_train_epochs 1 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --learning_rate 1e-4 \
    --lora_rank 8 \
    --lora_alpha 32 \
    --target_modules all-linear \
    --gradient_accumulation_steps 16 \
    --eval_steps 50 \
    --save_steps 50 \
    --save_total_limit 2 \
    --logging_steps 5 \
    --max_length 2048 \
    --output_dir output \
    --system 'You are a helpful assistant.' \
    --warmup_ratio 0.05 \
    --dataloader_num_workers 4 \
    --model_author swift \
    --model_name swift-robot



[INFO:modelscope] Download model 'Qwen/Qwen2.5-7B-Instruct' successfully.
[INFO:modelscope] Target directory already exists, skipping creation.
[INFO:swift] Loading the model using model_dir: /mnt/workspace/.cache/modelscope/hub/models/Qwen/Qwen2___5-7B-Instruct
[INFO:swift] model_kwargs: {'device_map': 'cuda:0'}
`torch_dtype` is deprecated! Use `dtype` instead!
Loading checkpoint shards: 100%|██████████████████████████████████████████████████████████████████████████████████| 4/4 [00:03<00:00,  1.23it/s]
[INFO:swift] model.hf_device_map: {'': device(type='cuda', index=0)}
[INFO:swift] model_info: ModelInfo(model_type='qwen2_5', model_dir='/mnt/workspace/.cache/modelscope/hub/models/Qwen/Qwen2___5-7B-Instruct', torch_dtype=torch.bfloat16, max_model_len=32768, quant_method=None, quant_bits=None, rope_scaling=None, is_moe_model=False, config=Qwen2Config {
  "architectures": [
    "Qwen2ForCausalLM"
  ],
  "attention_dropout": 0.0,
  "bos_token_id": 151643,
  "dtype": "bfloat16",
  "eos_token_id": 151645,
  "hidden_act": "silu",
  "hidden_size": 3584,
  "initializer_range": 0.02,
  "intermediate_size": 18944,
  "layer_types": [
    "full_attention",
    "full_attention",
    "full_attention",
    "full_attention"
  ],
  "max_position_embeddings": 32768,
  "max_window_layers": 28,
  "model_type": "qwen2",
  "num_attention_heads": 28,
  "num_hidden_layers": 28,
  "num_key_value_heads": 4,
  "pad_token_id": 151643,
  "rms_norm_eps": 1e-06,
  "rope_scaling": null,
  "rope_theta": 1000000.0,
  "sliding_window": null,
  "tie_word_embeddings": false,
  "transformers_version": "4.56.1",
  "use_cache": true,
  "use_sliding_window": false,
  "vocab_size": 152064
}
, task_type='causal_lm', num_labels=None)
[INFO:swift] model.generation_config: GenerationConfig {
  "bos_token_id": 151643,
  "eos_token_id": [
    151645,
    151643
  ],
  "max_new_tokens": 64,
  "pad_token_id": 151643,
  "repetition_penalty": 1.05
}
[INFO:swift] default_system: 'You are a helpful assistant.'
[INFO:swift] max_length: 2048
[INFO:swift] response_prefix: ''
[INFO:swift] agent_template: hermes
[INFO:swift] Start time of running main: 2025-09-26 12:58:24.591065
[INFO:swift] swift.__version__: 3.8.1
[INFO:swift] SelfCognitionPreprocessor has been successfully configured with name: ('swift-robot', 'swift-robot'), author: ('swift', 'swift').
[INFO:swift] Downloading the dataset from ModelScope, dataset_id: AI-ModelScope/alpaca-gpt4-data-zh
Downloading [README.md]: 100%|█████████████████████████████████████████████████████████████████████████████| 1.23k/1.23k [00:00<00:00, 7.09MB/s]
Downloading data: 31.8MB [00:08, 3.66MB/s]
Generating train split: 48818 examples [00:00, 65753.46 examples/s]
Map: 100%|██████████████████████████████████████████████████████████████████████████████████████| 48818/48818 [00:01<00:00, 34896.75 examples/s]
[INFO:swift] Downloading the dataset from ModelScope, dataset_id: AI-ModelScope/alpaca-gpt4-data-en
Downloading [README.md]: 100%|██████████████████████████████████████████████████████████████████████████████| 1.23k/1.23k [00:00<00:00, 803kB/s]
Downloading data: 88.3MB [00:24, 3.62MB/s]
Generating train split: 52002 examples [00:01, 42855.58 examples/s]
Map: 100%|██████████████████████████████████████████████████████████████████████████████████████| 52002/52002 [00:01<00:00, 40120.21 examples/s]
[INFO:swift] Downloading the dataset from ModelScope, dataset_id: swift/self-cognition
Downloading [README.md]: 100%|█████████████████████████████████████████████████████████████████████████████| 1.98k/1.98k [00:00<00:00, 14.8MB/s]
Downloading data: 100%|████████████████████████████████████████████████████████████████████████████████████| 23.8k/23.8k [00:00<00:00, 44.1MB/s]
Generating train split: 108 examples [00:00, 27537.07 examples/s]
Map: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 108/108 [00:00<00:00, 4136.58 examples/s]
[WARNING:swift] dataset_sample:500 is greater than len(dataset):108, repeated sampling will be performed.
[INFO:swift] train_dataset: Dataset({
    features: ['messages'],
    num_rows: 1500
})
[INFO:swift] val_dataset: None
Map: 100%|█████████████████████████████████████████████████████████████████████████████████████████| 1500/1500 [00:01<00:00, 1026.76 examples/s]
[INFO:swift] [INPUT_IDS] [151644, 8948, 198, 2610, 525, 264, 10950, 17847, 13, 151645, 198, 151644, 872, 198, 105043, 9686, 70, 417, 101037, 151645, 198, 151644, 77091, 198, 99520, 9370, 3837, 111020, 15672, 38, 2828, 1773, 104198, 67071, 70642, 100013, 100623, 48692, 100168, 104949, 70642, 12, 18247, 1773, 107055, 99885, 106603, 57191, 85106, 100364, 3837, 100437, 102422, 69041, 35946, 107666, 1773, 151645]
[INFO:swift] [INPUT] <|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
你是chatgpt吗<|im_end|>
<|im_start|>assistant
不是的，我不是ChatGPT。我是由swift开发的人工智能模型swift-robot。如果有任何疑问或需要帮助，欢迎随时向我提问。<|im_end|>
[INFO:swift] [LABELS_IDS] [-100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, 99520, 9370, 3837, 111020, 15672, 38, 2828, 1773, 104198, 67071, 70642, 100013, 100623, 48692, 100168, 104949, 70642, 12, 18247, 1773, 107055, 99885, 106603, 57191, 85106, 100364, 3837, 100437, 102422, 69041, 35946, 107666, 1773, 151645]
[INFO:swift] [LABELS] [-100 * 24]不是的，我不是ChatGPT。我是由swift开发的人工智能模型swift-robot。如果有任何疑问或需要帮助，欢迎随时向我提问。<|im_end|>
[INFO:swift] Dataset Token Length: 130.807333±103.982221, min=29.000000, max=550.000000, size=1500
[INFO:swift] The TrainArguments will be saved in: /workspace/verl/output/v0-20250926-114832/args.json
/usr/local/lib/python3.11/site-packages/awq/__init__.py:21: DeprecationWarning:
I have left this message as the final dev message to help you transition.
Important Notice:
- AutoAWQ is officially deprecated and will no longer be maintained.
- The last tested configuration used Torch 2.6.0 and Transformers 4.51.3.
- If future versions of Transformers break AutoAWQ compatibility, please report the issue to the Transformers project.

Alternative:
- AutoAWQ has been adopted by the vLLM Project: https://github.com/vllm-project/llm-compressor

For further inquiries, feel free to reach out:
- X: https://x.com/casper_hansen_
- LinkedIn: https://www.linkedin.com/in/casper-hansen-804005170/

  warnings.warn(_FINAL_DEV_MESSAGE, category=DeprecationWarning, stacklevel=1)
[INFO:swift] lora_config: LoraConfig(task_type='CAUSAL_LM', peft_type=<PeftType.LORA: 'LORA'>, auto_mapping=None, base_model_name_or_path='/mnt/
workspace/.cache/modelscope/hub/models/Qwen/Qwen2___5-7B-Instruct', revision=None, inference_mode=False, r=8, target_modules={'down_proj', 'o_pr
oj', 'gate_proj', 'q_proj', 'v_proj', 'up_proj', 'k_proj'}, exclude_modules=None, lora_alpha=32, lora_dropout=0.05, fan_in_fan_out=False, bias='
none', use_rslora=False, modules_to_save=[], init_lora_weights=True, layers_to_transform=None, layers_pattern=None, rank_pattern={}, alpha_patte
rn={}, megatron_config=None, megatron_core='megatron.core', trainable_token_indices=None, loftq_config={}, eva_config=None, corda_config=None, u
se_dora=False, use_qalora=False, qalora_group_size=16, layer_replication=None, runtime_config=LoraRuntimeConfig(ephemeral_gpu_offload=False), lo
ra_bias=False, target_parameters=None, lora_dtype=None, lorap_lr_ratio=None, lorap_emb_lr=1e-06)
[INFO:swift] model: PeftModelForCausalLM(
  (base_model): LoraModel(
    (model): Qwen2ForCausalLM(
      (model): Qwen2Model(
        (embed_tokens): Embedding(152064, 3584)
        (layers): ModuleList(
          (0-27): 28 x Qwen2DecoderLayer(
            (self_attn): Qwen2Attention(
-               (q_proj): lora.Linear(
                (base_layer): Linear(in_features=3584, out_features=3584, bias=True)
                (lora_dropout): ModuleDict(
                  (default): Dropout(p=0.05, inplace=False)
                )
                (lora_A): ModuleDict(
                  (default): Linear(in_features=3584, out_features=8, bias=False)
                )
                (lora_B): ModuleDict(
                  (default): Linear(in_features=8, out_features=3584, bias=False)
                )
                (lora_embedding_A): ParameterDict()
                (lora_embedding_B): ParameterDict()
                (lora_magnitude_vector): ModuleDict()
              )
              (k_proj): lora.Linear(
                (base_layer): Linear(in_features=3584, out_features=512, bias=True)
                (lora_dropout): ModuleDict(
                  (default): Dropout(p=0.05, inplace=False)
                )
                (lora_A): ModuleDict(
                  (default): Linear(in_features=3584, out_features=8, bias=False)
                )
                (lora_B): ModuleDict(
                  (default): Linear(in_features=8, out_features=512, bias=False)
                )
                (lora_embedding_A): ParameterDict()
                (lora_embedding_B): ParameterDict()
                (lora_magnitude_vector): ModuleDict()
              )
              (v_proj): lora.Linear(
                (base_layer): Linear(in_features=3584, out_features=512, bias=True)
                (lora_dropout): ModuleDict(
                  (default): Dropout(p=0.05, inplace=False)
                )
                (lora_A): ModuleDict(
                  (default): Linear(in_features=3584, out_features=8, bias=False)
                )
                (lora_B): ModuleDict(
                  (default): Linear(in_features=8, out_features=512, bias=False)
                )
                (lora_embedding_A): ParameterDict()
                (lora_embedding_B): ParameterDict()
                (lora_magnitude_vector): ModuleDict()
              )
              (o_proj): lora.Linear(
                (base_layer): Linear(in_features=3584, out_features=3584, bias=False)
                (lora_dropout): ModuleDict(
                  (default): Dropout(p=0.05, inplace=False)
                )
                (lora_A): ModuleDict(
                  (default): Linear(in_features=3584, out_features=8, bias=False)
                )
                (lora_B): ModuleDict(
                  (default): Linear(in_features=8, out_features=3584, bias=False)
              (down_proj): lora.Linear(
                (base_layer): Linear(in_features=18944, out_features=3584, bias=False)
                (lora_dropout): ModuleDict(
                  (default): Dropout(p=0.05, inplace=False)
                )
                (lora_A): ModuleDict(
                  (default): Linear(in_features=18944, out_features=8, bias=False)
                )
                (lora_B): ModuleDict(
                  (default): Linear(in_features=8, out_features=3584, bias=False)
                )
                (lora_embedding_A): ParameterDict()
                (lora_embedding_B): ParameterDict()
                (lora_magnitude_vector): ModuleDict()
              )
              (act_fn): SiLU()
            )
            (input_layernorm): Qwen2RMSNorm((3584,), eps=1e-06)
            (post_attention_layernorm): Qwen2RMSNorm((3584,), eps=1e-06)
          )
        )
        (norm): Qwen2RMSNorm((3584,), eps=1e-06)
        (rotary_emb): Qwen2RotaryEmbedding()
      )
      (lm_head): Linear(in_features=3584, out_features=152064, bias=False)
    )
  )
)
[INFO:swift] model_parameter_info: PeftModelForCausalLM: 7635.8016M Params (20.1851M Trainable [0.2643%]), 0.0001M Buffers.
/usr/local/lib/python3.11/site-packages/swift/trainers/mixin.py:104: FutureWarning: `tokenizer` is deprecated and will be removed in version 5.0.0 for `Seq2SeqTrainer.__init__`. Use `processing_class` instead.
  super().__init__(
/usr/local/lib/python3.11/site-packages/deepspeed/ops/op_builder/builder.py:16: DeprecationWarning: The distutils package is deprecated and slated for removal in Python 3.12. Use setuptools or check PEP 632 for potential alternatives
  import distutils.ccompiler
/usr/local/lib/python3.11/site-packages/deepspeed/ops/op_builder/builder.py:18: DeprecationWarning: The distutils.sysconfig module is deprecated, use sysconfig instead
  import distutils.sysconfig
[2025-09-26 13:00:44,888] [INFO] [real_accelerator.py:260:get_accelerator] Setting ds_accelerator to cuda (auto detect)
df: /root/.triton/autotune: 没有那个文件或目录
[2025-09-26 13:00:46,797] [INFO] [logging.py:107:log_dist] [Rank -1] [TorchCheckpointEngine] Initialized with serialization = False
[INFO:swift] use_reentrant: True
[INFO:swift] The logging file will be saved in: /workspace/verl/output/v0-20250926-114832/logging.jsonl
The tokenizer has new PAD/BOS/EOS tokens that differ from the model config and generation config. The model config and generation config were aligned accordingly, being updated with the tokenizer's values. Updated tokens: {'bos_token_id': None}.
Train:   0%|                                                                                                             | 0/94 [00:00<?, ?it/s]/usr/local/lib/python3.11/site-packages/torch/cuda/__init__.py:61: FutureWarning: The pynvml package is deprecated. Please install nvidia-ml-py instead. If you did not install pynvml directly, please report this to the maintainers of the package that installed pynvml for you.
  import pynvml  # type: ignore[import]
[INFO:swift] use_logits_to_keep: True
{'loss': 1.4749825, 'grad_norm': 1.59615517, 'learning_rate': 2e-05, 'token_acc': 0.66827957, 'epoch': 0.01, 'global_step/max_steps': '1/94', 'percentage': '1.06%', 'elapsed_time': '7s', 'remaining_time': '12m 6s', 'memory(GiB)': 16.75, 'train_speed(iter/s)': 0.128088}
{'loss': 1.72185874, 'grad_norm': 1.92592478, 'learning_rate': 0.0001, 'token_acc': 0.64476276, 'epoch': 0.05, 'global_step/max_steps': '5/94', 'percentage': '5.32%', 'elapsed_time': '32s', 'remaining_time': '9m 36s', 'memory(GiB)': 17.47, 'train_speed(iter/s)': 0.154297}
{'loss': 1.35411816, 'grad_norm': 0.95349097, 'learning_rate': 9.922e-05, 'token_acc': 0.6687643, 'epoch': 0.11, 'global_step/max_steps': '10/94', 'percentage': '10.64%', 'elapsed_time': '1m 3s', 'remaining_time': '8m 50s', 'memory(GiB)': 17.47, 'train_speed(iter/s)': 0.158366}
{'loss': 1.27653036, 'grad_norm': 0.64977044, 'learning_rate': 9.692e-05, 'token_acc': 0.66162008, 'epoch': 0.16, 'global_step/max_steps': '15/94', 'percentage': '15.96%', 'elapsed_time': '1m 33s', 'remaining_time': '8m 14s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.159901}
{'loss': 1.22438469, 'grad_norm': 0.62878072, 'learning_rate': 9.315e-05, 'token_acc': 0.66291977, 'epoch': 0.21, 'global_step/max_steps': '20/94', 'percentage': '21.28%', 'elapsed_time': '2m 4s', 'remaining_time': '7m 41s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.160312}
{'loss': 1.06875381, 'grad_norm': 0.9624899, 'learning_rate': 8.176e-05, 'token_acc': 0.68718656, 'epoch': 0.32, 'global_step/max_steps': '30/94', 'percentage': '31.91%', 'elapsed_time': '3m 5s', 'remaining_time': '6m 36s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.161411}
{'loss': 1.14363508, 'grad_norm': 0.62338978, 'learning_rate': 7.449e-05, 'token_acc': 0.68429361, 'epoch': 0.37, 'global_step/max_steps': '35/94', 'percentage': '37.23%', 'elapsed_time': '3m 35s', 'remaining_time': '6m 3s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.162096}
{'loss': 1.15083075, 'grad_norm': 0.77291209, 'learning_rate': 6.645e-05, 'token_acc': 0.68132029, 'epoch': 0.43, 'global_step/max_steps': '40/94', 'percentage': '42.55%', 'elapsed_time': '4m 6s', 'remaining_time': '5m 32s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.162586}
{'loss': 1.04461298, 'grad_norm': 0.41802394, 'learning_rate': 5.791e-05, 'token_acc': 0.70528012, 'epoch': 0.48, 'global_step/max_steps': '45/94', 'percentage': '47.87%', 'elapsed_time': '4m 36s', 'remaining_time': '5m 1s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.162757}
{'loss': 1.17622795, 'grad_norm': 0.67498571, 'learning_rate': 4.912e-05, 'token_acc': 0.67076671, 'epoch': 0.53, 'global_step/max_steps': '50/94', 'percentage': '53.19%', 'elapsed_time': '5m 6s', 'remaining_time': '4m 30s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.162917}
Train:  53%|█████████████████████████████████████████████████████▏                                              | 50/94 [05:06<04:25,  6.03s/it][INFO:swift] Saving model checkpoint to /workspace/verl/output/v0-20250926-114832/checkpoint-50
{'loss': 1.25931406, 'grad_norm': 0.70017552, 'learning_rate': 4.035e-05, 'token_acc': 0.64513743, 'epoch': 0.59, 'global_step/max_steps': '55/94', 'percentage': '58.51%', 'elapsed_time': '5m 37s', 'remaining_time': '3m 59s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.163147}
{'loss': 1.00852137, 'grad_norm': 0.55153394, 'learning_rate': 3.189e-05, 'token_acc': 0.70592486, 'epoch': 0.64, 'global_step/max_steps': '60/94', 'percentage': '63.83%', 'elapsed_time': '6m 6s', 'remaining_time': '3m 27s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.163604}
{'loss': 1.11549168, 'grad_norm': 0.67940325, 'learning_rate': 2.399e-05, 'token_acc': 0.69179487, 'epoch': 0.69, 'global_step/max_steps': '65/94', 'percentage': '69.15%', 'elapsed_time': '6m 35s', 'remaining_time': '2m 56s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.16429}
{'loss': 1.06401749, 'grad_norm': 0.50387096, 'learning_rate': 1.689e-05, 'token_acc': 0.69981038, 'epoch': 0.75, 'global_step/max_steps': '70/94', 'percentage': '74.47%', 'elapsed_time': '7m 5s', 'remaining_time': '2m 26s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.164329}
{'loss': 1.16705465, 'grad_norm': 0.60562009, 'learning_rate': 1.083e-05, 'token_acc': 0.66741811, 'epoch': 0.8, 'global_step/max_steps': '75/94', 'percentage': '79.79%', 'elapsed_time': '7m 35s', 'remaining_time': '1m 55s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.164534}
{'loss': 1.08200331, 'grad_norm': 0.65198541, 'learning_rate': 5.98e-06, 'token_acc': 0.69363553, 'epoch': 0.85, 'global_step/max_steps': '80/94', 'percentage': '85.11%', 'elapsed_time': '8m 5s', 'remaining_time': '1m 25s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.164654}
{'loss': 1.0843091, 'grad_norm': 0.72754085, 'learning_rate': 2.5e-06, 'token_acc': 0.68906786, 'epoch': 0.91, 'global_step/max_steps': '85/94', 'percentage': '90.43%', 'elapsed_time': '8m 35s', 'remaining_time': '54s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.164761}
{'loss': 1.06825314, 'grad_norm': 0.53342998, 'learning_rate': 5e-07, 'token_acc': 0.70450556, 'epoch': 0.96, 'global_step/max_steps': '90/94', 'percentage': '95.74%', 'elapsed_time': '9m 6s', 'remaining_time': '24s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.164716}
Train: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 94/94 [09:29<00:00,  5.76s/it][INFO:swift] Saving model checkpoint to /workspace/verl/output/v0-20250926-114832/checkpoint-94
{'train_runtime': 570.417, 'train_samples_per_second': 2.63, 'train_steps_per_second': 0.165, 'train_loss': 1.16871121, 'token_acc': 0.69184366, 'epoch': 1.0, 'global_step/max_steps': '94/94', 'percentage': '100.00%', 'elapsed_time': '9m 30s', 'remaining_time': '0s', 'memory(GiB)': 18.33, 'train_speed(iter/s)': 0.164799}
Train: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████| 94/94 [09:30<00:00,  6.07s/it]
[INFO:swift] last_model_checkpoint: /workspace/verl/output/v0-20250926-114832/checkpoint-94
[INFO:swift] best_model_checkpoint: None
[INFO:swift] images_dir: /workspace/verl/output/v0-20250926-114832/images
[INFO:swift] End time of running main: 2025-09-26 13:10:19.818606

# 训练的输出结果
```
 tree
.
└── v0-20250926-114832
    ├── args.json
    ├── checkpoint-50
    │   ├── adapter_config.json
    │   ├── adapter_model.safetensors
    │   ├── additional_config.json
    │   ├── args.json
    │   ├── optimizer.pt
    │   ├── README.md
    │   ├── rng_state.pth
    │   ├── scheduler.pt
    │   ├── trainer_state.json
    │   └── training_args.bin
    ├── checkpoint-94
    │   ├── adapter_config.json
    │   ├── adapter_model.safetensors
    │   ├── additional_config.json
    │   ├── args.json
    │   ├── optimizer.pt
    │   ├── README.md
    │   ├── rng_state.pth
    │   ├── scheduler.pt
    │   ├── trainer_state.json
    │   └── training_args.bin
    ├── images
    │   ├── train_epoch.png
    │   ├── train_grad_norm.png
    │   ├── train_learning_rate.png
    │   ├── train_loss.png
    │   ├── train_token_acc.png
    │   ├── train_total_flos.png
    │   ├── train_train_loss.png
    │   ├── train_train_runtime.png
    │   ├── train_train_samples_per_second.png
    │   └── train_train_steps_per_second.png
    ├── logging.jsonl
    └── runs
        └── events.out.tfevents.1758862847.yaqiyun-SYS-4028GR-TR2.318.0
```

## 查看训练日志
cd output/v0-20250926-114832
tensorboard --logdir runs
访问：http://localhost:6006/

一轮完整训练的输出目录（时间戳结尾）。里面最关键的是：

args.json：你运行脚本时的高层参数（模型名、数据路径、LoRA/QLoRA 开关、batch size、epochs 等）。用于记录可复现性。

logging.jsonl：逐步训练日志（JSON Lines）。里面通常有 step/epoch/loss/learning_rate/grad_norm/token_acc 等字段，是做曲线和对比 checkpoint 的原始数据源。

runs/events.out.tfevents...：TensorBoard 事件文件，和 images/ 是同一批指标的可视化两种形式。

checkpoint-50 与 checkpoint-94

这是按 step 保存的两个检查点。它们都包含：

adapter_model.safetensors + adapter_config.json：如果是 LoRA/QLoRA，只保存增量参数（适配器）；推理时要和底模合用。

training_args.bin / args.json：训练器与任务参数快照。

optimizer.pt / scheduler.pt / rng_state.pth：用于从该步精确恢复训练（继续训/再现 bug）。

trainer_state.json：记录到这个检查点时训练进度（全局 step、最佳指标、最近的 log history 截断等）。

README.md：多数框架自动生成的“怎么用这个检查点”的提示。

小结：如果你只是要推理/验证效果，通常只需要 adapter_model.safetensors（以及底模）；如果要继续训练，就连同 optimizer.pt / scheduler.pt 一起用。

images/ 指标图（快速肉眼诊断）

这些图名基本对应下列结论要点：

train_loss.png / train_train_loss.png：总体/批内训练损失。应随 step 下降并逐渐平滑；后期若抖动或回升，可能学习率过大、过拟合或数据噪声。

train_token_acc.png：逐 token 训练准确率。应与 loss 反向相关，平稳上升。后期平台期正常；突然掉头通常是学习率/梯度异常。

train_learning_rate.png：学习率调度曲线（warmup → cosine/linear 等）。看拐点是否对应 loss 的改善或震荡。

train_grad_norm.png：梯度范数。尖刺/爆炸是危险信号（可能需要 grad clip、更小 lr、缩小 batch）。

train_total_flos.png：累计浮点计算量（增长单调，主要用于核查吞吐）。

train_runtime / steps_per_second / samples_per_second.png：吞吐与稳定性。如果中途有阶梯式跌落，可能 I/O、数据分布、混合精度降级或重启。

train_epoch.png：按 epoch 聚合的指标，对看跨 epoch 趋势有用。


## args.json
{
  "output_dir": "/workspace/verl/output/v0-20250926-114832",
  "overwrite_output_dir": false,
  "do_train": false,
  "do_eval": false,
  "do_predict": false,
  "eval_strategy": "no",
  "prediction_loss_only": false,
  "per_device_train_batch_size": 1,
  "per_device_eval_batch_size": 1,
  "per_gpu_train_batch_size": null,
  "per_gpu_eval_batch_size": null,
  "gradient_accumulation_steps": 16,
  "eval_accumulation_steps": null,
  "eval_delay": 0,
  "torch_empty_cache_steps": null,
  "learning_rate": 0.0001,
  "weight_decay": 0.1,
  "adam_beta1": 0.9,
  "adam_beta2": 0.95,
  "adam_epsilon": 1e-08,
  "max_grad_norm": 1.0,
  "num_train_epochs": 1.0,
  "max_steps": -1,
  "lr_scheduler_type": "cosine",
  "lr_scheduler_kwargs": null,
  "warmup_ratio": 0.05,
  "warmup_steps": 0,
  "log_level": "passive",
  "log_level_replica": "warning",
  "log_on_each_node": true,
  "logging_dir": "/workspace/verl/output/v0-20250926-114832/runs",
  "logging_strategy": "steps",
  "logging_first_step": true,
  "logging_steps": 5,
  "logging_nan_inf_filter": true,
  "save_strategy": "steps",
  "save_steps": 50.0,
  "save_total_limit": 2,
  "save_safetensors": true,
  "save_on_each_node": false,
  "save_only_model": false,
  "restore_callback_states_from_checkpoint": false,
  "no_cuda": false,
  "use_cpu": false,
  "use_mps_device": false,
  "seed": 42,
  "data_seed": 42,
  "jit_mode_eval": false,
  "use_ipex": false,
  "bf16": true,
  "fp16": false,
  "fp16_opt_level": "O1",
  "half_precision_backend": "auto",
  "bf16_full_eval": false,
  "fp16_full_eval": false,
  "tf32": null,
  "local_rank": -1,
  "ddp_backend": null,
  "tpu_num_cores": null,
  "tpu_metrics_debug": false,
  "debug": null,
  "dataloader_drop_last": false,
  "eval_steps": 50.0,
  "dataloader_num_workers": 4,
  "dataloader_prefetch_factor": null,
  "past_index": -1,
  "run_name": "/workspace/verl/output/v0-20250926-114832",
  "disable_tqdm": null,
  "remove_unused_columns": true,
  "label_names": null,
  "load_best_model_at_end": false,
  "metric_for_best_model": "loss",
  "greater_is_better": false,
  "ignore_data_skip": false,
  "fsdp": "",
  "fsdp_min_num_params": 0,
  "fsdp_config": null,
  "fsdp_transformer_layer_cls_to_wrap": null,
  "accelerator_config": {
    "dispatch_batches": false
  },
  "parallelism_config": null,
  "deepspeed": null,
  "label_smoothing_factor": 0.0,
  "optim": "adamw_torch",
  "optim_args": null,
  "adafactor": false,
  "group_by_length": false,
  "length_column_name": "length",
  "report_to": [
    "tensorboard"
  ],
  "ddp_find_unused_parameters": null,
  "ddp_bucket_cap_mb": null,
  "ddp_broadcast_buffers": null,
  "dataloader_pin_memory": true,
  "dataloader_persistent_workers": false,
  "skip_memory_metrics": true,
  "use_legacy_prediction_loop": false,
  "push_to_hub": false,
  "resume_from_checkpoint": null,
  "hub_model_id": null,
  "hub_strategy": "every_save",
  "hub_token": null,
  "hub_private_repo": null,
  "hub_always_push": false,
  "hub_revision": null,
  "gradient_checkpointing": true,
  "gradient_checkpointing_kwargs": null,
  "include_inputs_for_metrics": false,
  "include_for_metrics": [],
  "eval_do_concat_batches": true,
  "fp16_backend": "auto",
  "push_to_hub_model_id": null,
  "push_to_hub_organization": null,
  "push_to_hub_token": null,
  "mp_parameters": "",
  "auto_find_batch_size": false,
  "full_determinism": false,
  "torchdynamo": null,
  "ray_scope": "last",
  "ddp_timeout": 18000000,
  "torch_compile": false,
  "torch_compile_backend": null,
  "torch_compile_mode": null,
  "include_tokens_per_second": false,
  "include_num_input_tokens_seen": false,
  "neftune_noise_alpha": null,
  "optim_target_modules": null,
  "batch_eval_metrics": false,
  "eval_on_start": false,
  "use_liger_kernel": false,
  "liger_kernel_config": null,
  "eval_use_gather_object": false,
  "average_tokens_across_devices": true,
  "sortish_sampler": false,
  "predict_with_generate": false,
  "generation_max_length": null,
  "generation_num_beams": null,
  "generation_config": null,
  "tuner_backend": "peft",
  "vit_gradient_checkpointing": null,
  "router_aux_loss_coef": 0.0,
  "enable_dft_loss": false,
  "enable_channel_loss": false,
  "check_model": true,
  "acc_strategy": "token",
  "train_dataloader_shuffle": true,
  "max_epochs": null,
  "aligner_lr": null,
  "vit_lr": null,
  "use_logits_to_keep": null,
  "ds3_gather_for_generation": true,
  "resume_only_model": false,
  "optimizer": null,
  "loss_type": null,
  "metric": null,
  "eval_use_evalscope": false,
  "eval_dataset": [],
  "eval_dataset_args": null,
  "eval_limit": null,
  "eval_generation_config": null,
  "extra_eval_args": null,
  "use_flash_ckpt": false,
  "model": "Qwen/Qwen2.5-7B-Instruct",
  "model_type": "qwen2_5",
  "model_revision": null,
  "task_type": "causal_lm",
  "torch_dtype": "bfloat16",
  "attn_impl": null,
  "new_special_tokens": [],
  "num_labels": null,
  "problem_type": null,
  "rope_scaling": null,
  "device_map": null,
  "max_memory": {},
  "max_model_len": null,
  "local_repo_path": null,
  "init_strategy": null,
  "template": "qwen2_5",
  "system": "You are a helpful assistant.",
  "max_length": 2048,
  "truncation_strategy": "delete",
  "max_pixels": null,
  "agent_template": null,
  "norm_bbox": null,
  "use_chat_template": true,
  "padding_free": false,
  "padding_side": "right",
  "loss_scale": "default",
  "sequence_parallel_size": 1,
  "response_prefix": null,
  "template_backend": "swift",
  "dataset": [
    "AI-ModelScope/alpaca-gpt4-data-zh#500",
    "AI-ModelScope/alpaca-gpt4-data-en#500",
    "swift/self-cognition#500"
  ],
  "val_dataset": [],
  "split_dataset_ratio": 0.0,
  "dataset_num_proc": 1,
  "load_from_cache_file": true,
  "dataset_shuffle": true,
  "val_dataset_shuffle": false,
  "streaming": false,
  "interleave_prob": null,
  "stopping_strategy": "first_exhausted",
  "shuffle_buffer_size": 1000,
  "download_mode": "reuse_dataset_if_exists",
  "columns": {},
  "strict": false,
  "model_name": [
    "swift-robot"
  ],
  "model_author": [
    "swift"
  ],
  "custom_dataset_info": [],
  "quant_method": null,
  "quant_bits": null,
  "hqq_axis": null,
  "bnb_4bit_compute_dtype": "bfloat16",
  "bnb_4bit_quant_type": "nf4",
  "bnb_4bit_use_double_quant": true,
  "bnb_4bit_quant_storage": null,
  "max_new_tokens": 64,
  "temperature": 0.0,
  "top_k": null,
  "top_p": null,
  "repetition_penalty": null,
  "num_beams": 1,
  "stream": false,
  "stop_words": [],
  "logprobs": false,
  "top_logprobs": null,
  "ckpt_dir": null,
  "lora_modules": [],
  "train_type": "lora",
  "adapters": [],
  "external_plugins": [],
  "model_kwargs": {},
  "load_args": false,
  "load_data_args": false,
  "packing": false,
  "packing_length": null,
  "lazy_tokenize": false,
  "cached_dataset": [],
  "custom_register_path": [],
  "use_hf": false,
  "ignore_args_error": false,
  "use_swift_lora": false,
  "freeze_parameters": [],
  "freeze_parameters_regex": null,
  "freeze_parameters_ratio": 0.0,
  "trainable_parameters": [],
  "trainable_parameters_regex": null,
  "freeze_llm": false,
  "freeze_vit": true,
  "freeze_aligner": true,
  "target_modules": [
    "all-linear"
  ],
  "target_regex": null,
  "target_parameters": null,
  "modules_to_save": [],
  "lora_rank": 8,
  "lora_alpha": 32,
  "lora_dropout": 0.05,
  "lora_bias": "none",
  "lora_dtype": null,
  "lorap_lr_ratio": null,
  "use_rslora": false,
  "use_dora": false,
  "lora_ga_batch_size": 2,
  "lora_ga_iters": 2,
  "lora_ga_max_length": 1024,
  "lora_ga_direction": "ArB2r",
  "lora_ga_scale": "stable",
  "lora_ga_stable_gamma": 16,
  "init_weights": true,
  "fourier_n_frequency": 2000,
  "fourier_scaling": 300.0,
  "boft_block_size": 4,
  "boft_block_num": 0,
  "boft_n_butterfly_factor": 1,
  "boft_dropout": 0.0,
  "vera_rank": 256,
  "vera_projection_prng_key": 0,
  "vera_dropout": 0.0,
  "vera_d_initial": 0.1,
  "adapter_act": "gelu",
  "adapter_length": 128,
  "use_galore": false,
  "galore_target_modules": null,
  "galore_rank": 128,
  "galore_update_proj_gap": 50,
  "galore_scale": 1.0,
  "galore_proj_type": "std",
  "galore_optim_per_parameter": false,
  "galore_with_embedding": false,
  "galore_quantization": false,
  "galore_proj_quant": false,
  "galore_proj_bits": 4,
  "galore_proj_group_size": 256,
  "galore_cos_threshold": 0.4,
  "galore_gamma_proj": 2,
  "galore_queue_size": 5,
  "adalora_target_r": 8,
  "adalora_init_r": 12,
  "adalora_tinit": 0,
  "adalora_tfinal": 0,
  "adalora_deltaT": 1,
  "adalora_beta1": 0.85,
  "adalora_beta2": 0.85,
  "adalora_orth_reg_weight": 0.5,
  "llamapro_num_new_blocks": 4,
  "llamapro_num_groups": null,
  "lisa_activated_layers": 0,
  "lisa_step_interval": 20,
  "reft_layer_key": null,
  "reft_layers": null,
  "reft_rank": 4,
  "reft_intervention_type": "LoreftIntervention",
  "reft_args": null,
  "swanlab_token": null,
  "swanlab_project": null,
  "swanlab_workspace": null,
  "swanlab_exp_name": null,
  "swanlab_lark_webhook_url": null,
  "swanlab_lark_secret": null,
  "swanlab_mode": "cloud",
  "add_version": true,
  "create_checkpoint_symlink": false,
  "zero_hpz_partition_size": null,
  "deepspeed_autotp_size": null,
  "early_stop_interval": null,
  "rank": -1,
  "global_world_size": 1,
  "local_world_size": 1,
  "model_suffix": "Qwen2.5-7B-Instruct",
  "model_info": "ModelInfo(model_type='qwen2_5', model_dir='/mnt/workspace/.cache/modelscope/hub/models/Qwen/Qwen2___5-7B-Instruct', torch_dtype=torch.bfloat16, max_model_len=32768, quant_method=None, quant_bits=None, rope_scaling=None, is_moe_model=False, config=None, task_type='causal_lm', num_labels=None)",
  "model_meta": "ModelMeta(model_type='qwen2_5', model_groups=[ModelGroup(models=[Model(ms_model_id='Qwen/Qwen2.5-0.5B-Instruct', hf_model_id='Qwen/Qwen2.5-0.5B-Instruct', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-1.5B-Instruct', hf_model_id='Qwen/Qwen2.5-1.5B-Instruct', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-3B-Instruct', hf_model_id='Qwen/Qwen2.5-3B-Instruct', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-7B-Instruct', hf_model_id='Qwen/Qwen2.5-7B-Instruct', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-14B-Instruct', hf_model_id='Qwen/Qwen2.5-14B-Instruct', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-32B-Instruct', hf_model_id='Qwen/Qwen2.5-32B-Instruct', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-72B-Instruct', hf_model_id='Qwen/Qwen2.5-72B-Instruct', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-0.5B', hf_model_id='Qwen/Qwen2.5-0.5B', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-1.5B', hf_model_id='Qwen/Qwen2.5-1.5B', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-3B', hf_model_id='Qwen/Qwen2.5-3B', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-7B', hf_model_id='Qwen/Qwen2.5-7B', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-14B', hf_model_id='Qwen/Qwen2.5-14B', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-32B', hf_model_id='Qwen/Qwen2.5-32B', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-72B', hf_model_id='Qwen/Qwen2.5-72B', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-0.5B-Instruct-GPTQ-Int4', hf_model_id='Qwen/Qwen2.5-0.5B-Instruct-GPTQ-Int4', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-1.5B-Instruct-GPTQ-Int4', hf_model_id='Qwen/Qwen2.5-1.5B-Instruct-GPTQ-Int4', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-3B-Instruct-GPTQ-Int4', hf_model_id='Qwen/Qwen2.5-3B-Instruct-GPTQ-Int4', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4', hf_model_id='Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4', hf_model_id='Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4', hf_model_id='Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-72B-Instruct-GPTQ-Int4', hf_model_id='Qwen/Qwen2.5-72B-Instruct-GPTQ-Int4', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-0.5B-Instruct-GPTQ-Int8', hf_model_id='Qwen/Qwen2.5-0.5B-Instruct-GPTQ-Int8', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-1.5B-Instruct-GPTQ-Int8', hf_model_id='Qwen/Qwen2.5-1.5B-Instruct-GPTQ-Int8', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-3B-Instruct-GPTQ-Int8', hf_model_id='Qwen/Qwen2.5-3B-Instruct-GPTQ-Int8', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-7B-Instruct-GPTQ-Int8', hf_model_id='Qwen/Qwen2.5-7B-Instruct-GPTQ-Int8', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-14B-Instruct-GPTQ-Int8', hf_model_id='Qwen/Qwen2.5-14B-Instruct-GPTQ-Int8', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-32B-Instruct-GPTQ-Int8', hf_model_id='Qwen/Qwen2.5-32B-Instruct-GPTQ-Int8', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-72B-Instruct-GPTQ-Int8', hf_model_id='Qwen/Qwen2.5-72B-Instruct-GPTQ-Int8', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-0.5B-Instruct-AWQ', hf_model_id='Qwen/Qwen2.5-0.5B-Instruct-AWQ', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-1.5B-Instruct-AWQ', hf_model_id='Qwen/Qwen2.5-1.5B-Instruct-AWQ', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-3B-Instruct-AWQ', hf_model_id='Qwen/Qwen2.5-3B-Instruct-AWQ', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-7B-Instruct-AWQ', hf_model_id='Qwen/Qwen2.5-7B-Instruct-AWQ', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-14B-Instruct-AWQ', hf_model_id='Qwen/Qwen2.5-14B-Instruct-AWQ', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-32B-Instruct-AWQ', hf_model_id='Qwen/Qwen2.5-32B-Instruct-AWQ', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-72B-Instruct-AWQ', hf_model_id='Qwen/Qwen2.5-72B-Instruct-AWQ', model_path=None, ms_revision=None, hf_revision=None)], ignore_patterns=None, requires=None, tags=[]), ModelGroup(models=[Model(ms_model_id='Qwen/Qwen2.5-Coder-0.5B-Instruct', hf_model_id='Qwen/Qwen2.5-Coder-0.5B-Instruct', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-1.5B-Instruct', hf_model_id='Qwen/Qwen2.5-Coder-1.5B-Instruct', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-3B-Instruct', hf_model_id='Qwen/Qwen2.5-Coder-3B-Instruct', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-7B-Instruct', hf_model_id='Qwen/Qwen2.5-Coder-7B-Instruct', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-14B-Instruct', hf_model_id='Qwen/Qwen2.5-Coder-14B-Instruct', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-32B-Instruct', hf_model_id='Qwen/Qwen2.5-Coder-32B-Instruct', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-0.5B', hf_model_id='Qwen/Qwen2.5-Coder-0.5B', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-1.5B', hf_model_id='Qwen/Qwen2.5-Coder-1.5B', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-3B', hf_model_id='Qwen/Qwen2.5-Coder-3B', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-7B', hf_model_id='Qwen/Qwen2.5-Coder-7B', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-14B', hf_model_id='Qwen/Qwen2.5-Coder-14B', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-32B', hf_model_id='Qwen/Qwen2.5-Coder-32B', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-0.5B-Instruct-AWQ', hf_model_id='Qwen/Qwen2.5-Coder-0.5B-Instruct-AWQ', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-1.5B-Instruct-AWQ', hf_model_id='Qwen/Qwen2.5-Coder-1.5B-Instruct-AWQ', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-3B-Instruct-AWQ', hf_model_id='Qwen/Qwen2.5-Coder-3B-Instruct-AWQ', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-7B-Instruct-AWQ', hf_model_id='Qwen/Qwen2.5-Coder-7B-Instruct-AWQ', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-14B-Instruct-AWQ', hf_model_id='Qwen/Qwen2.5-Coder-14B-Instruct-AWQ', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-32B-Instruct-AWQ', hf_model_id='Qwen/Qwen2.5-Coder-32B-Instruct-AWQ', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-0.5B-Instruct-GPTQ-Int4', hf_model_id='Qwen/Qwen2.5-Coder-0.5B-Instruct-GPTQ-Int4', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-0.5B-Instruct-GPTQ-Int8', hf_model_id='Qwen/Qwen2.5-Coder-0.5B-Instruct-GPTQ-Int8', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-1.5B-Instruct-GPTQ-Int4', hf_model_id='Qwen/Qwen2.5-Coder-1.5B-Instruct-GPTQ-Int4', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-1.5B-Instruct-GPTQ-Int8', hf_model_id='Qwen/Qwen2.5-Coder-1.5B-Instruct-GPTQ-Int8', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-3B-Instruct-GPTQ-Int4', hf_model_id='Qwen/Qwen2.5-Coder-3B-Instruct-GPTQ-Int4', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-3B-Instruct-GPTQ-Int8', hf_model_id='Qwen/Qwen2.5-Coder-3B-Instruct-GPTQ-Int8', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-7B-Instruct-GPTQ-Int4', hf_model_id='Qwen/Qwen2.5-Coder-7B-Instruct-GPTQ-Int4', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-7B-Instruct-GPTQ-Int8', hf_model_id='Qwen/Qwen2.5-Coder-7B-Instruct-GPTQ-Int8', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-14B-Instruct-GPTQ-Int4', hf_model_id='Qwen/Qwen2.5-Coder-14B-Instruct-GPTQ-Int4', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-14B-Instruct-GPTQ-Int8', hf_model_id='Qwen/Qwen2.5-Coder-14B-Instruct-GPTQ-Int8', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-32B-Instruct-GPTQ-Int4', hf_model_id='Qwen/Qwen2.5-Coder-32B-Instruct-GPTQ-Int4', model_path=None, ms_revision=None, hf_revision=None), Model(ms_model_id='Qwen/Qwen2.5-Coder-32B-Instruct-GPTQ-Int8', hf_model_id='Qwen/Qwen2.5-Coder-32B-Instruct-GPTQ-Int8', model_path=None, ms_revision=None, hf_revision=None)], ignore_patterns=None, requires=None, tags=['coding']), ModelGroup(models=[Model(ms_model_id='moonshotai/Kimi-Dev-72B', hf_model_id='moonshotai/Kimi-Dev-72B', model_path=None, ms_revision=None, hf_revision=None)], ignore_patterns=None, requires=None, tags=[])], template='qwen2_5', get_function=<function get_model_tokenizer_with_flash_attn at 0x7d1774e919e0>, model_arch=ModelKeys(arch_name='llama', embedding='model.embed_tokens', module_list='model.layers', lm_head='lm_head', q_proj='model.layers.{}.self_attn.q_proj', k_proj='model.layers.{}.self_attn.k_proj', v_proj='model.layers.{}.self_attn.v_proj', o_proj='model.layers.{}.self_attn.o_proj', attention='model.layers.{}.self_attn', mlp='model.layers.{}.mlp', down_proj='model.layers.{}.mlp.down_proj', qkv_proj=None, qk_proj=None, qa_proj=None, qb_proj=None, kv_proj=None, kva_proj=None, kvb_proj=None), architectures=['Qwen2ForCausalLM'], additional_saved_files=[], torch_dtype=None, is_multimodal=False, is_reward=False, task_type=None, ignore_patterns=None, requires=['transformers>=4.37'], tags=[])",
  "model_dir": "/mnt/workspace/.cache/modelscope/hub/models/Qwen/Qwen2___5-7B-Instruct",
  "hub": "<class 'swift.hub.hub.MSHub'>",
  "evaluation_strategy": "steps",
  "training_args": "Seq2SeqTrainingArguments(output_dir='/workspace/verl/output/v0-20250926-114832', overwrite_output_dir=False, do_train=False, do_eval=False, do_predict=False, eval_strategy=<IntervalStrategy.NO: 'no'>, prediction_loss_only=False, per_device_train_batch_size=1, per_device_eval_batch_size=1, per_gpu_train_batch_size=None, per_gpu_eval_batch_size=None, gradient_accumulation_steps=16, eval_accumulation_steps=None, eval_delay=0, torch_empty_cache_steps=None, learning_rate=0.0001, weight_decay=0.1, adam_beta1=0.9, adam_beta2=0.95, adam_epsilon=1e-08, max_grad_norm=1.0, num_train_epochs=1.0, max_steps=-1, lr_scheduler_type=<SchedulerType.COSINE: 'cosine'>, lr_scheduler_kwargs=None, warmup_ratio=0.05, warmup_steps=0, log_level='passive', log_level_replica='warning', log_on_each_node=True, logging_dir='/workspace/verl/output/v0-20250926-114832/runs', logging_strategy=<IntervalStrategy.STEPS: 'steps'>, logging_first_step=True, logging_steps=5, logging_nan_inf_filter=True, save_strategy=<SaveStrategy.STEPS: 'steps'>, save_steps=50, save_total_limit=2, save_safetensors=True, save_on_each_node=False, save_only_model=False, restore_callback_states_from_checkpoint=False, no_cuda=False, use_cpu=False, use_mps_device=False, seed=42, data_seed=42, jit_mode_eval=False, use_ipex=False, bf16=True, fp16=False, fp16_opt_level='O1', half_precision_backend='auto', bf16_full_eval=False, fp16_full_eval=False, tf32=None, local_rank=0, ddp_backend=None, tpu_num_cores=None, tpu_metrics_debug=False, debug=[], dataloader_drop_last=False, eval_steps=50.0, dataloader_num_workers=4, dataloader_prefetch_factor=10, past_index=-1, run_name='/workspace/verl/output/v0-20250926-114832', disable_tqdm=False, remove_unused_columns=False, label_names=None, load_best_model_at_end=False, metric_for_best_model='loss', greater_is_better=False, ignore_data_skip=False, fsdp=[], fsdp_min_num_params=0, fsdp_config={'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}, fsdp_transformer_layer_cls_to_wrap=None, accelerator_config=AcceleratorConfig(split_batches=False, dispatch_batches=False, even_batches=True, use_seedable_sampler=True, non_blocking=False, gradient_accumulation_kwargs=None, use_configured_state=False), parallelism_config=None, deepspeed=None, label_smoothing_factor=0.0, optim=<OptimizerNames.ADAMW_TORCH: 'adamw_torch'>, optim_args=None, adafactor=False, group_by_length=False, length_column_name='length', report_to=['tensorboard'], ddp_find_unused_parameters=None, ddp_bucket_cap_mb=None, ddp_broadcast_buffers=None, dataloader_pin_memory=True, dataloader_persistent_workers=False, skip_memory_metrics=True, use_legacy_prediction_loop=False, push_to_hub=False, resume_from_checkpoint=None, hub_model_id=None, hub_strategy=<HubStrategy.EVERY_SAVE: 'every_save'>, hub_token=None, hub_private_repo=None, hub_always_push=False, hub_revision=None, gradient_checkpointing=True, gradient_checkpointing_kwargs=None, include_inputs_for_metrics=False, include_for_metrics=[], eval_do_concat_batches=True, fp16_backend='auto', push_to_hub_model_id=None, push_to_hub_organization=None, push_to_hub_token=None, mp_parameters='', auto_find_batch_size=False, full_determinism=False, torchdynamo=None, ray_scope='last', ddp_timeout=18000000, torch_compile=False, torch_compile_backend=None, torch_compile_mode=None, include_tokens_per_second=None, include_num_input_tokens_seen=None, neftune_noise_alpha=None, optim_target_modules=None, batch_eval_metrics=False, eval_on_start=False, use_liger_kernel=False, liger_kernel_config=None, eval_use_gather_object=False, average_tokens_across_devices=None, sortish_sampler=False, predict_with_generate=False, generation_max_length=None, generation_num_beams=None, generation_config=None, tuner_backend='peft', vit_gradient_checkpointing=True, router_aux_loss_coef=0.0, enable_dft_loss=False, enable_channel_loss=False, check_model=True, acc_strategy='token', train_dataloader_shuffle=True, max_epochs=None, aligner_lr=None, vit_lr=None, use_logits_to_keep=None, ds3_gather_for_generation=True, resume_only_model=False, optimizer=None, loss_type=None, metric=None, eval_use_evalscope=False, eval_dataset=[], eval_dataset_args=None, eval_limit=None, eval_generation_config=None, extra_eval_args=None, use_flash_ckpt=False, sft_alpha=0, train_type='lora', local_repo_path=None, galore_config=None)"
}
