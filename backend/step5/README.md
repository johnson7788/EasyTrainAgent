# 需要先启动MCP server
```bash
cd step1
python energy_services.py
```

# 启动微调后的模型
```bash
cd step5
swift deploy \
    --adapters ../output/v1-20250927-221821/checkpoint-2 \
    --infer_backend pt \
    --temperature 0 \
    --max_new_tokens 2048 \
    --served_model_name 'mylora-model'
```

# 启动Agent
```
更改.env，更改模型供应商和模型配置信息
MODEL_PROVIDER=swift
LLM_MODEL=mylora-model
SWIFT_API_URL=http://127.0.0.1:8000/v1
SWIFT_API_KEY=empty
```

# 测试Agent使用mcp
```
cd step3
python a2a_client.py
```

## 日志
1) 模型推理端的日志
[sft.log](sft.log)

2) Agent的日志
[agent.log](agent.log)

3) 客户端日志
[client.log](client.log)
