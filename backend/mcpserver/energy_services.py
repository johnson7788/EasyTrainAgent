#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/9/15 20:06
# @File  : energy_services.py.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 一体化的 LNG 价格信息 & LNG 工厂利润（模拟）查询服务
#
from fastmcp import FastMCP
from typing import List, Dict, Optional
from datetime import datetime, timedelta, date
import random
import hashlib
import statistics  # 目前未直接使用，保留以便后续计算均值/分位

# ========== 全局配置：固定随机种子 & 可重建 ==========
DEFAULT_SEED = 20250422  # 可按需修改
SEED = DEFAULT_SEED

def _stable_rng(*keys) -> random.Random:
    """
    基于全局 SEED 与可哈希 keys 生成稳定的 RNG（与调用次数无关）。
    """
    payload = (str(SEED) + "::" + "|".join(map(str, keys))).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    # 取前 8 字节生成 64-bit 种子
    n = int.from_bytes(digest[:8], "big", signed=False)
    return random.Random(n)

# ========== FastMCP 服务 ==========
mcp = FastMCP("LNG信息与工厂利润一体化服务")

# ========== 模拟静态/半静态数据（会按种子重建） ==========
# 省份与工厂
SIMULATED_FACTORIES: Dict[str, List[str]] = {
    "内蒙古": ["内蒙古工厂A", "内蒙古工厂B", "内蒙古工厂C"],
    "河北": ["河北工厂X", "河北工厂Y"]
}

# 竞拍价（元/立方米）
SIMULATED_AUCTION_PRICES: Dict[str, Dict[str, float]] = {
    "内蒙古": {},
    "河北": {}
}

# 工厂出厂价（元/吨）
SIMULATED_FACTORY_PRICES: Dict[str, Dict[str, float]] = {}

# LNG 到岸/送到价（月度基准价，元/立方米）
SIMULATED_LNG_PRICES: Dict[str, Dict[str, float]] = {
    "浙江": {
        "2025-04": 4.5,
        "2025-03": 4.2,
        "2024-04": 4.0,
    },
    "山西": {
        "2025-04": 4.3,
        "2025-03": 4.1,
        "2024-04": 3.9,
    },
    "河北": {
        "2025-04": 4.4,
        "2025-03": 4.0,
        "2024-04": 3.8,
    }
}

# 供需与库存（示例）
SIMULATED_SUPPLY_DEMAND = {
    "浙江": [
        {"date": "2025-04-17", "demand": 1000, "supply": 900, "inventory": 5000},
        {"date": "2025-04-16", "demand": 950, "supply": 920, "inventory": 5100},
    ],
    "山西": [
        {"date": "2025-04-17", "demand": 800, "supply": 850, "inventory": 4200},
        {"date": "2025-04-16", "demand": 790, "supply": 800, "inventory": 4300},
    ],
    "河北": [
        {"date": "2025-04-17", "demand": 870, "supply": 840, "inventory": 4600},
        {"date": "2025-04-16", "demand": 860, "supply": 850, "inventory": 4550},
    ],
}

# ========== 重建模拟数据（随 SEED 与基准日而变，保证可复现） ==========
def _daterange(start_date: date, end_date: date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def _parse_date(date_str: str) -> Optional[date]:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return None

def regenerate_simulated_data(base_date: Optional[date] = None, days: int = 30) -> None:
    """
    按当前 SEED 重建最近 `days` 天（含基准日）的竞拍价与出厂价。
    """
    global SIMULATED_AUCTION_PRICES, SIMULATED_FACTORY_PRICES
    SIMULATED_AUCTION_PRICES = {"内蒙古": {}, "河北": {}}
    SIMULATED_FACTORY_PRICES = {}

    if base_date is None:
        base_date = datetime.now().date()

    for i in range(days):
        current_date_obj = base_date - timedelta(days=i)
        date_str = current_date_obj.strftime("%Y-%m-%d")

        # 竞拍价：按省与日期建立稳定 RNG
        rng_nm = _stable_rng("auction", "内蒙古", date_str)
        rng_hb = _stable_rng("auction", "河北", date_str)
        SIMULATED_AUCTION_PRICES["内蒙古"][date_str] = round(rng_nm.uniform(2.8, 3.2), 2)
        SIMULATED_AUCTION_PRICES["河北"][date_str]   = round(rng_hb.uniform(3.0, 3.4), 2)

        # 出厂价：按工厂与日期建立稳定 RNG
        for prov in ("内蒙古", "河北"):
            for factory in SIMULATED_FACTORIES[prov]:
                if factory not in SIMULATED_FACTORY_PRICES:
                    SIMULATED_FACTORY_PRICES[factory] = {}
                rng = _stable_rng("factory_price", factory, date_str)
                if prov == "内蒙古":
                    SIMULATED_FACTORY_PRICES[factory][date_str] = round(rng.uniform(5800, 6200))
                else:  # 河北
                    SIMULATED_FACTORY_PRICES[factory][date_str] = round(rng.uniform(6000, 6400))

# 初始化一次（使用 DEFAULT_SEED 与今天作为基准）
regenerate_simulated_data()

# ========== 公共工具 ==========
@mcp.tool()
def get_current_date() -> str:
    """返回今天的日期，格式为YYYY-MM-DD。"""
    return datetime.now().strftime("%Y-%m-%d")

@mcp.tool()
def get_current_time() -> str:
    """返回当前时间，格式为HH:MM:SS。"""
    return datetime.now().strftime("%H:%M:%S")

@mcp.tool()
def set_seed(seed: int) -> int:
    """
    设置全局 SEED，并重建最近30天的模拟数据。
    返回生效的种子值。
    """
    global SEED
    SEED = int(seed)
    regenerate_simulated_data()
    return SEED

@mcp.tool()
def regenerate_data(base_date: Optional[str] = None, days: int = 30) -> str:
    """
    手动重建模拟数据。
    base_date: YYYY-MM-DD；若为空则使用今天。
    days: 重建天数（含基准日）。
    """
    d = _parse_date(base_date) if base_date else None
    regenerate_simulated_data(d, days=max(1, int(days)))
    return f"Regenerated with SEED={SEED}, base_date={(d or datetime.now().date()).isoformat()}, days={days}"

# ========== 工厂利润（模拟）相关：查询竞拍价与出厂价 ==========
@mcp.tool()
def get_auction_price(province: str, start_date: str, end_date: str) -> Dict[str, float]:
    """
    获取指定省份在指定日期范围内的原料气竞拍价格（模拟）。
    """
    print(f"[模拟接口] 查询竞拍价: 省份={province}, 范围={start_date}~{end_date}")
    s = _parse_date(start_date)
    e = _parse_date(end_date)
    if not s or not e or s > e:
        print("[模拟接口] 日期格式错误或开始日期晚于结束日期。")
        return {}

    out: Dict[str, float] = {}
    if province in SIMULATED_AUCTION_PRICES:
        data = SIMULATED_AUCTION_PRICES[province]
        for d in _daterange(s, e):
            k = d.strftime("%Y-%m-%d")
            if k in data:
                out[k] = data[k]
    print(f"[模拟接口] 返回条目数: {len(out)}")
    return out

@mcp.tool()
def get_factory_prices(factory_names: List[str], start_date: str, end_date: str) -> Dict[str, Dict[str, float]]:
    """
    获取指定工厂列表在指定日期范围内的出厂价格（模拟）。
    返回结构：{date: {factory: price, ...}, ...}
    """
    print(f"[模拟接口] 查询出厂价: 工厂={factory_names}, 范围={start_date}~{end_date}")
    s = _parse_date(start_date)
    e = _parse_date(end_date)
    if not s or not e or s > e:
        print("[模拟接口] 日期格式错误或开始日期晚于结束日期。")
        return {}

    out: Dict[str, Dict[str, float]] = {}
    for d in _daterange(s, e):
        k = d.strftime("%Y-%m-%d")
        daily: Dict[str, float] = {}
        for f in factory_names:
            if f in SIMULATED_FACTORY_PRICES and k in SIMULATED_FACTORY_PRICES[f]:
                daily[f] = SIMULATED_FACTORY_PRICES[f][k]
        if daily:
            out[k] = daily
    print(f"[模拟接口] 返回天数: {len(out)}")
    return out

# ========== LNG 价格问题 SOP Prompt ==========
@mcp.prompt("SOP")
def sop_lng_price_analysis(question: str) -> str:
    """
    返回处理“某地LNG送到价格及变化原因”的标准分析步骤（SOP）。
    """
    return f"""
你需要回答一个关于液化天然气（LNG）价格变动的问题，以下是标准的思考与分析流程（SOP）：

1. **识别地区与时间范围**：
   - 从问题中提取出地区名称（如“浙江”、“山西”、“河北”）。
   - 获取当前日期。
   - 获取历史同期时间（通常为去年同月或同期）。

2. **查询当前价格与历史价格**：
   - 查询该地区当前LNG送到价格。
   - 查询该地区历史同期LNG送到价格。
   - 对比当前价格与历史价格的差异，并说明是上涨、下跌还是持平。

3. **分析供需库存与市场信息**：
   - 获取该地区最近的供需数据（需求量、供应量、库存情况）。
   - 检查是否存在供需缺口或库存变动导致价格变动。
   - 汇总最近的相关新闻（如天气变化、国际价格波动、政策调控等），用于补充原因分析。

4. **总结结论**：
   - 结合价格变化、供需情况与新闻内容，给出简明扼要的总结，说明“价格变动的主要原因”。
   - 若信息不足，可以说明“目前缺乏足够数据判断价格变动原因”。

请根据以上步骤，分析以下问题并回答：
【{question}】
"""

# ========== LNG 到岸/送到价查询 ==========
@mcp.tool()
def get_lng_price(region: str, start_date: str, end_date: Optional[str] = None) -> List[Dict]:
    """
    获取指定地区从 start_date 到 end_date（默认今天）的每日 LNG 价格（模拟）。
    - 基于月度基准价 + 小幅波动。
    - 小幅波动由与 (region, start_date, end_date, 当天日期) 绑定的稳定 RNG 产生，
      确保相同查询在不同时间点/调用次数下结果一致。
    """
    if not region:
        return []
    if region not in SIMULATED_LNG_PRICES:
        # 不做 lower()，以免中文键丢失；如需别名映射可在此扩展
        return []

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.now() if not end_date else datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return []

    prices: List[Dict] = []
    current = start
    # 绑定“稳定随机”的 key：当日日期参与哈希，仅用于确保不同自然日的“同参同结果”
    today_key = datetime.now().strftime("%Y-%m-%d")
    rng = _stable_rng("lng_price_series", region, start_date, end_date or "None", today_key)

    while current <= end:
        month_key = current.strftime("%Y-%m")
        base_price = SIMULATED_LNG_PRICES[region].get(month_key, 4.0)
        daily_price = base_price + rng.uniform(-0.05, 0.05)  # 轻微波动，稳定 RNG 控制
        prices.append({
            "date": current.strftime("%Y-%m-%d"),
            "price": round(daily_price, 2)
        })
        current += timedelta(days=1)

    return prices

if __name__ == '__main__':
    mcp.run(transport="sse", host="127.0.0.1", port=9000)
    # 固定种子（可选）：不调用也会使用默认种子
    set_seed(20250422)
    # 示例1：查询最近3天内蒙古竞拍价 & 内蒙古工厂A/B出厂价
    today = datetime.now().date()
    start = (today - timedelta(days=2)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    print(get_auction_price("内蒙古", start, end))
    print(get_factory_prices(["内蒙古工厂A", "内蒙古工厂B"], start, end))

    # 示例2：查询浙江 2025-04-01 ~ 2025-04-07 的 LNG 价格（同参同结果）
    print(get_lng_price("浙江", "2025-04-01", "2025-04-07"))
