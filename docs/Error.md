# 报错，可以这样， export CUDA_VISIBLE_DEVICES=1， 一定要加export，否则就会报错
[INFO:swift] Setting args.lazy_tokenize: False
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/swift/cli/rlhf.py", line 5, in <module>
    rlhf_main()
  File "/usr/local/lib/python3.11/site-packages/swift/llm/train/rlhf.py", line 200, in rlhf_main
    return SwiftRLHF(args).main()
           ^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/swift/llm/train/sft.py", line 27, in __init__
    super().__init__(args)
  File "/usr/local/lib/python3.11/site-packages/swift/llm/base.py", line 19, in __init__
    self.args = self._parse_args(args)
                ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/swift/llm/base.py", line 31, in _parse_args
    args, remaining_argv = parse_args(self.args_class, args)
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/swift/utils/utils.py", line 152, in parse_args
    args, remaining_args = parser.parse_args_into_dataclasses(argv, return_remaining_strings=True)
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/transformers/hf_argparser.py", line 358, in parse_args_into_dataclasses
    obj = dtype(**inputs)
          ^^^^^^^^^^^^^^^
  File "<string>", line 435, in __init__
  File "/usr/local/lib/python3.11/site-packages/swift/llm/argument/rlhf_args.py", line 135, in __post_init__
    TrainArguments.__post_init__(self)
  File "/usr/local/lib/python3.11/site-packages/swift/llm/argument/train_args.py", line 168, in __post_init__
    self._init_deepspeed()
  File "/usr/local/lib/python3.11/site-packages/swift/llm/argument/train_args.py", line 186, in _init_deepspeed
    raise ValueError('DeepSpeed is not compatible with `device_map`. '
ValueError: DeepSpeed is not compatible with `device_map`. n_gpu: 3, local_world_size: 1.


[rank0]: Traceback (most recent call last):
[rank0]:   File "/usr/local/lib/python3.11/site-packages/swift/cli/rlhf.py", line 5, in <module>
[rank0]:     rlhf_main()
[rank0]:   File "/usr/local/lib/python3.11/site-packages/swift/llm/train/rlhf.py", line 200, in rlhf_main
[rank0]:     return SwiftRLHF(args).main()
[rank0]:            ^^^^^^^^^^^^^^^
[rank0]:   File "/usr/local/lib/python3.11/site-packages/swift/llm/train/sft.py", line 27, in __init__
[rank0]:     super().__init__(args)
[rank0]:   File "/usr/local/lib/python3.11/site-packages/swift/llm/base.py", line 19, in __init__
[rank0]:     self.args = self._parse_args(args)
[rank0]:                 ^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/usr/local/lib/python3.11/site-packages/swift/llm/base.py", line 31, in _parse_args
[rank0]:     args, remaining_argv = parse_args(self.args_class, args)
[rank0]:                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/usr/local/lib/python3.11/site-packages/swift/utils/utils.py", line 152, in parse_args
[rank0]:     args, remaining_args = parser.parse_args_into_dataclasses(argv, return_remaining_strings=True)
[rank0]:                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/usr/local/lib/python3.11/site-packages/transformers/hf_argparser.py", line 358, in parse_args_into_dataclasses
[rank0]:     obj = dtype(**inputs)
[rank0]:           ^^^^^^^^^^^^^^^
[rank0]:   File "<string>", line 435, in __init__
[rank0]:   File "/usr/local/lib/python3.11/site-packages/swift/llm/argument/rlhf_args.py", line 137, in __post_init__
[rank0]:     self._check_grpo()
[rank0]:   File "/usr/local/lib/python3.11/site-packages/swift/llm/argument/rlhf_args.py", line 299, in _check_grpo
[rank0]:     raise ValueError('GRPO with vLLM is not compatible with `device_map`. '
[rank0]: ValueError: GRPO with vLLM is not compatible with `device_map`. Please set NPROC_PER_NODE equal to num_processes.



# 如果在swift rollout中使用multi_turn_scheduler，但是没有指定external_plugins的位置，那么rollout就会卡住，无法启动

# 代码报错，是grpo_main中的max_length和max_completion_length的长度过短导致的，增加长度
(EngineCore_0 pid=461106) INFO 09-30 17:34:46 [block_pool.py:280] Successfully reset prefix cache
INFO:     127.0.0.1:38354 - "POST /reset_prefix_cache/ HTTP/1.1" 200 OK
  0%|                                                    | 0/32 [00:00<?, ?it/s][WARNING:swift] max_model_len(2048) - num_tokens(1605) < max_tokens(1024). Setting max_tokens: 443
[WARNING:swift] max_model_len(2048) - num_tokens(5221) < max_tokens(1024). Setting max_tokens: -3173
[WARNING:swift] max_model_len(2048) - num_tokens(1605) < max_tokens(1024). Setting max_tokens: 443
[ERROR:swift] Method execution failed: async_infer
Traceback (most recent call last):
  File "/workspace/verl/ms-swift/swift/llm/infer/rollout.py", line 144, in async_llm_worker
    result = await method(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/plugin/multi_turn.py", line 90, in async_infer
    results = await self.infer_engine._batch_infer_stream(tasks, request_config.stream, use_tqdm, None)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/grpo_vllm_engine.py", line 155, in _batch_infer_stream
    return await self.batch_run(new_tasks)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/infer_engine.py", line 114, in batch_run
    return await asyncio.gather(*tasks)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/tasks.py", line 277, in __step
    result = coro.send(None)
             ^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/grpo_vllm_engine.py", line 145, in _new_run
    res = await task
          ^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/plugin/multi_turn.py", line 84, in _infer_async_single
    return await self.run(infer_request, request_config, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/plugin/multi_turn.py", line 229, in run
    response: 'ChatCompletionResponse' = await self.infer_engine.infer_async(
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/vllm_engine.py", line 743, in infer_async
    generation_config = self._prepare_generation_config(request_config)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/vllm_engine.py", line 406, in _prepare_generation_config
    res = SamplingParams(**kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/vllm/sampling_params.py", line 342, in __post_init__
    self._verify_args()
  File "/usr/local/lib/python3.11/site-packages/vllm/sampling_params.py", line 397, in _verify_args
    raise ValueError(
ValueError: max_tokens must be at least 1, got -3173.
[WARNING:swift] max_model_len(2048) - num_tokens(1603) < max_tokens(1024). Setting max_tokens: 445
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/uvicorn/protocols/http/httptools_impl.py", line 409, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/applications.py", line 113, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 186, in __call__
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 716, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 736, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 290, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 78, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 75, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 302, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 213, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/rollout.py", line 386, in infer
    all_outputs = list(chain.from_iterable(all_outputs))  # from list of list to single list
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'NoneType' object is not iterable

# 训练数据问题，在训练到某些数据时发生了错误,请使用少量训练数据试试，例如前10条数据。
[INFO:swift] use_reentrant: True
Trainer.tokenizer is now deprecated. You should use Trainer.processing_class instead.
[INFO:swift] The logging file will be saved in: /workspace/verl/docs/ms-swift/tools/output/mcp_agent/v5-20251009-115936/logging.jsonl
The tokenizer has new PAD/BOS/EOS tokens that differ from the model config and generation config. The model config and generation config were aligned accordingly, being updated with the tokenizer's values. Updated tokens: {'bos_token_id': None}.
WARNING:accelerate.accelerator:Gradient accumulation steps mismatch: GradientAccumulationPlugin has 1, DeepSpeed config has 8. Using DeepSpeed's value.
Parameter Offload - Persistent parameters statistics: param_count = 365, numel = 2129920
Train:   0%|                                                                                                              | 0/9 [00:00<?, ?it/s]/usr/local/lib/python3.11/site-packages/torch/utils/checkpoint.py:86: UserWarning: None of the inputs have requires_grad=True. Gradients will be None
  warnings.warn(
[2025-10-09 12:01:31,035] [WARNING] [stage3.py:2160:step] 1 pytorch allocator cache flushes since last step. this happens when there is high memory pressure and is detrimental to performance. if this is happening frequently consider adjusting settings to reduce memory consumption. If you are unable to make the cache flushes go away consider adding get_accelerator().empty_cache() calls in your training loop to ensure that all ranks flush their caches at the same time
{'loss': 0.0, 'grad_norm': 0.0, 'learning_rate': 5e-07, 'reward': 0.0, 'reward_std': 0.0, 'frac_reward_zero_std': 1.0, 'rewards/Format/mean': 0.0, 'rewards/Format/std': 0.0, 'completions/mean_length': 2067.25, 'completions/min_length': 1091.0, 'completions/max_length': 3584.0, 'completions/clipped_ratio': 0.125, 'num_turns': 5.0, 'kl': 0.0, 'clip_ratio/low_mean': 0.0, 'clip_ratio/low_min': 0.0, 'clip_ratio/high_mean': 0.0, 'clip_ratio/high_max': 0.0, 'clip_ratio/region_mean': 0.0, 'epoch': 0.11, 'global_step/max_steps': '1/9', 'percentage': '11.11%', 'elapsed_time': '1m 35s', 'remaining_time': '12m 44s', 'memory(GiB)': 21.86, 'train_speed(iter/s)': 0.010467}
{'loss': 0.0, 'grad_norm': 0.0, 'learning_rate': 4.8e-07, 'reward': 0.0, 'reward_std': 0.0, 'frac_reward_zero_std': 1.0, 'rewards/Format/mean': 0.0, 'rewards/Format/std': 0.0, 'completions/mean_length': 2774.125, 'completions/min_length': 951.0, 'completions/max_length': 4846.0, 'completions/clipped_ratio': 0.0, 'num_turns': 5.0, 'kl': 0.0, 'clip_ratio/low_mean': 0.0, 'clip_ratio/low_min': 0.0, 'clip_ratio/high_mean': 0.0, 'clip_ratio/high_max': 0.0, 'clip_ratio/region_mean': 0.0, 'epoch': 0.22, 'global_step/max_steps': '2/9', 'percentage': '22.22%', 'elapsed_time': '2m 46s', 'remaining_time': '9m 43s', 'memory(GiB)': 21.86, 'train_speed(iter/s)': 0.012004}
{'loss': 0.0, 'grad_norm': 0.0, 'learning_rate': 4.3e-07, 'reward': 0.0, 'reward_std': 0.0, 'frac_reward_zero_std': 1.0, 'rewards/Format/mean': 0.0, 'rewards/Format/std': 0.0, 'completions/mean_length': 1363.125, 'completions/min_length': 1194.0, 'completions/max_length': 1632.0, 'completions/clipped_ratio': 0.0, 'num_turns': 5.0, 'kl': 0.0, 'clip_ratio/low_mean': 0.0, 'clip_ratio/low_min': 0.0, 'clip_ratio/high_mean': 0.0, 'clip_ratio/high_max': 0.0, 'clip_ratio/region_mean': 0.0, 'epoch': 0.33, 'global_step/max_steps': '3/9', 'percentage': '33.33%', 'elapsed_time': '3m 23s', 'remaining_time': '6m 47s', 'memory(GiB)': 21.86, 'train_speed(iter/s)': 0.01474}
{'loss': 0.0, 'grad_norm': 0.0, 'learning_rate': 3.5e-07, 'reward': 0.0, 'reward_std': 0.0, 'frac_reward_zero_std': 1.0, 'rewards/Format/mean': 0.0, 'rewards/Format/std': 0.0, 'completions/mean_length': 1473.125, 'completions/min_length': 1219.0, 'completions/max_length': 1738.0, 'completions/clipped_ratio': 0.0, 'num_turns': 5.0, 'kl': 0.0, 'clip_ratio/low_mean': 0.0, 'clip_ratio/low_min': 0.0, 'clip_ratio/high_mean': 0.0, 'clip_ratio/high_max': 0.0, 'clip_ratio/region_mean': 0.0, 'epoch': 0.44, 'global_step/max_steps': '4/9', 'percentage': '44.44%', 'elapsed_time': '4m 0s', 'remaining_time': '5m 0s', 'memory(GiB)': 21.86, 'train_speed(iter/s)': 0.016664}
{'loss': 0.0, 'grad_norm': 0.0, 'learning_rate': 2.5e-07, 'reward': 0.0, 'reward_std': 0.0, 'frac_reward_zero_std': 1.0, 'rewards/Format/mean': 0.0, 'rewards/Format/std': 0.0, 'completions/mean_length': 1988.375, 'completions/min_length': 1094.0, 'completions/max_length': 3110.0, 'completions/clipped_ratio': 0.0, 'num_turns': 5.0, 'kl': 0.0, 'clip_ratio/low_mean': 0.0, 'clip_ratio/low_min': 0.0, 'clip_ratio/high_mean': 0.0, 'clip_ratio/high_max': 0.0, 'clip_ratio/region_mean': 0.0, 'epoch': 0.56, 'global_step/max_steps': '5/9', 'percentage': '55.56%', 'elapsed_time': '4m 49s', 'remaining_time': '3m 51s', 'memory(GiB)': 21.86, 'train_speed(iter/s)': 0.01725}
{'loss': 0.0, 'grad_norm': 0.0, 'learning_rate': 1.5e-07, 'reward': 0.0, 'reward_std': 0.0, 'frac_reward_zero_std': 1.0, 'rewards/Format/mean': 0.0, 'rewards/Format/std': 0.0, 'completions/mean_length': 1257.0, 'completions/min_length': 1074.0, 'completions/max_length': 1422.0, 'completions/clipped_ratio': 0.0, 'num_turns': 5.0, 'kl': 0.0, 'clip_ratio/low_mean': 0.0, 'clip_ratio/low_min': 0.0, 'clip_ratio/high_mean': 0.0, 'clip_ratio/high_max': 0.0, 'clip_ratio/region_mean': 0.0, 'epoch': 0.67, 'global_step/max_steps': '6/9', 'percentage': '66.67%', 'elapsed_time': '5m 20s', 'remaining_time': '2m 40s', 'memory(GiB)': 21.86, 'train_speed(iter/s)': 0.018726}
Train:  67%|████████████████████████████████████████████████████████████████████                                  | 6/9 [05:20<02:11, 43.90s/it][INFO:swift] last_model_checkpoint: None
[INFO:swift] best_model_checkpoint: None
[INFO:swift] images_dir: /workspace/verl/docs/ms-swift/tools/output/mcp_agent/v5-20251009-115936/images
[rank0]: Traceback (most recent call last):
[rank0]:   File "/workspace/verl/docs/ms-swift/tools/grpo_main.py", line 79, in <module>
[rank0]:     rlhf_main(args)
[rank0]:   File "/workspace/verl/ms-swift/swift/llm/train/rlhf.py", line 217, in rlhf_main
[rank0]:     return SwiftRLHF(args).main()
[rank0]:            ^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/llm/base.py", line 49, in main
[rank0]:     result = self.run()
[rank0]:              ^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/llm/train/sft.py", line 195, in run
[rank0]:     return self.train(trainer)
[rank0]:            ^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/llm/train/sft.py", line 243, in train
[rank0]:     trainer.train(trainer.args.resume_from_checkpoint)
[rank0]:   File "/workspace/verl/ms-swift/swift/trainers/mixin.py", line 674, in train
[rank0]:     res = super().train(*args, **kwargs)
[rank0]:           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/usr/local/lib/python3.11/site-packages/transformers/trainer.py", line 2328, in train
[rank0]:     return inner_training_loop(
[rank0]:            ^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/usr/local/lib/python3.11/site-packages/transformers/trainer.py", line 2672, in _inner_training_loop
[rank0]:     tr_loss_step = self.training_step(model, inputs, num_items_in_batch)
[rank0]:                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/trainers/rlhf_trainer/grpo_trainer.py", line 1974, in training_step
[rank0]:     return super().training_step(model, inputs, num_items_in_batch)
[rank0]:            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/usr/local/lib/python3.11/site-packages/transformers/trainer.py", line 4003, in training_step
[rank0]:     inputs = self._prepare_inputs(inputs)
[rank0]:              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/trainers/rlhf_trainer/utils.py", line 170, in wrapper
[rank0]:     return func(self, *args, **kwargs)
[rank0]:            ^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/trainers/rlhf_trainer/grpo_trainer.py", line 436, in _prepare_inputs
[rank0]:     generation_batch = self._generate_and_score_completions(generation_batch)
[rank0]:                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/trainers/rlhf_trainer/utils.py", line 170, in wrapper
[rank0]:     return func(self, *args, **kwargs)
[rank0]:            ^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/trainers/rlhf_trainer/grpo_trainer.py", line 845, in _generate_and_score_completions
[rank0]:     inputs = self._generate_completions(inputs)
[rank0]:              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/trainers/rlhf_trainer/grpo_trainer.py", line 826, in _generate_completions
[rank0]:     results = self._fast_infer(inputs)
[rank0]:               ^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/trainers/rlhf_trainer/grpo_trainer.py", line 808, in _fast_infer
[rank0]:     outputs = self._infer_single_or_multi_turn(inputs, self.request_config)
[rank0]:               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/trainers/rlhf_trainer/grpo_trainer.py", line 714, in _infer_single_or_multi_turn
[rank0]:     rollout_outputs: List[RolloutOutput] = self._rollout(inputs, request_config, is_global_inputs)
[rank0]:                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/trainers/rlhf_trainer/grpo_trainer.py", line 644, in _rollout
[rank0]:     rollout_outputs = self._server_rollout(inputs, request_config, is_global_inputs)
[rank0]:                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/trainers/rlhf_trainer/grpo_trainer.py", line 2342, in _server_rollout
[rank0]:     all_outputs: List[RolloutOutput] = self._engine_infer(
[rank0]:                                        ^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/trainers/rlhf_trainer/grpo_trainer.py", line 1996, in _engine_infer
[rank0]:     res = self.vllm_client.infer([asdict(req) for req in infer_requests],
[rank0]:           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[rank0]:   File "/workspace/verl/ms-swift/swift/trainers/rlhf_trainer/vllm_client.py", line 171, in infer
[rank0]:     raise RuntimeError(f'Multiple errors: {all_errors}')
[rank0]: RuntimeError: Multiple errors: [Exception('Server 0 failed: 500, Internal Server Error')]
Train:  67%|████████████████████████████████████████████████████████████████████                                  | 6/9 [05:34<02:47, 55.74s/it]
sys:1: DeprecationWarning: builtin type swigvarlink has no __module__ attribute
在rollout处出现的报错如下
(EngineCore_0 pid=16439) INFO 10-09 15:51:57 [block_pool.py:280] Successfully reset prefix cache
INFO:     127.0.0.1:34776 - "POST /reset_prefix_cache/ HTTP/1.1" 200 OK
  0%|                                                                                                                     | 0/8 [00:00<?, ?it/s][WARNING:swift] max_model_len(8096) - num_tokens(12052) < max_tokens(2048). Setting max_tokens: -3956
[WARNING:swift] max_model_len(8096) - num_tokens(12052) < max_tokens(2048). Setting max_tokens: -3956
[ERROR:swift] Method execution failed: async_infer
Traceback (most recent call last):
  File "/workspace/verl/ms-swift/swift/llm/infer/rollout.py", line 144, in async_llm_worker
    result = await method(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/plugin/multi_turn.py", line 90, in async_infer
    results = await self.infer_engine._batch_infer_stream(tasks, request_config.stream, use_tqdm, None)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/grpo_vllm_engine.py", line 155, in _batch_infer_stream
    return await self.batch_run(new_tasks)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/infer_engine.py", line 114, in batch_run
    return await asyncio.gather(*tasks)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/tasks.py", line 277, in __step
    result = coro.send(None)
             ^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/grpo_vllm_engine.py", line 145, in _new_run
    res = await task
          ^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/plugin/multi_turn.py", line 84, in _infer_async_single
    return await self.run(infer_request, request_config, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/plugin/multi_turn.py", line 229, in run
    response: 'ChatCompletionResponse' = await self.infer_engine.infer_async(
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/vllm_engine.py", line 743, in infer_async
    generation_config = self._prepare_generation_config(request_config)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/vllm_engine.py", line 406, in _prepare_generation_config
    res = SamplingParams(**kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/vllm/sampling_params.py", line 342, in __post_init__
    self._verify_args()
  File "/usr/local/lib/python3.11/site-packages/vllm/sampling_params.py", line 397, in _verify_args
    raise ValueError(
ValueError: max_tokens must be at least 1, got -3956.

INFO:     127.0.0.1:34776 - "POST /infer/ HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/uvicorn/protocols/http/httptools_impl.py", line 409, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/applications.py", line 113, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 186, in __call__
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 716, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 736, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 290, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 78, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 75, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 302, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 213, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/rollout.py", line 386, in infer
    all_outputs = list(chain.from_iterable(all_outputs))  # from list of list to single list
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'NoneType' object is not iterable




# tool没在message中存在
❌ Failed to call tool get_lng_demand from http://localhost:9000/sse: Unknown tool: get_lng_demand
[INFO:swift] 现在的上下文长度为: 197
[INFO:swift] 现在的上下文长度为: 3695
[INFO:swift] 现在的上下文长度为: 127
[INFO:swift] 现在的上下文长度为: 127
[INFO:swift] 现在的上下文长度为: 127
[INFO:swift] 现在的上下文长度为: 127
❌ Failed to call tool get_daily_demand from http://localhost:9000/sse: Unknown tool: get_daily_demand
[INFO:swift] 现在的上下文长度为: 292
[WARNING:swift] Truncating conversation (total=7249)
[INFO:swift] 现在的上下文长度为: 7067
[ERROR:swift] Method execution failed: async_infer
Traceback (most recent call last):
  File "/workspace/verl/ms-swift/swift/llm/infer/rollout.py", line 144, in async_llm_worker
    result = await method(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/plugin/multi_turn.py", line 90, in async_infer
    results = await self.infer_engine._batch_infer_stream(tasks, request_config.stream, use_tqdm, None)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/grpo_vllm_engine.py", line 155, in _batch_infer_stream
    return await self.batch_run(new_tasks)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/infer_engine.py", line 114, in batch_run
    return await asyncio.gather(*tasks)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/tasks.py", line 279, in __step
    result = coro.throw(exc)
             ^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/grpo_vllm_engine.py", line 145, in _new_run
    res = await task
          ^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/plugin/multi_turn.py", line 84, in _infer_async_single
    return await self.run(infer_request, request_config, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/plugin/multi_turn.py", line 229, in run
    response: 'ChatCompletionResponse' = await self.infer_engine.infer_async(
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/infer_engine/vllm_engine.py", line 741, in infer_async
    inputs = await loop.run_in_executor(None, template.encode, infer_request, True)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/futures.py", line 287, in __await__
    yield self  # This tells Task to wait for completion.
    ^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/tasks.py", line 349, in __wakeup
    future.result()
  File "/usr/local/lib/python3.11/asyncio/futures.py", line 203, in result
    raise self._exception.with_traceback(self._exception_tb)
  File "/usr/local/lib/python3.11/concurrent/futures/thread.py", line 58, in run
    result = self.fn(*self.args, **self.kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/torch/utils/_contextlib.py", line 116, in decorate_context
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/template/base.py", line 497, in encode
    encoded = self._encode_truncated(chosen)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/template/base.py", line 1189, in _encode_truncated
    encoded = Template._encode(self, inputs)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/template/base.py", line 1226, in _encode
    self._swift_encode(inputs) if template_backend == 'swift' else self._jinja_encode(inputs))
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/template/base.py", line 1091, in _swift_encode
    assert response_role in {'assistant'}, f'response_role: "{response_role}"'
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: response_role: "tool"

INFO:     127.0.0.1:44672 - "POST /infer/ HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/uvicorn/protocols/http/httptools_impl.py", line 409, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/applications.py", line 113, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 186, in __call__
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 716, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 736, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 290, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 78, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 75, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 302, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 213, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/verl/ms-swift/swift/llm/infer/rollout.py", line 386, in infer
    all_outputs = list(chain.from_iterable(all_outputs))  # from list of list to single list
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'NoneType' object is not iterable