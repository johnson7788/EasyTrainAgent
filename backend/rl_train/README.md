# 强化学习训练模型

## 训练流程
1. 环境部署： [docs](..%2Fdocs)[prepare.md](../prepare.md)
2.开始训练,修改.env文件： [train.py](train.py)
    - 训练时和测试时使用的prompt.py
```
python train.py
```
3.测试模型训练效果: [model_test.py](model_test.py)

## 文件
```
├── README.md
├── env_template   ##模版文件，使用哪个模型进行搜索和作为reward模型
├── model_test.py ## 训练后的模型进行测试
├── prompt.py  #训练时的prompt,生成大纲和评估大纲的奖励模型
├── requirements.txt
├── topic.json    #训练时需要的主题数据
└── train.py       # 训练代码
```