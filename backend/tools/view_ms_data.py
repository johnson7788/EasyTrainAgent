#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/9/27 10:59
# @File  : view_ms_data.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 查看数据

from modelscope import MsDataset

# 加载数据集
dataset = MsDataset.load('AI-ModelScope/function-calling-chatml', split='train')
# dataset = MsDataset.load('zouxuhong/Countdown-Tasks-3to4', split='train')

# 查看数据集的基本信息
print("Dataset Information:")
print(f"Number of examples: {len(dataset)}")
print(f"Features of the dataset: {dataset.features}")

# 查看前5个样本
print("\nFirst 5 samples in the dataset:")
for i in range(5):
    print(f"Sample {i+1}: {dataset[i]}")
