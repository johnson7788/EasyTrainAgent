# 测试合并后的模型
## 显卡1用于训练时的推理，自动同步参数，使用SFT过后的模型
export CUDA_VISIBLE_DEVICES=1 \
swift rollout \
    --model ./output/merged_qwen3 \
    --vllm_use_async_engine true \
    --external_plugins ./plugin.py \
    --multi_turn_scheduler mcp_call_scheduler \
    --vllm_max_model_len 4096 \
    --vllm_gpu_memory_utilization 0.8 \
    --max_turns 5
## 测试tool_call_scheduler和Qwen/Qwen2.5-3B-Instruct
swift rollout \
    --model Qwen/Qwen2.5-3B-Instruct \
    --vllm_use_async_engine true \
    --external_plugins ./plugin.py \
    --multi_turn_scheduler tool_call_scheduler \
    --vllm_max_model_len 4096 \
    --vllm_gpu_memory_utilization 0.8 \
    --max_turns 5

# 目录
```
grpo_main.py  # 训练GRPO代码，会使用dataset.py加载数据，同时也会使用plugin.py中LLMRulerReward作为奖励函数
start_rollout.py  # 启动VLLM的rollout，会使用plugin.py中的MCPCallScheduler作为MCP工具
dataset.py  # 加载自定义的数据，这里加载本地的train.jsonl数据
plugin.py  # 自定义的MCP调用插件和使用LLM进行GRPO的奖励函数
my_ruler.py  # 自定义的LLM奖励函数
mcp_client.py # MCP的客户端调用工具,被plugin.py中的MCPCallScheduler使用
mcp_config.json  # 使用哪些的MCP工具
mcp_config_load.py # 加载mcp_config.json，被plugin.py中的MCPCallScheduler使用
```

## 运行GRPO训练
1) python energy_services.py 启动step1中的MCP server
2) cp env_template .env  #配置ruler模型
3)export CUDA_VISIBLE_DEVICES=1; python start_rollout.py  #在显卡1上启动vllm模型的rollout
4)export CUDA_VISIBLE_DEVICES=2; python grpo_main.py  #在显卡2上启动GRPO模型训练

## Debug方式
1） 在容器里面运行[start_sshd.sh](../tools/start_sshd.sh)
2） 然后使用pycharm的ssh连接容器
3） 运行grpo_main.py进行debug