from mcp.server.fastmcp import FastMCP, Context, Image
import json
import os
from datetime import datetime, timedelta
import random
import io
from typing import Dict, List, Optional
import urllib.parse  # 添加 URL 解碼庫

# 嘗試導入 matplotlib，但提供備選方案
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("警告：未安裝 matplotlib，將使用文字圖表替代")

# 創建一個 MCP 服務器
mcp = FastMCP("蔬果價格查詢")

# 模擬價格數據
FRUITS = {
    "apple": {
        "zh_name": "蘋果",
        "current_price": 35.5,  # 每公斤價格（台幣）
        "unit": "公斤",
        "prices": []  # 最近 30 天的價格將在初始化時生成
    },
    "banana": {
        "zh_name": "香蕉",
        "current_price": 28.0,  # 每公斤價格（台幣）
        "unit": "公斤",
        "prices": []  # 最近 30 天的價格將在初始化時生成
    }
}

# 創建中文名稱到英文名稱的映射
ZH_TO_EN = {
    "蘋果": "apple",
    "苹果": "apple",  # 簡體字也支援
    "香蕉": "banana"
}

# 生成過去 30 天的價格數據
for fruit in FRUITS.values():
    base_price = fruit["current_price"]
    today = datetime.now()
    
    # 為每一天生成價格
    for i in range(30):
        day = today - timedelta(days=29-i)
        # 隨機波動，但保持在 ±15% 範圍內
        price = base_price * (1 + random.uniform(-0.15, 0.15))
        fruit["prices"].append({
            "date": day.strftime("%Y-%m-%d"),
            "price": round(price, 1)
        })
    
    # 確保最後一天的價格是當前價格
    fruit["prices"][-1]["price"] = base_price

# 查找蔬果的輔助函數（支援中英文名稱，包括 URL 編碼處理）
def get_fruit_key(fruit_name: str) -> str:
    """根據中文或英文名稱獲取英文鍵值
    
    Args:
        fruit_name: 蔬果名稱（中文或英文，可能是 URL 編碼的）
    
    Returns:
        英文鍵值或 None
    """
    # 嘗試 URL 解碼，以支援 URL 編碼的中文名稱
    try:
        decoded_name = urllib.parse.unquote(fruit_name)
        if decoded_name != fruit_name:
            print(f"解碼 URL 編碼的名稱：{fruit_name} -> {decoded_name}")
            fruit_name = decoded_name
    except Exception as e:
        print(f"URL 解碼失敗：{e}")
    
    fruit_name = fruit_name.lower()
    
    # 直接匹配英文名稱
    if fruit_name in FRUITS:
        return fruit_name
    
    # 查找中文名稱映射
    if fruit_name in ZH_TO_EN:
        return ZH_TO_EN[fruit_name]
    
    return None

# 創建標準表格格式的函數
def create_table(dates, prices, title="價格表", sample_size=10):
    """創建標準表格格式
    
    Args:
        dates: 日期列表
        prices: 價格列表
        title: 表格標題
        sample_size: 要顯示的數據點數量
        
    Returns:
        表格字符串
    """
    if not dates or not prices:
        return "無數據可顯示"
    
    # 選擇均勻分佈的樣本點
    sample_indices = []
    if len(dates) <= sample_size:
        sample_indices = list(range(len(dates)))
    else:
        step = len(dates) / sample_size
        for i in range(sample_size):
            sample_indices.append(int(i * step))
        # 確保包含最後一個點
        if sample_indices[-1] != len(dates) - 1:
            sample_indices[-1] = len(dates) - 1
    
    # 創建表頭
    table = f"【{title}】\n"
    table += "+--------------+--------------+\n"
    table += "| 日期         | 價格 (元/公斤) |\n"
    table += "+--------------+--------------+\n"
    
    # 添加數據行
    for i in sample_indices:
        date = dates[i]
        price = prices[i]
        table += f"| {date} | {price:12.1f} |\n"
    
    table += "+--------------+--------------+\n"
    
    # 添加價格趨勢描述
    price_trend = _get_price_trend_description(prices)
    table += f"價格趨勢: {price_trend}\n"
    
    return table

# 創建價格比較表格
def create_comparison_table(dates, prices1, prices2, fruit1_name, fruit2_name, sample_size=8):
    """創建兩種蔬果價格比較表格
    
    Args:
        dates: 日期列表
        prices1: 第一種蔬果價格列表
        prices2: 第二種蔬果價格列表
        fruit1_name: 第一種蔬果名稱
        fruit2_name: 第二種蔬果名稱
        sample_size: 要顯示的數據點數量
        
    Returns:
        比較表格字符串
    """
    if not dates or not prices1 or not prices2:
        return "無數據可顯示"
    
    # 選擇均勻分佈的樣本點
    sample_indices = []
    if len(dates) <= sample_size:
        sample_indices = list(range(len(dates)))
    else:
        step = len(dates) / sample_size
        for i in range(sample_size):
            sample_indices.append(int(i * step))
        # 確保包含最後一個點
        if sample_indices[-1] != len(dates) - 1:
            sample_indices[-1] = len(dates) - 1
    
    # 創建表頭
    table = f"【{fruit1_name} vs {fruit2_name} 價格比較】\n"
    table += "+--------------+--------------+--------------+--------------+\n"
    table += f"| 日期         | {fruit1_name:12} | {fruit2_name:12} | 差異 (元/公斤) |\n"
    table += "+--------------+--------------+--------------+--------------+\n"
    
    # 添加數據行
    for i in sample_indices:
        date = dates[i]
        price1 = prices1[i]
        price2 = prices2[i]
        diff = price1 - price2
        table += f"| {date} | {price1:12.1f} | {price2:12.1f} | {diff:+12.1f} |\n"
    
    table += "+--------------+--------------+--------------+--------------+\n"
    
    # 添加總結
    avg_price1 = sum(prices1) / len(prices1)
    avg_price2 = sum(prices2) / len(prices2)
    avg_diff = avg_price1 - avg_price2
    
    table += f"平均價格:       | {avg_price1:12.1f} | {avg_price2:12.1f} | {avg_diff:+12.1f} |\n"
    table += "+--------------+--------------+--------------+--------------+\n"
    
    return table

# 價格趨勢的文字描述函數
def _get_price_trend_description(prices):
    """根據價格數據提供趨勢描述
    
    Args:
        prices: 價格列表
        
    Returns:
        趨勢描述字符串
    """
    if len(prices) < 2:
        return "數據不足以分析趨勢"
    
    # 計算價格變化
    changes = []
    for i in range(1, len(prices)):
        changes.append(prices[i] - prices[i-1])
    
    # 計算上漲、下跌和持平的次數
    up_count = sum(1 for change in changes if change > 0)
    down_count = sum(1 for change in changes if change < 0)
    flat_count = sum(1 for change in changes if change == 0)
    
    # 計算起始和結束價格的變化
    start_price = prices[0]
    end_price = prices[-1]
    total_change = end_price - start_price
    percent_change = (total_change / start_price) * 100
    
    # 生成描述
    description = ""
    
    # 總體趨勢
    if percent_change > 10:
        description += "大幅上漲"
    elif percent_change > 5:
        description += "明顯上漲"
    elif percent_change > 0:
        description += "小幅上漲"
    elif percent_change < -10:
        description += "大幅下跌"
    elif percent_change < -5:
        description += "明顯下跌"
    elif percent_change < 0:
        description += "小幅下跌"
    else:
        description += "基本持平"
    
    description += f" ({percent_change:+.1f}%)"
    
    # 波動情況
    if up_count > 0.7 * len(changes):
        description += "，持續上漲趨勢"
    elif down_count > 0.7 * len(changes):
        description += "，持續下跌趨勢"
    elif up_count > down_count and up_count > flat_count:
        description += "，有波動但總體向上"
    elif down_count > up_count and down_count > flat_count:
        description += "，有波動但總體向下"
    else:
        description += "，波動較大"
    
    return description

# 獲取蔬果列表的資源
@mcp.resource("fruits://list")
def list_fruits() -> str:
    """獲取所有可查詢的蔬果列表"""
    result = "可查詢的蔬果：\n"
    result += "+----------+--------------+--------------+\n"
    result += "| 蔬果名稱 | 英文名稱     | 目前價格     |\n"
    result += "+----------+--------------+--------------+\n"
    
    for key, fruit in FRUITS.items():
        result += f"| {fruit['zh_name']:8} | {key:12} | {fruit['current_price']:10.1f} 元/{fruit['unit']} |\n"
    
    result += "+----------+--------------+--------------+\n"
    result += "\n您可以通過以下方式查詢詳細資訊：\n"
    result += "1. 讀取資源: fruits://蘋果 或 fruits://apple\n"
    result += "2. 使用工具: get_price_chart、compare_prices 或 analyze_price_trend\n"
    
    return result

# 獲取特定蔬果資訊的資源
@mcp.resource("fruits://{fruit_name}")
def get_fruit_info(fruit_name: str) -> str:
    """獲取特定蔬果的基本資訊
    
    Args:
        fruit_name: 蔬果名稱（中文或英文，如 apple、蘋果、banana、香蕉）
    
    Returns:
        蔬果資訊
    """
    fruit_key = get_fruit_key(fruit_name)
    if not fruit_key:
        return f"找不到 {fruit_name} 的資訊，支援的蔬果有：" + "、".join([f"{f['zh_name']}({k})" for k, f in FRUITS.items()])
    
    fruit = FRUITS[fruit_key]
    prices_data = [item["price"] for item in fruit["prices"]]
    dates = [item["date"] for item in fruit["prices"]]
    
    result = f"【{fruit['zh_name']}】基本資訊\n\n"
    result += f"目前價格: {fruit['current_price']} 元/{fruit['unit']}\n"
    result += f"30天最高價: {max(prices_data)} 元/{fruit['unit']}\n"
    result += f"30天最低價: {min(prices_data)} 元/{fruit['unit']}\n"
    result += f"30天平均價: {sum(prices_data)/len(prices_data):.1f} 元/{fruit['unit']}\n"
    result += f"近期走勢: {_price_trend_description(fruit['prices'])}\n\n"
    
    # 添加標準表格
    result += create_table(dates, prices_data, f"{fruit['zh_name']}過去30天價格表")
    
    return result

# 獲取特定蔬果價格走勢圖的工具
@mcp.tool()
def get_price_chart(fruit_name: str, days: int = 30) -> str:
    """獲取特定蔬果的價格走勢圖
    
    Args:
        fruit_name: 蔬果名稱（中文或英文，如 apple、蘋果、banana、香蕉）
        days: 要顯示的天數，最多30天
    
    Returns:
        價格走勢圖（表格版）
    """
    fruit_key = get_fruit_key(fruit_name)
    if not fruit_key:
        return f"找不到 {fruit_name} 的資訊，支援的蔬果有：" + "、".join([f"{f['zh_name']}({k})" for k, f in FRUITS.items()])
    
    fruit = FRUITS[fruit_key]
    zh_name = fruit['zh_name']
    
    # 限制天數最多 30 天
    days = min(days, 30)
    
    # 獲取價格數據
    price_data = fruit["prices"][-days:]
    dates = [item["date"] for item in price_data]
    prices = [item["price"] for item in price_data]
    
    # 計算重要統計數據
    current_price = prices[-1]
    avg_price = sum(prices) / len(prices)
    max_price = max(prices)
    min_price = min(prices)
    max_change = max([abs(prices[i] - prices[i-1]) for i in range(1, len(prices))])
    
    # 生成詳細報告
    result = f"【{zh_name}過去{days}天價格分析】\n\n"
    
    # 統計摘要
    result += "價格統計摘要：\n"
    result += "+----------------+----------------+\n"
    result += "| 指標           | 數值           |\n"
    result += "+----------------+----------------+\n"
    result += f"| 當前價格       | {current_price:14.1f} |\n"
    result += f"| 平均價格       | {avg_price:14.1f} |\n"
    result += f"| 最高價格       | {max_price:14.1f} |\n"
    result += f"| 最低價格       | {min_price:14.1f} |\n"
    result += f"| 最大單日波動   | {max_change:14.1f} |\n"
    result += "+----------------+----------------+\n\n"
    
    # 添加詳細價格表
    result += "詳細價格數據（採樣顯示）：\n"
    result += create_table(dates, prices, f"{zh_name}價格表", sample_size=10)
    
    # 添加價格變化描述
    change_from_start = prices[-1] - prices[0]
    percent_change = (change_from_start / prices[0]) * 100
    
    result += f"\n價格走勢描述：\n"
    result += f"- 從 {dates[0]} 到 {dates[-1]} 期間，{zh_name}價格"
    
    if change_from_start > 0:
        result += f"上漲了 {change_from_start:.1f} 元 (+{percent_change:.1f}%)"
    elif change_from_start < 0:
        result += f"下跌了 {-change_from_start:.1f} 元 ({percent_change:.1f}%)"
    else:
        result += "保持不變"
    
    result += "。\n"
    
    # 添加波動分析
    above_avg = sum(1 for p in prices if p > avg_price)
    below_avg = sum(1 for p in prices if p < avg_price)
    
    result += f"- 在這 {days} 天中，價格有 {above_avg} 天高於平均價，{below_avg} 天低於平均價。\n"
    
    # 週期性變化分析
    if days >= 14:
        week1_avg = sum(prices[:7]) / 7
        week2_avg = sum(prices[7:14]) / 7
        week_change = ((week2_avg / week1_avg) - 1) * 100
        
        result += f"- 第二週較第一週平均價格變化：{week_change:+.1f}%\n"
    
    if days >= 21:
        week3_avg = sum(prices[14:21]) / 7
        result += f"- 第三週較第二週平均價格變化：{((week3_avg / week2_avg) - 1) * 100:+.1f}%\n"
    
    # 預測趨勢
    if percent_change > 5:
        result += "- 預測：若當前趨勢持續，短期內價格可能繼續上漲。\n"
    elif percent_change < -5:
        result += "- 預測：若當前趨勢持續，短期內價格可能繼續下跌。\n"
    else:
        result += "- 預測：價格可能在當前水平附近波動。\n"
    
    return result

# 比較兩種蔬果價格的工具
@mcp.tool()
def compare_prices(fruit1: str, fruit2: str, days: int = 30) -> str:
    """比較兩種蔬果的價格走勢
    
    Args:
        fruit1: 第一種蔬果名稱（中文或英文，如 apple、蘋果）
        fruit2: 第二種蔬果名稱（中文或英文，如 banana、香蕉）
        days: 要比較的天數，最多30天
    
    Returns:
        比較結果（表格版）
    """
    fruit_key1 = get_fruit_key(fruit1)
    fruit_key2 = get_fruit_key(fruit2)
    
    if not fruit_key1 or not fruit_key2:
        error_msg = []
        if not fruit_key1:
            error_msg.append(f"找不到 {fruit1} 的資訊")
        if not fruit_key2:
            error_msg.append(f"找不到 {fruit2} 的資訊")
        error_msg.append("支援的蔬果有：" + "、".join([f"{f['zh_name']}({k})" for k, f in FRUITS.items()]))
        return "\n".join(error_msg)
    
    # 限制天數最多 30 天
    days = min(days, 30)
    
    # 獲取價格數據
    price_data1 = FRUITS[fruit_key1]["prices"][-days:]
    price_data2 = FRUITS[fruit_key2]["prices"][-days:]
    
    dates = [item["date"] for item in price_data1]
    prices1 = [item["price"] for item in price_data1]
    prices2 = [item["price"] for item in price_data2]
    
    fruit1_name = FRUITS[fruit_key1]["zh_name"]
    fruit2_name = FRUITS[fruit_key2]["zh_name"]
    
    # 計算價格差異
    current_diff = prices1[-1] - prices2[-1]
    avg_diff = sum(p1 - p2 for p1, p2 in zip(prices1, prices2)) / len(prices1)
    
    # 生成比較報告
    result = f"【{fruit1_name} vs {fruit2_name} 價格比較分析】\n\n"
    
    # 總結數據
    result += "價格比較摘要：\n"
    result += "+----------------+----------------+----------------+----------------+\n"
    result += f"| 指標           | {fruit1_name:14} | {fruit2_name:14} | 差異           |\n"
    result += "+----------------+----------------+----------------+----------------+\n"
    result += f"| 當前價格       | {prices1[-1]:14.1f} | {prices2[-1]:14.1f} | {current_diff:+14.1f} |\n"
    result += f"| 平均價格       | {sum(prices1)/len(prices1):14.1f} | {sum(prices2)/len(prices2):14.1f} | {avg_diff:+14.1f} |\n"
    result += f"| 最高價格       | {max(prices1):14.1f} | {max(prices2):14.1f} | {max(prices1)-max(prices2):+14.1f} |\n"
    result += f"| 最低價格       | {min(prices1):14.1f} | {min(prices2):14.1f} | {min(prices1)-min(prices2):+14.1f} |\n"
    result += "+----------------+----------------+----------------+----------------+\n\n"
    
    # 添加價格比較表格
    result += "價格對比詳細數據：\n"
    result += create_comparison_table(dates, prices1, prices2, fruit1_name, fruit2_name)
    
    # 添加比較分析
    result += f"\n價格比較分析：\n"
    
    # 價格差異分析
    if current_diff > 0:
        result += f"- 目前 {fruit1_name} 比 {fruit2_name} 貴 {current_diff:.1f} 元 ({(current_diff/prices2[-1])*100:.1f}%)。\n"
    else:
        result += f"- 目前 {fruit1_name} 比 {fruit2_name} 便宜 {-current_diff:.1f} 元 ({(current_diff/prices2[-1])*100:.1f}%)。\n"
    
    # 價格趨勢比較
    f1_change = ((prices1[-1] / prices1[0]) - 1) * 100
    f2_change = ((prices2[-1] / prices2[0]) - 1) * 100
    
    result += f"- {fruit1_name}過去{days}天價格變化：{f1_change:+.1f}%\n"
    result += f"- {fruit2_name}過去{days}天價格變化：{f2_change:+.1f}%\n"
    
    # 相關性分析
    if (f1_change > 0 and f2_change > 0) or (f1_change < 0 and f2_change < 0):
        result += f"- 兩種蔬果價格走勢方向一致，但 {fruit1_name if abs(f1_change) > abs(f2_change) else fruit2_name} 變化幅度更大。\n"
    else:
        result += f"- 兩種蔬果價格走勢方向相反，{fruit1_name} {('上漲' if f1_change > 0 else '下跌')}而 {fruit2_name} {('下跌' if f2_change > 0 else '上漲')}。\n"
    
    # 購買建議
    result += "\n購買建議：\n"
    if current_diff < 0:
        result += f"- 如果口味偏好相近，目前 {fruit1_name} 性價比更高。\n"
    else:
        result += f"- 如果口味偏好相近，目前 {fruit2_name} 性價比更高。\n"
    
    if f1_change < 0 and f1_change < f2_change:
        result += f"- {fruit1_name}價格正在下跌，可能是較好的購買時機。\n"
    elif f2_change < 0 and f2_change < f1_change:
        result += f"- {fruit2_name}價格正在下跌，可能是較好的購買時機。\n"
    
    return result

# 獲取價格走勢分析的工具
@mcp.tool()
def analyze_price_trend(fruit_name: str) -> str:
    """獲取特定蔬果的價格走勢分析
    
    Args:
        fruit_name: 蔬果名稱（中文或英文，如 apple、蘋果、banana、香蕉）
    
    Returns:
        價格走勢分析報告
    """
    fruit_key = get_fruit_key(fruit_name)
    if not fruit_key:
        return f"找不到 {fruit_name} 的資訊，支援的蔬果有：" + "、".join([f"{f['zh_name']}({k})" for k, f in FRUITS.items()])
    
    fruit = FRUITS[fruit_key]
    prices_data = fruit["prices"]
    prices = [item["price"] for item in prices_data]
    dates = [item["date"] for item in prices_data]
    
    # 計算平均價格
    avg_price = sum(prices) / len(prices)
    
    # 計算環比變化
    current_price = prices[-1]
    week_ago_price = prices[-8] if len(prices) >= 8 else prices[0]
    two_weeks_ago_price = prices[-15] if len(prices) >= 15 else prices[0]
    month_ago_price = prices[0]
    
    week_change = ((current_price / week_ago_price) - 1) * 100
    two_weeks_change = ((current_price / two_weeks_ago_price) - 1) * 100
    month_change = ((current_price / month_ago_price) - 1) * 100
    
    # 計算波動性（標準差）
    variance = sum((price - avg_price) ** 2 for price in prices) / len(prices)
    std_dev = variance ** 0.5
    volatility = (std_dev / avg_price) * 100
    
    # 判斷趨勢
    trend_description = _price_trend_description(prices_data)
    
    # 組合報告
    report = f"【{fruit['zh_name']}價格分析報告】\n\n"
    
    # 基本統計表
    report += "價格基本統計：\n"
    report += "+----------------+----------------+\n"
    report += "| 指標           | 數值           |\n"
    report += "+----------------+----------------+\n"
    report += f"| 當前價格       | {current_price:14.1f} |\n"
    report += f"| 30天平均價格   | {avg_price:14.1f} |\n"
    report += f"| 30天最高價格   | {max(prices):14.1f} |\n"
    report += f"| 30天最低價格   | {min(prices):14.1f} |\n"
    report += f"| 價格波動性     | {volatility:14.1f}% |\n"
    report += "+----------------+----------------+\n\n"
    
    # 環比變化表
    report += "價格環比變化：\n"
    report += "+----------------+----------------+\n"
    report += "| 時間範圍       | 變化百分比     |\n"
    report += "+----------------+----------------+\n"
    report += f"| 一週環比       | {week_change:+14.1f}% |\n"
    report += f"| 兩週環比       | {two_weeks_change:+14.1f}% |\n"
    report += f"| 月度環比       | {month_change:+14.1f}% |\n"
    report += "+----------------+----------------+\n\n"
    
    # 添加詳細價格表格
    report += "30天價格數據（採樣顯示）：\n"
    report += create_table(dates, prices, f"{fruit['zh_name']}價格表")
    
    # 價格趨勢描述
    report += f"\n價格趨勢分析：\n"
    report += f"- 總體趨勢：{trend_description}\n"
    
    # 分段趨勢分析
    if len(prices) >= 21:
        early_prices = prices[:10]
        mid_prices = prices[10:20]
        late_prices = prices[20:]
        
        early_avg = sum(early_prices) / len(early_prices)
        mid_avg = sum(mid_prices) / len(mid_prices)
        late_avg = sum(late_prices) / len(late_prices)
        
        report += "- 分段趨勢分析：\n"
        report += f"  * 初期（{dates[0]} ~ {dates[9]}）：平均價格 {early_avg:.1f} 元\n"
        report += f"  * 中期（{dates[10]} ~ {dates[19]}）：平均價格 {mid_avg:.1f} 元，較初期變化 {((mid_avg/early_avg)-1)*100:+.1f}%\n"
        report += f"  * 後期（{dates[20]} ~ {dates[-1]}）：平均價格 {late_avg:.1f} 元，較中期變化 {((late_avg/mid_avg)-1)*100:+.1f}%\n"
    
    # 預測分析
    report += "\n市場預測：\n"
    
    if week_change > 5:
        prediction = "- 短期趨勢：價格處於上漲通道，短期內可能繼續上漲"
    elif week_change < -5:
        prediction = "- 短期趨勢：價格處於下跌通道，短期內可能繼續下跌"
    else:
        prediction = "- 短期趨勢：價格相對穩定，短期內可能在當前水平波動"
    
    report += prediction + "\n"
    
    # 波動性分析
    if volatility > 10:
        report += "- 波動分析：價格波動較大，市場不確定性高\n"
    elif volatility > 5:
        report += "- 波動分析：價格波動適中，屬於正常市場波動\n"
    else:
        report += "- 波動分析：價格波動較小，市場相對穩定\n"
    
    # 購買建議
    report += "- 購買建議："
    if week_change < -3:
        report += "價格趨勢向下，可能是合適的購買時機\n"
    elif week_change > 3:
        report += "價格趨勢向上，可考慮等待價格回落後再購買\n"
    else:
        report += "價格相對穩定，可根據需要購買\n"
    
    return report

# 輔助函數：分析價格趨勢並返回描述
def _price_trend_description(prices):
    if len(prices) < 2:
        return "數據不足以分析趨勢"
    
    # 計算最近7天的趨勢
    recent_prices = prices[-7:] if len(prices) >= 7 else prices
    price_changes = [recent_prices[i+1]["price"] - recent_prices[i]["price"] for i in range(len(recent_prices)-1)]
    
    # 判斷趨勢
    up_changes = sum(1 for change in price_changes if change > 0)
    down_changes = sum(1 for change in price_changes if change < 0)
    flat_changes = len(price_changes) - up_changes - down_changes
    
    if up_changes > len(price_changes) * 0.65:
        return "明顯上漲趨勢"
    elif down_changes > len(price_changes) * 0.65:
        return "明顯下跌趨勢"
    elif up_changes > down_changes and up_changes > flat_changes:
        return "輕微上漲趨勢"
    elif down_changes > up_changes and down_changes > flat_changes:
        return "輕微下跌趨勢"
    else:
        return "價格相對穩定"

if __name__ == "__main__":
    mcp.run()