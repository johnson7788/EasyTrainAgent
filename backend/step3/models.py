#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/8/6 10:59
# @File  : models.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 统一创建多厂商模型实例

import os
from typing import Optional

import dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

dotenv.load_dotenv()

# 尝试导入 Claude（Anthropic）
try:
    from langchain_anthropic import ChatAnthropic  # pip install langchain-anthropic
    _HAS_ANTHROPIC = True
except Exception:
    _HAS_ANTHROPIC = False


# 各 Provider 的 OpenAI 兼容配置（base_url + api_key 环境变量名）
_OPENAI_COMPAT_PROVIDERS = {
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url_env": None,
        "base_url_default": "https://api.openai.com/v1",
    },
    "deepseek": {
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url_env": None,
        "base_url_default": "https://api.deepseek.com/v1",
    },
    "ali": {
        "api_key_env": "ALI_API_KEY",
        "base_url_env": None,
        "base_url_default": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    },
    "silicon": {
        "api_key_env": "SILICON_API_KEY",
        "base_url_env": None,
        "base_url_default": "https://api.siliconflow.cn/v1",
    },
    "modelscope": {
        "api_key_env": "MODELSCOPE_API_KEY",  # 注意：你的 create_model.py 注释里写了 MODEL_SCOPE_API_KEY，但实际用了 MODELSCOPE_API_KEY
        "base_url_env": None,
        "base_url_default": "https://api-inference.modelscope.cn/v1",
    },
    "doubao": {
        "api_key_env": "DOUBAO_API_KEY",
        "base_url_env": None,
        "base_url_default": "https://ark.cn-beijing.volces.com/api/v3",
    },
    "vllm": {
        "api_key_env": "VLLM_API_KEY",
        "base_url_env": "VLLM_API_URL",       # 必填
        "base_url_default": None,
    },
    "ollama": {
        "api_key_env": "OLLAMA_API_KEY",      # 视你的服务是否校验
        "base_url_env": "OLLAMA_API_URL",     # 必填，如 http://localhost:11434/v1
        "base_url_default": None,
    },
    "local": {
        # 为了和你的 create_model.py 对齐，这里沿用 ALI_API_KEY；如不需要，可换成 LOCAL_API_KEY
        "api_key_env": "ALI_API_KEY",
        "base_url_env": None,
        "base_url_default": "http://localhost:6688",
    },
    "swift": {
        "api_key_env": "SWIFT_API_KEY",
        "base_url_env": "SWIFT_API_URL",  # 必填
        "base_url_default": "http://127.0.0.1:8000/v1",
    },
}


def _require_env(name: str):
    val = os.getenv(name)
    if not val:
        raise EnvironmentError(f"环境变量 {name} 未设置")
    return val


def create_model(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0,
    **kwargs
):
    """
    创建并返回一个 LangChain Chat 模型实例。
    - provider: 指定模型提供方；不传则读取环境变量 MODEL_PROVIDER
    - model:    指定模型名；不传则读取环境变量 LLM_MODEL
    - temperature: 生成温度（默认 0）
    - **kwargs: 透传给底层 LangChain 模型（如 timeout、max_retries 等）

    返回值：
      - ChatOpenAI / ChatGoogleGenerativeAI / ChatAnthropic 实例
    """
    provider = provider or os.getenv("MODEL_PROVIDER")
    model = model or os.getenv("LLM_MODEL")

    if not provider:
        raise ValueError("请通过参数 provider 或环境变量 MODEL_PROVIDER 指定模型提供方")
    if not model:
        raise ValueError("请通过参数 model 或环境变量 LLM_MODEL 指定模型名称")

    print(f"使用的模型为：{provider} 的 {model}")

    # 1) Google（非 OpenAI 兼容）
    if provider.lower() == "google":
        _require_env("GOOGLE_API_KEY")
        # ChatGoogleGenerativeAI 不需要 base_url
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            **kwargs
        )

    if provider.lower() == 'openai':
        HTTP_PROXY = os.getenv("HTTP_PROXY")
        if HTTP_PROXY:
            print("ChatOpenAI接口使用代理：" + HTTP_PROXY)
            model = ChatOpenAI(
                model=os.getenv('LLM_MODEL'),
                openai_api_key=os.getenv('OPENAI_API_KEY'),
                temperature=0,
                openai_proxy=HTTP_PROXY
            )
        else:
            model = ChatOpenAI(
                model=os.getenv('LLM_MODEL'),
                openai_api_key=os.getenv('OPENAI_API_KEY'),
                temperature=0
            )
    # 2) Claude / Anthropic（非 OpenAI 兼容）
    if provider.lower() == "claude":
        if not _HAS_ANTHROPIC:
            raise ImportError(
                "未安装 langchain-anthropic，请先执行：pip install langchain-anthropic"
            )
        _require_env("CLAUDE_API_KEY")
        return ChatAnthropic(
            model=model,                     # 例如：claude-3-5-sonnet-latest
            api_key=os.getenv("CLAUDE_API_KEY"),
            temperature=temperature,
            **kwargs
        )

    # 3) OpenAI 兼容类 Provider（统一用 ChatOpenAI + base_url ),不使用代理
    key = provider.lower()
    if key in _OPENAI_COMPAT_PROVIDERS:
        cfg = _OPENAI_COMPAT_PROVIDERS[key]
        api_key_env = cfg["api_key_env"]
        base_url_env = cfg["base_url_env"]
        base_url_default = cfg["base_url_default"]

        api_key = _require_env(api_key_env)
        base_url = os.getenv(base_url_env) if base_url_env else base_url_default
        if not base_url:
            raise EnvironmentError(
                f"{provider} 需要设置 {'/'.join([base_url_env]) if base_url_env else 'base_url'}"
            )
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            **kwargs
        )

    # 其他/不支持
    raise Exception("无效的模型Provider，请修改环境变量.env文件或传入正确的 provider")
