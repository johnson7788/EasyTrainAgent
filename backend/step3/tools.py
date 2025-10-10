#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/8/6 10:48
# @File  : tools.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : Agent使用的工具, 设置3个知识库工具
import os
import httpx
import re
import time
import json
from datetime import datetime
import random
from typing import Annotated, NotRequired
from langchain_core.tools import tool
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from custom_state import CustomState
@tool
def search_document_db(keyword: str, tool_call_id: Annotated[str, InjectedToolCallId], state: Annotated[CustomState, InjectedState]) -> Command:
    """
    搜索数据库
    :param keyword: 关键词, eg: 乳腺癌
    :return:
    """
    print("SearchDocument: " + keyword)
    data = [{'title': "Initiation Of Medications For Parkinson'S Disease: A Qualitative Description", 'id': 34264430, 'match_sentence': '目的与目标：了解帕金森病患者在开始使用帕金森病药物治疗时的经历，以促进该疾病的药物治疗', 'match_sentences': [{'id': '03_770_0', 'sentence': '目的与目标：了解帕金森病患者在开始使用帕金森病药物治疗时的经历，以促进该疾病的药物治疗', 'db_id': 34264430, 'prefix_sentence': '', 'tail_sentence': '背景：先前的研究已经记录了帕金森病患者对药物治疗方案的不依从性以及他们对开始使用药物治疗的犹豫不决\n然而，在美国，关于帕金森病患者开始使用抗帕金森病药物的经历、决策以及他们对这些药物的信念或理解程度，所知甚少'}, {'id': '03_770_1', 'sentence': '背景：先前的研究已经记录了帕金森病患者对药物治疗方案的不依从性以及他们对开始使用药物治疗的犹豫不决', 'db_id': 34264430, 'prefix_sentence': '目的与目标：了解帕金森病患者在开始使用帕金森病药物治疗时的经历，以促进该疾病的药物治疗', 'tail_sentence': '然而，在美国，关于帕金森病患者开始使用抗帕金森病药物的经历、决策以及他们对这些药物的信念或理解程度，所知甚少\n设计：采用探索性和描述性的定性研究方法'}, {'id': '03_770_2', 'sentence': '然而，在美国，关于帕金森病患者开始使用抗帕金森病药物的经历、决策以及他们对这些药物的信念或理解程度，所知甚少', 'db_id': 34264430, 'prefix_sentence': '目的与目标：了解帕金森病患者在开始使用帕金森病药物治疗时的经历，以促进该疾病的药物治疗\n背景：先前的研究已经记录了帕金森病患者对药物治疗方案的不依从性以及他们对开始使用药物治疗的犹豫不决', 'tail_sentence': '设计：采用探索性和描述性的定性研究方法'}, {'id': '03_770_3', 'sentence': '设计：采用探索性和描述性的定性研究方法', 'db_id': 34264430, 'prefix_sentence': '背景：先前的研究已经记录了帕金森病患者对药物治疗方案的不依从性以及他们对开始使用药物治疗的犹豫不决\n然而，在美国，关于帕金森病患者开始使用抗帕金森病药物的经历、决策以及他们对这些药物的信念或理解程度，所知甚少', 'tail_sentence': ''}], 'url': 'https://bing.com/26420046_f4d7548c646a49bcbf1f59c01f612f50.pdf'}, {'title': 'Antiviral Therapy In Patients With Chronic Hepatitis C Is Associated With A Reduced Risk Of Parkinsonism', 'id': 2731487, 'match_sentence': '背景：慢性丙型肝炎（CHC）抗病毒治疗后帕金森综合征的风险尚不明确', 'match_sentences': [{'id': '03_785_0', 'sentence': '背景：慢性丙型肝炎（CHC）抗病毒治疗后帕金森综合征的风险尚不明确', 'db_id': 2731487, 'prefix_sentence': '', 'tail_sentence': '目的：研究CHC与帕金森综合征和抗病毒治疗的有效性之间的关联\n方法：通过2004年至2012年台湾的国家健康保险研究数据库，采用倾向评分匹配CHC患者与非CHC患者、接受聚乙二醇干扰素为基础的抗病毒治疗患者及未接受该治疗的患者，并随访新发的帕金森综合征和帕金森病（PD）诊断'}, {'id': '03_785_1', 'sentence': '目的：研究CHC与帕金森综合征和抗病毒治疗的有效性之间的关联', 'db_id': 2731487, 'prefix_sentence': '背景：慢性丙型肝炎（CHC）抗病毒治疗后帕金森综合征的风险尚不明确', 'tail_sentence': '方法：通过2004年至2012年台湾的国家健康保险研究数据库，采用倾向评分匹配CHC患者与非CHC患者、接受聚乙二醇干扰素为基础的抗病毒治疗患者及未接受该治疗的患者，并随访新发的帕金森综合征和帕金森病（PD）诊断\n进行多变量Cox比例风险回归分析'}, {'id': '03_785_2', 'sentence': '方法：通过2004年至2012年台湾的国家健康保险研究数据库，采用倾向评分匹配CHC患者与非CHC患者、接受聚乙二醇干扰素为基础的抗病毒治疗患者及未接受该治疗的患者，并随访新发的帕金森综合征和帕金森病（PD）诊断', 'db_id': 2731487, 'prefix_sentence': '背景：慢性丙型肝炎（CHC）抗病毒治疗后帕金森综合征的风险尚不明确\n目的：研究CHC与帕金森综合征和抗病毒治疗的有效性之间的关联', 'tail_sentence': '进行多变量Cox比例风险回归分析'}, {'id': '03_785_3', 'sentence': '进行多变量Cox比例风险回归分析', 'db_id': 2731487, 'prefix_sentence': '目的：研究CHC与帕金森综合征和抗病毒治疗的有效性之间的关联\n方法：通过2004年至2012年台湾的国家健康保险研究数据库，采用倾向评分匹配CHC患者与非CHC患者、接受聚乙二醇干扰素为基础的抗病毒治疗患者及未接受该治疗的患者，并随访新发的帕金森综合征和帕金森病（PD）诊断', 'tail_sentence': ''}], 'url': 'https://bing.com/31505068_0d205110fefc4abc98a0d93caa66c1ab.pdf'}, {'title': "Survey On General Knowledge On Parkinson'S Disease In Patients With Parkinson'S Disease And Current Clinical Practice For Parkinson'S Disease Among General Neurologists From Southwest China", 'id': 34121438, 'match_sentence': '目的：评估四川省基层医院帕金森病（PD）患者对帕金森病的一般知识以及神经科医生对帕金森病诊断和治疗现状及选择情况', 'match_sentences': [{'id': '03_791_0', 'sentence': '目的：评估四川省基层医院帕金森病（PD）患者对帕金森病的一般知识以及神经科医生对帕金森病诊断和治疗现状及选择情况', 'db_id': 34121438, 'prefix_sentence': '', 'tail_sentence': '方法：于2010年10月至2012年10月，在四川省基层医院对344名帕金森病患者和368名神经科医生进行了横断面问卷调查\n针对患者，设计了一份关于帕金森病一般知识的问卷；针对神经科医生，设计了一份关于帕金森病诊断和治疗的问卷'}, {'id': '03_791_1', 'sentence': '方法：于2010年10月至2012年10月，在四川省基层医院对344名帕金森病患者和368名神经科医生进行了横断面问卷调查', 'db_id': 34121438, 'prefix_sentence': '目的：评估四川省基层医院帕金森病（PD）患者对帕金森病的一般知识以及神经科医生对帕金森病诊断和治疗现状及选择情况', 'tail_sentence': '针对患者，设计了一份关于帕金森病一般知识的问卷；针对神经科医生，设计了一份关于帕金森病诊断和治疗的问卷\n结果：帕金森病患者在病因、抗帕金森病药物的副作用、左旋多巴的使用以及手术治疗等方面缺乏相关信息'}, {'id': '03_791_2', 'sentence': '针对患者，设计了一份关于帕金森病一般知识的问卷；针对神经科医生，设计了一份关于帕金森病诊断和治疗的问卷', 'db_id': 34121438, 'prefix_sentence': '目的：评估四川省基层医院帕金森病（PD）患者对帕金森病的一般知识以及神经科医生对帕金森病诊断和治疗现状及选择情况\n方法：于2010年10月至2012年10月，在四川省基层医院对344名帕金森病患者和368名神经科医生进行了横断面问卷调查', 'tail_sentence': '结果：帕金森病患者在病因、抗帕金森病药物的副作用、左旋多巴的使用以及手术治疗等方面缺乏相关信息'}, {'id': '03_791_3', 'sentence': '结果：帕金森病患者在病因、抗帕金森病药物的副作用、左旋多巴的使用以及手术治疗等方面缺乏相关信息', 'db_id': 34121438, 'prefix_sentence': '方法：于2010年10月至2012年10月，在四川省基层医院对344名帕金森病患者和368名神经科医生进行了横断面问卷调查\n针对患者，设计了一份关于帕金森病一般知识的问卷；针对神经科医生，设计了一份关于帕金森病诊断和治疗的问卷', 'tail_sentence': ''}], 'url': 'https://bing.com/24529223_c72b29a066b0421886842388c59b6654.pdf'}, {'title': "Novel Models For Parkinson'S Disease And Their Impact On Future Drug Discovery", 'id': 4525353, 'match_sentence': '从基于细胞的模型、熟知的毒素基动物模型，到最近的基因模型和越来越多使用的非哺乳动物模型，每个模型都在寻找更好的帕金森病治疗方法方面具有价值', 'match_sentences': [{'id': '03_796_0', 'sentence': '为了寻找更好的治疗方法，最近已经开发了多种新的体内和体外帕金森病模型', 'db_id': 4525353, 'prefix_sentence': '', 'tail_sentence': '涵盖领域：作者概述了各种传统的帕金森病模型，并讨论了近年来新开发的模型\n他们还探讨了这些模型在帕金森病患者中发现具有潜在治疗价值药物方面的应用'}, {'id': '03_796_1', 'sentence': '涵盖领域：作者概述了各种传统的帕金森病模型，并讨论了近年来新开发的模型', 'db_id': 4525353, 'prefix_sentence': '为了寻找更好的治疗方法，最近已经开发了多种新的体内和体外帕金森病模型', 'tail_sentence': '他们还探讨了这些模型在帕金森病患者中发现具有潜在治疗价值药物方面的应用\n从基于细胞的模型、熟知的毒素基动物模型，到最近的基因模型和越来越多使用的非哺乳动物模型，每个模型都在寻找更好的帕金森病治疗方法方面具有价值'}, {'id': '03_796_2', 'sentence': '他们还探讨了这些模型在帕金森病患者中发现具有潜在治疗价值药物方面的应用', 'db_id': 4525353, 'prefix_sentence': '为了寻找更好的治疗方法，最近已经开发了多种新的体内和体外帕金森病模型\n涵盖领域：作者概述了各种传统的帕金森病模型，并讨论了近年来新开发的模型', 'tail_sentence': '从基于细胞的模型、熟知的毒素基动物模型，到最近的基因模型和越来越多使用的非哺乳动物模型，每个模型都在寻找更好的帕金森病治疗方法方面具有价值\n专家意见：在发现帕金森病近60年后，左旋多巴仍然是帕金森病患者的黄金标准治疗方法'}, {'id': '03_796_3', 'sentence': '从基于细胞的模型、熟知的毒素基动物模型，到最近的基因模型和越来越多使用的非哺乳动物模型，每个模型都在寻找更好的帕金森病治疗方法方面具有价值', 'db_id': 4525353, 'prefix_sentence': '涵盖领域：作者概述了各种传统的帕金森病模型，并讨论了近年来新开发的模型\n他们还探讨了这些模型在帕金森病患者中发现具有潜在治疗价值药物方面的应用', 'tail_sentence': '专家意见：在发现帕金森病近60年后，左旋多巴仍然是帕金森病患者的黄金标准治疗方法\n似乎不太可能有一个模型能够完全再现帕金森病的复杂性，就像认为不可能有一种单一治疗方案能够同时缓解帕金森病的运动和非运动症状一样'}, {'id': '03_796_4', 'sentence': '专家意见：在发现帕金森病近60年后，左旋多巴仍然是帕金森病患者的黄金标准治疗方法', 'db_id': 4525353, 'prefix_sentence': '他们还探讨了这些模型在帕金森病患者中发现具有潜在治疗价值药物方面的应用\n从基于细胞的模型、熟知的毒素基动物模型，到最近的基因模型和越来越多使用的非哺乳动物模型，每个模型都在寻找更好的帕金森病治疗方法方面具有价值', 'tail_sentence': '似乎不太可能有一个模型能够完全再现帕金森病的复杂性，就像认为不可能有一种单一治疗方案能够同时缓解帕金森病的运动和非运动症状一样\n因此，治疗可能需要多种疗法的组合'}, {'id': '03_796_5', 'sentence': '似乎不太可能有一个模型能够完全再现帕金森病的复杂性，就像认为不可能有一种单一治疗方案能够同时缓解帕金森病的运动和非运动症状一样', 'db_id': 4525353, 'prefix_sentence': '从基于细胞的模型、熟知的毒素基动物模型，到最近的基因模型和越来越多使用的非哺乳动物模型，每个模型都在寻找更好的帕金森病治疗方法方面具有价值\n专家意见：在发现帕金森病近60年后，左旋多巴仍然是帕金森病患者的黄金标准治疗方法', 'tail_sentence': '因此，治疗可能需要多种疗法的组合'}, {'id': '03_796_6', 'sentence': '因此，治疗可能需要多种疗法的组合', 'db_id': 4525353, 'prefix_sentence': '专家意见：在发现帕金森病近60年后，左旋多巴仍然是帕金森病患者的黄金标准治疗方法\n似乎不太可能有一个模型能够完全再现帕金森病的复杂性，就像认为不可能有一种单一治疗方案能够同时缓解帕金森病的运动和非运动症状一样', 'tail_sentence': ''}], 'url': 'https://bing.com/29363335_5f171d8a03154e2b97f4ecbdcdd6eeab.pdf'}, {'title': "Parkinson'S Syndrome After Cranial Radiotherapy: A Case Report", 'id': 35867594, 'match_sentence': '帕金森综合征是以运动迟缓为核心问题的一组体征和症状，可能是特发性帕金森病(帕金森病，PD)、继发性帕金森病或由神经退行性疾病引起的帕金森病的一种表现', 'match_sentences': [{'id': '03_799_0', 'sentence': '帕金森综合征是以运动迟缓为核心问题的一组体征和症状，可能是特发性帕金森病(帕金森病，PD)、继发性帕金森病或由神经退行性疾病引起的帕金森病的一种表现', 'db_id': 35867594, 'prefix_sentence': '', 'tail_sentence': '帕金森病是帕金森综合症最常见的病因，约占80%的病例\n帕金森综合征的继发病因包括肿瘤、创伤、脑积水、化疗、两性霉素B、甲氧氯普胺等药物和放射治疗'}, {'id': '03_799_1', 'sentence': '帕金森病是帕金森综合症最常见的病因，约占80%的病例', 'db_id': 35867594, 'prefix_sentence': '帕金森综合征是以运动迟缓为核心问题的一组体征和症状，可能是特发性帕金森病(帕金森病，PD)、继发性帕金森病或由神经退行性疾病引起的帕金森病的一种表现', 'tail_sentence': '帕金森综合征的继发病因包括肿瘤、创伤、脑积水、化疗、两性霉素B、甲氧氯普胺等药物和放射治疗\n放射治疗后继发的帕金森症状在文献中很少报道，通常卡比多巴-左旋多巴不能缓解'}, {'id': '03_799_2', 'sentence': '帕金森综合征的继发病因包括肿瘤、创伤、脑积水、化疗、两性霉素B、甲氧氯普胺等药物和放射治疗', 'db_id': 35867594, 'prefix_sentence': '帕金森综合征是以运动迟缓为核心问题的一组体征和症状，可能是特发性帕金森病(帕金森病，PD)、继发性帕金森病或由神经退行性疾病引起的帕金森病的一种表现\n帕金森病是帕金森综合症最常见的病因，约占80%的病例', 'tail_sentence': '放射治疗后继发的帕金森症状在文献中很少报道，通常卡比多巴-左旋多巴不能缓解'}, {'id': '03_799_3', 'sentence': '放射治疗后继发的帕金森症状在文献中很少报道，通常卡比多巴-左旋多巴不能缓解', 'db_id': 35867594, 'prefix_sentence': '帕金森病是帕金森综合症最常见的病因，约占80%的病例\n帕金森综合征的继发病因包括肿瘤、创伤、脑积水、化疗、两性霉素B、甲氧氯普胺等药物和放射治疗', 'tail_sentence': ''}], 'url': 'https://bing.com/35619842_150f93ae06f14988a4f13ad3f6d2d553.pdf'}]
    contents = ""
    for item in data:
        match_sentences = item.get("match_sentences")
        for one_sentence in match_sentences:
            sentence_id = one_sentence.get("id")
            sentence = one_sentence.get("sentence")
            contents += f"{sentence_id} -- {sentence}\n"
        contents += "\n"
    print(f"tool_call_id: {tool_call_id}")
    return Command(update={
        "search_dbs": [{"db": "search_document_db", "result": data}],
        "messages": [
            ToolMessage(content=contents, tool_call_id=tool_call_id)
        ]
    })

# ALL_TOOLS = [search_document_db]
ALL_TOOLS = []