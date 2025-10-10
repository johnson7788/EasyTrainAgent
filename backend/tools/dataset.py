# Copyright (c) Alibaba, Inc. and its affiliates.
import json
from typing import Any, Dict, Optional

from swift.llm import DatasetMeta, ResponsePreprocessor, load_dataset, register_dataset


class CustomPreprocessor(ResponsePreprocessor):
    prompt = """根据用户的需求，合理的使用工具 """

    def preprocess(self, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # 只取出问题
        print("\n" + "=" * 80)
        print("[DEBUG] 正在处理一条样本")
        user_question = row["messages"][0]["content"]
        print("[DEBUG] user_question:", user_question)
        # 最后的参考答案，可能没啥用
        response = row["messages"][-1]["content"]
        res = super().preprocess({
            'query': user_question
        })
        # 把工具加进去
        res['tools'] = row["tools"]
        return res


register_dataset(
    DatasetMeta(
        dataset_path='./train.jsonl',
        dataset_name="custom_mcp_data",
        preprocess_func=CustomPreprocessor(),
    ))

if __name__ == '__main__':
    dataset = load_dataset(['custom_mcp_data'])[0]
    print(f'dataset: {dataset}')
    print(f'dataset[0]: {dataset[0]}')
