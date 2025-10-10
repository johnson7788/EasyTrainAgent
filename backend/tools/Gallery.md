# 命令行参数
https://swift.readthedocs.io/zh-cn/latest/Instruction/%E5%91%BD%E4%BB%A4%E8%A1%8C%E5%8F%82%E6%95%B0.html
命令行参数的介绍会分为基本参数，原子参数、集成参数和特定模型参数。命令行最终使用的参数列表为集成参数。集成参数继承自基本参数和一些原子参数。特定模型参数是针对于具体模型的参数，可以通过--model_kwargs'或者环境变量进行设置。
命令行传入list使用空格隔开即可。例如：--dataset <dataset_path1> <dataset_path2>。
命令行传入dict使用json。例如：--model_kwargs '{"fps_max_frames": 12}'。



# 如何debug：
你可以使用以下方式进行debug，这与使用命令行微调是等价的，但此方式不支持分布式。微调命令行运行入口可以查看这里。
from swift.llm import sft_main, TrainArguments
result = sft_main(TrainArguments(
    model='Qwen/Qwen2.5-7B-Instruct',
    train_type='lora',
    dataset=['AI-ModelScope/alpaca-gpt4-data-zh#500',
             'AI-ModelScope/alpaca-gpt4-data-en#500',
             'swift/self-cognition#500'],
    torch_dtype='bfloat16',
    # ...
))


# swift deploy 与 swift rollout 的区别
swift deploy 主要用于模型的部署和推理，支持 PT、vLLM、SGLang 等多种引擎，兼容流式推理与 OpenAI API 的调用格式。
swift rollout 则专注于 GRPO 推理加速，目前仅支持 vLLM 引擎，并内置了权重自动同步的功能。


# 多轮规划器 MultiTurnScheduler
MultiTurnScheduler 是一个抽象基类，提供了默认的多轮对话管理逻辑，
多轮规划器主要承担两大核心功能：
终止条件判断：通过 check_finished 方法判断当前轮次推理是否应该结束
推理请求构造：通过 step 方法构建下一轮推理的请求对象


# GRPO公式
下面按公式逐项解释（它本质上是带**KL 正则**的 PPO-式目标，在每个提示上做**多条采样分组**求平均——这也是 GRPO 的“Group/Relative”的来源）：

**总体目标**

* $J_{\text{GRPO}}(\theta)= \mathbb{E}_{q\sim P(Q),\,\{o_i\}\sim \pi_{\theta_{\text{old}}}}\big[ \cdots \big]$
  从提示分布 $P(Q)$ 采样一个问题 $q$，再用旧策略 $\pi_{\theta_{\text{old}}}$ 为这个 $q$ 采样 **G** 条答案（记为组 $\{o_i\}_{i=1}^G$），对组内和时间步求平均、再求期望。

**组与时间维度的平均**

* $\frac{1}{G}\sum_{i=1}^G \frac{1}{|o_i|}\sum_{t=1}^{|o_i|}(\cdots)$
  对每个答案序列 $o_i$ 的每个 token（时间步 $t$）求平均，避免长序列权重更大。

**PPO 的“比率×优势 + 裁剪”**

* 概率比率（policy ratio）：

  $$
  r_{i,t}(\theta)=\frac{\pi_\theta(o_{i,t}\mid q,o_{i,<t})}{\pi_{\theta_{\text{old}}}(o_{i,t}\mid q,o_{i,<t})}
  $$

  表示新旧策略在第 $t$ 个 token 上给出该动作（token）的相对倾向。
* 裁剪目标（和 PPO 一样取最小值）：

  $$
  \min\big[\, r_{i,t} \,\hat A_{i,t},\ \text{clip}(r_{i,t},\,1-\varepsilon,\,1+\varepsilon)\,\hat A_{i,t}\big]
  $$

  其中 $\varepsilon$ 是裁剪阈值，防止单次更新走得过远导致策略崩溃。
* $\hat A_{i,t}$ 是第 $t$ 步的**优势函数**估计：token 的好坏相对“基线”的提升量。
  在 GRPO 里常见做法是把**序列级奖励**（如打分、偏好）分摊/回传到 token（也可用**组相对基线**：用同一提示下的组平均/排名作为基线，使优势变成 “好于同组平均多少”）。

**KL 正则（拉回参考策略）**

* $-\beta\, \mathbb{D}_{\mathrm{KL}}\!\left[\pi_\theta\,\|\,\pi_{\text{ref}}\right]$
  惩罚与参考策略（通常是未对齐的初始模型或一个固定策略）偏离过多，$\beta$ 控制强度。这样既能提升奖励，又不会漂移得太激进。

**直观理解**

1. 同一提示 $q$ 采样 **G 条答案**，用它们之间的**相对好坏**（优势）来学习，噪声更小、稳定性更好。
2. 对每个 token，用 **PPO 裁剪**限制步长，用 **KL 项**把策略拉回参考分布，训练更稳。
3. 结果就是：让产生高奖励的 token 概率上升、低奖励的下降，但更新被 $\varepsilon$ 和 $\beta$ 两个“安全阀”控制。

# swift/cli/main.py
ROUTE_MAPPING: Dict[str, str] = {
    'pt': 'swift.cli.pt',
    'sft': 'swift.cli.sft',
    'infer': 'swift.cli.infer',
    'merge-lora': 'swift.cli.merge_lora',
    'web-ui': 'swift.cli.web_ui',
    'deploy': 'swift.cli.deploy',
    'rollout': 'swift.cli.rollout',
    'rlhf': 'swift.cli.rlhf',
    'sample': 'swift.cli.sample',
    'export': 'swift.cli.export',
    'eval': 'swift.cli.eval',
    'app': 'swift.cli.app',
}

# 各子命令说明（按路由表与文件）

* `pt` → `swift.cli.pt`
  文件 `pt.py`：`from swift.llm import pt_main` → 预训练（pre-training）入口。
  典型用途：从头或继续在大规模语料上训练基础模型。支持分布式（若设置了环境变量，会走 `torchrun`）。

* `sft` → `swift.cli.sft`
  文件 `sft.py`：`from swift.llm import sft_main`。
  特别点：如果环境变量 `UNSLOTH_PATCH_TRL=1`，会 `import unsloth` 做 TRL 的补丁优化。
  典型用途：**监督微调**（Supervised Fine-Tuning），在指令/对话数据上对基座模型做二阶段训练；支持分布式。

* `infer` → `swift.cli.infer`
  文件 `infer.py`：`from swift.llm import infer_main`。
  典型用途：**推理/服务**模式下加载模型并进行生成或批量预测；在设置分布式变量时也会走 `torchrun`（便于多卡推理或张量并行）。

* `merge-lora` → `swift.cli.merge_lora`
  文件 `merge_lora.py`：定义了 `SwiftMergeLoRA(SwiftPipeline)`，`run()` 里调用 `merge_lora(self.args)`（`ExportArguments` 参数集）。
  典型用途：把 **LoRA/LoRA+ 适配器**权重合并回基础模型，得到一个合并后的全量权重（便于部署或导出）。

* `web-ui` → `swift.cli.web_ui`
  文件 `web_ui.py`：`from swift.ui import webui_main`。
  典型用途：启动**可视化 Web 界面**（通常是 Gradio/Streamlit 一类）。
  兼容提示：若你传了 `--model/--adapters/--ckpt_dir` 等参数，会被改写到 `swift app`（见上面的兼容逻辑）。

* `deploy` → `swift.cli.deploy`
  文件 `deploy.py`：`from swift.llm import deploy_main`。
  典型用途：**部署**模型/服务的自动化流程（例如打包、发布到服务框架、生成运行配置等）。

* `rollout` → `swift.cli.rollout`
  文件 `rollout.py`：`from swift.llm import rollout_main`。
  典型用途：**灰度/滚动发布**、版本切换、流量控制等与上线相关的运维动作（具体策略由 `rollout_main` 实现）。

* `rlhf` → `swift.cli.rlhf`
  文件 `rlhf.py`：`from swift.llm import rlhf_main`。
  典型用途：**人类反馈强化学习**（RLHF/ DPO/ PPO 等流程的一部分），在偏好数据上优化模型；支持分布式。

* `sample` → `swift.cli.sample`
  文件 `sample.py`：`from swift.llm.sampling import sampling_main`。
  典型用途：从一个或多个模型 **抽样生成** 文本，用于对比、质检、示例集产出或小规模评测。

* `export` → `swift.cli.export`
  文件 `export.py`：`from swift.llm import export_main`。
  典型用途：**导出模型**到目标格式/目录（例如合并权重、转静态图、导出到特定后端格式，配合 `merge-lora` 常见）。

* `eval` → `swift.cli.eval`
  文件 `eval.py`：`from swift.llm import eval_main`。
  典型用途：在基准或自定义数据集上做**评测**（准确率、困惑度、任务指标等），产出评测报告/表格。

* `app` → `swift.cli.app`
  文件 `app.py`：`from swift.llm import app_main`。
  典型用途：**统一的交互式应用入口**（往往是 Web UI 的新推荐入口）；与 `web-ui` 的兼容逻辑相呼应，是官方建议使用的方式。


# 内置的奖励函数
ms-swift/swift/plugin/orm.py
orms = {
    'toolbench': ReactORM,
    'math': MathORM,
    'accuracy': MathAccuracy,
    'format': Format,
    'react_format': ReActFormat,
    'cosine': CosineReward,
    'repetition': RepetitionPenalty,
    'soft_overlong': SoftOverlong,
}


# 流程
RLHF, __post_init__ 开始进行分别init
ms-swift/swift/llm/argument/rlhf_args.py
ms-swift/swift/llm/argument/train_args.py
ms-swift/swift/llm/argument/base_args/base_args.py 
  --- self._init_custom_register() --加载自己定义的数据集 dataset.py
  --  self._import_external_plugins() 注册外部插件 plugin.py

运行训练
ms-swift/swift/llm/base.py
  def main(self):   --- result = self.run()
    -- ms-swift/swift/llm/train/sft.py
处理数据,检查美中数据类型
ms-swift/swift/llm/dataset/preprocessor/core.py
  -- def batched_preprocess
                    for r in row:
                    self._check_objects(r)
                    self._check_rejected_response(r)
                    self._check_messages(r)
                    self._cast_mm_data(r)
ms-swift/swift/llm/base.py --self.run() -- args.save_args() 保存到训练参数

ms-swift/swift/llm/train/tuner.py  -- 不同训练方式的准备方式 def prepare_model

ms-swift/swift/trainers/rlhf_trainer/grpo_trainer.py
  --class GRPOTrainer  参数reward_funcs 奖励函数

ms-swift/swift/trainers/rlhf_trainer/rlhf_mixin.py  --class RLHFTrainerMixin:

swift rollout 时使用vllm
ms-swift/swift/llm/infer/rollout.py  --async def async_llm_worker -- engine = SwiftRolloutDeploy  --def get_infer_engine --return GRPOVllmEngine(**kwargs)
ms-swift/swift/llm/infer/infer_engine/vllm_engine.py -- VllmEngine

# 在强化学习训练时，是如何把对话数据发送给vllm的rollout客户端的，具体的代码在哪里
swift/trainers/rlhf_trainer/grpo_trainer.py
 def _engine_infer(
_server_rollout


# 添加tools，方便请求vllm
ms-swift/swift/trainers/rlhf_trainer/grpo_trainer.py
        for data in inputs:
            # Extract required metadata fields
            request_data = {key: data[key] for key in REQUEST_METADATA_FIELDS if key in data}
            if 'tools' in data:
                if isinstance(data["tools"], str):
                    request_data["tools"] = json.loads(data["tools"])
                else:
                    request_data["tools"] = data["tools"]
            if 'uuid' not in request_data:
                request_data['uuid'] = data['request_id']  # Use unique request_id for vLLM
            # Preserve additional fields for multi-turn async scenarios