# EasyTrainAgent - 后端

欢迎使用 EasyTrainAgent！本项目的目标是帮助开发者轻松训练和部署自己的领域专属智能体（Agent）。通过遵循以下步骤，你将能够利用自己的工具（API）和语言模型，构建一个强大的智能体。

## 目录结构

```
.
├── README.md                # 本文档
├── requirements.txt         # 项目依赖
├── env_template             # 环境变量模板
├── questions.txt            # 生成的用于SFT数据的问题列表
├── train.jsonl              # 生成的SFT训练数据
├── generate_questions.py    # 步骤2: 根据MCP工具生成领域相关问题
├── generate_train_data.py   # 步骤3: 根据生成的生成问题调用Agent生成SFT训练数据
├── train_tool_sft.py        # 步骤4: 进行监督微调 (SFT)
├── original_model.py        # 测试未经训练的原始模型
├── inference_tool_sft.py    # 步骤5: 测试SFT微调后的模型
├── merge_lora.py            # 步骤6和步骤9: 合并LoRA权重
├── main_api.py              # 后端的API服务
├── test_api.py              # 测试部署的API
├── a2a_agent/               # Agent模块，用于与工具服务器交互并生成对话数据
│   └── main.py              # 运行Agent服务
├── mcpserver/               # 工具服务器示例 (MCP)
│   └── energy_services.py   # 一个实现自定义工具的示例
└── rl_train/                # 强化学习 (RL) 训练模块
    └── train.py             # 步骤7: 运行RL训练
    └── model_test.py        # 步骤8: 测试训练后的RL模型
```

## 准备工作

在开始之前，请完成以下环境准备步骤。
服务器准备：
[prepare.md](docs/prepare.md)

**1. 安装依赖**

本项目依赖于特定的 Python 包。我们建议在一个虚拟环境中进行安装，以避免与其他项目冲突。

```bash
# 安装所有必要的依赖
pip install -r requirements.txt
```

**2. 配置环境变量**

你需要一个语言模型（LLM）的 API Key 来生成训练数据和进行模型评估。请将 `env_template` 文件复制为 `.env`，并填入你的 API Key。

```bash
# 复制环境变量文件
cp env_template .env

# 编辑 .env 文件并填入你的密钥
# 例如: OPENAI_API_KEY="sk-..."
```

## 训练流程

请按照以下步骤，一步步完成从数据准备到模型部署的全过程。

### 步骤 1: 实现并运行你的工具服务器 (MCP)

智能体的核心是与外部工具进行交互。你需要将你的工具封装成一个 API 服务。

1.  **实现工具**：参考 `mcpserver/energy_services.py` 文件，创建你自己的工具逻辑。每个工具都应该是一个独立的函数，并通过 FastAPI 的路由暴露为 API 端点。
2.  **运行服务**：启动你的工具服务器。

    ```bash
    cd mcpserver
    python energy_services.py
    ```

3.  **测试工具**：你可以使用 `rl_train/mcp_client.py` 来测试你的工具服务器是否正常工作。

### 步骤 2: 生成领域问题

为了让模型学会使用你的工具，我们需要生成一批与工具功能相关的自然语言问题。

```bash
# 生成20条问题，并保存到 questions.txt
python generate_questions.py -n 20 -o questions.txt
```

### 步骤 3: 生成 SFT 训练数据

此步骤将利用 `a2a_agent` 模块，调用你的工具服务器 (MCP) 和语言模型，将上一步生成的问题转化为多轮对话格式的 SFT 训练数据。

1.  **启动 Agent 服务**：

    ```bash
    cd a2a_agent
    python main.py
    ```

2.  **生成训练数据**：此脚本会读取 `questions.txt`，通过 Agent 服务与工具交互，最终生成 `train.jsonl` 文件。

    ```bash
    # 回到 backend 根目录
    cd ..
    python generate_train_data.py
    ```

### 步骤 4: 监督微调 (SFT)

使用上一步生成的 `train.jsonl` 文件对基础模型进行微调，使其具备调用工具的能力。

```bash
python train_tool_sft.py \
  --data_path ./train.jsonl \
  --epochs 3 \
  --lr 2e-4 \
  --batch_size 8 \
  --grad_accum 2 \
  --wandb_project easy-train-sft
```

训练完成后，LoRA 权重将保存在 `./lora_model` 目录中。
```
ls lora_model/
README.md            adapter_model.safetensors  chat_template.jinja  special_tokens_map.json  tokenizer_config.json
adapter_config.json  added_tokens.json          merges.txt           tokenizer.json           vocab.json
```

### 步骤 5: 测试 SFT 模型

在合并权重之前，你可以使用 `inference_tool_sft.py` 脚本来测试微调后模型的工具调用能力。

```bash
python inference_tool_sft.py \
  --model ./lora_model \
  --base_model unsloth/Qwen3-4B-Instruct-2507 \
  --query "山西2024年5月的LNG到岸价格是多少？"
```

### 步骤 6: 合并 LoRA 权重

将训练好的 LoRA 权重与基础模型合并，生成一个完整的、可直接部署的模型。

```bash
# 回到 backend 根目录
cd ..
python merge_lora.py  --base_id unsloth/Qwen3-4B-Instruct-2507  --lora_dir ./lora_model   --out_dir ./qwen3-4b-sft
```

### 步骤 7: 强化学习 (RL) 训练

为了进一步优化模型的性能，你可以选择进行强化学习训练。

```bash
cd rl_train
python train.py
```

### 步骤 8: 合并 LoRA 权重

将训练好的 LoRA 权重与基础模型合并，生成一个完整的、可直接部署的模型。

```bash
# 回到 backend 根目录
cd ..
python merge_lora.py  --base_id unsloth/Qwen3-4B-Instruct-2507  --lora_dir /workspace/verl/ART/.art/content-training/models/ppt-content06/checkpoints/0002   --out_dir ./qwen3-4b-sft
```

合并后的模型将保存在一个新目录中（例如 `qwen3-4b-merged`）。

### 步骤 9: 部署与测试

使用 VLLM 框架将合并后的模型部署为 OpenAI 兼容的 API 服务。

1.  **启动 API 服务**：

    ```bash
    # 将 "qwen3-4b-merged" 替换为你的模型目录名
    python -m vllm.entrypoints.openai.api_server \
      --host 0.0.0.0 \
      --model qwen3-4b-merged
    ```

2.  **测试 API**：

    ```bash
    curl http://localhost:8000/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d {
        "model": "qwen3-4b-merged",
        "messages": [{"role": "user", "content": "你好！"}]
      }
    ```

---

## SFT 数据格式示例

一条完整的 SFT 训练数据包含 `conversations` 和 `tools` 两个部分。这有助于模型理解对话上下文和可用的工具。

<details>
<summary>点击查看单条 SFT 训练数据示例</summary>

```json
{
    "conversations": [
        {
            "from": "human",
            "value": "你好，我需要一个1到100之间的随机数。"
        },
        {
            "from": "function_call",
            "value": "{\"name\": \"generate_random_number\", \"arguments\": {\"min\": 1, \"max\": 100}}"
        },
        {
            "from": "observation",
            "value": "{\"number\": 57}"
        },
        {
            "from": "gpt",
            "value": "生成的随机数在1到100之间，是57。"
        }
    ],
    "tools": [
        {
            "name": "generate_random_number",
            "description": "在指定范围内生成一个随机数",
            "parameters": {
                "type": "object",
                "properties": {
                    "min": {
                        "type": "integer",
                        "description": "最小值"
                    },
                    "max": {
                        "type": "integer",
                        "description": "最大值"
                    }
                },
                "required": [
                    "min",
                    "max"
                ]
            }
        }
    ]
}
```
</details>
