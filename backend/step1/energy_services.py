#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/9/15 20:06
# @File  : energy_services.py.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 一体化的 LNG 价格信息

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

def regenerate_simulated_data(base_date: Optional[date] = None, days: int = 1000) -> None:
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
# ========== 工厂利润（模拟）相关：查询竞拍价与出厂价 ==========
@mcp.tool()
def get_auction_price(province: str, start_date: str, end_date: str) -> Dict[str, float]:
    """
    获取指定省份在指定日期范围内的原料气竞拍价格。
    返回示例，单位价格是每立方米/元
    {'2025-09-25': 3.06, '2025-09-26': 3.18, '2025-09-27': 3.1}
    """
    print(f"[接口] 查询竞拍价: 省份={province}, 范围={start_date}~{end_date}")
    s = _parse_date(start_date)
    e = _parse_date(end_date)
    if not s or not e or s > e:
        print("[接口] 日期格式错误或开始日期晚于结束日期。")
        return {}

    out: Dict[str, float] = {}
    if province in SIMULATED_AUCTION_PRICES:
        data = SIMULATED_AUCTION_PRICES[province]
        for d in _daterange(s, e):
            k = d.strftime("%Y-%m-%d")
            if k in data:
                out[k] = data[k]
    print(f"[接口] 返回条目数: {len(out)}")
    return out

@mcp.tool()
def get_factory_prices(factory_names: List[str], start_date: str, end_date: str) -> Dict[str, Dict[str, float]]:
    """
    获取指定工厂列表在指定日期范围内的出厂价格，单位每吨/元。
    返回示例输出：
    {'2025-09-25': {'内蒙古工厂A': 6124, '内蒙古工厂B': 5899}, '2025-09-26': {'内蒙古工厂A': 5898, '内蒙古工厂B': 5919}, '2025-09-27': {'内蒙古工厂A': 6069, '内蒙古工厂B': 6050}}
    """
    print(f"[接口] 查询出厂价: 工厂={factory_names}, 范围={start_date}~{end_date}")
    s = _parse_date(start_date)
    e = _parse_date(end_date)
    if not s or not e:
        print("[接口] 日期格式错误或开始日期晚于结束日期。")
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
    print(f"[接口] 返回天数: {len(out)}")
    return out

# ========== LNG 到岸/送到价查询 ==========
@mcp.tool()
def get_lng_price(region: str, start_date: str, end_date: Optional[str] = None) -> List[Dict]:
    """
    获取指定地区从 start_date 到 end_date（默认今天）的每日 LNG 价格。
    - 基于月度基准价 + 小幅波动。
    返回示例：
    [{'date': '2025-04-01', 'price': 4.55}, {'date': '2025-04-02', 'price': 4.53}, {'date': '2025-04-03', 'price': 4.55}, {'date': '2025-04-04', 'price': 4.49}, {'date': '2025-04-05', 'price': 4.46}, {'date': '2025-04-06', 'price': 4.53}, {'date': '2025-04-07', 'price': 4.5}]
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
    # 示例1：查询最近3天内蒙古竞拍价 & 内蒙古工厂A/B出厂价
    today = datetime.now().date()
    start = (today - timedelta(days=2)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    print(get_auction_price("内蒙古", start, end))
    print(get_factory_prices(["内蒙古工厂A", "内蒙古工厂B"], start, end))
    print(get_factory_prices(["河北工厂Y"], "2025-04-15", "2025-04-15"))

    # 示例2：查询浙江 2025-04-01 ~ 2025-04-07 的 LNG 价格（同参同结果）
    print(get_lng_price("浙江", "2022-01-01", "2022-01-07"))
