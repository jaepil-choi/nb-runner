# 策略指南
## 📘 如何实现自定义策略函数

本指南适用于对编程不熟悉的用户，  
将逐步讲解如何实现一个简单的自定义策略函数。  
你可以参考下面的例子，并按照相同的结构编写属于你自己的逻辑。

---

## ✅ 必须遵循的结构（固定规则）

- 函数名称必须为 `strategy`
- 函数的输入为：`df`, `config_dict`
- 函数的返回值为：`long_candidates`, `short_candidates`（必须是列表）
- 策略配置的访问方式如下：

```python
strategy_specific_config = config_dict.get('strategy_config')
```

你的策略参数应写在一个配置文件中，例如 `config.py`：

```python
# config.py 示例
hours = 12  # 小时为单位的时间段

strategy_config = {
    "maximum_candidates": 5,  # 多/空候选数量
    "minutes": 60 * hours     # 转换为分钟
}
```

> ⚠️ 系统会自动将上述 `strategy_config` 包装成 `config_dict`，以如下方式传入你的策略函数：

```python
longs, shorts = strategy.strategy(df, {'strategy_config': config.strategy_config})
```

你不需要手动构建 `config_dict`，只需按照上面的方式调用即可。

## 🧾 输入数据格式（`df`）

传入策略函数的 `df` 是一个时间序列价格的 DataFrame，包含以下内容：

- 索引（行）：每分钟的时间戳
- 列：资产名称（如 BTCUSDT, ETHUSDT 等）
- 值：每个时间点的收盘价格（浮点数）

示例：

| 时间               | BTCUSDT | ETHUSDT | XRPUSDT | ... |
|--------------------|---------|---------|---------|-----|
| 2025-04-13 00:00:00| 84817.0 | 1655.26 | 2.1568  | ... |
| 2025-04-13 00:01:00| 84836.7 | 1655.39 | 2.1565  | ... |
| 2025-04-13 00:02:00| 84891.7 | 1656.20 | 2.1593  | ... |

> ✅ 策略函数会使用这个 DataFrame 进行选股逻辑处理。

---

## 🪄 策略示例：基于简单收益率的策略

```python
# strategy.py
import pandas as pd

def strategy(df, config_dict):
    """
    一个简单的收益率策略：
    计算当前价格与 N 分钟前的价格相比的涨跌幅，
    选出涨幅最大和最小的资产。
    """
    strategy_specific_config = config_dict.get('strategy_config')

    period = strategy_specific_config.get("minutes")[0]  # 使用第一个时间段
    maximum_candidates = strategy_specific_config.get("maximum_candidates")

    returns = df.iloc[-1] / df.iloc[-period] - 1  # 计算简单收益率
    sorted_returns = returns.sort_values(ascending=False)

    long_candidates = list(sorted_returns.head(maximum_candidates).index)
    short_candidates = list(sorted_returns.tail(maximum_candidates).index)

    return long_candidates, short_candidates
```

---

## 🧱 策略验证测试示例（包含配置）

```python
# 1. config.py 示例
hours = 12

strategy_config = {
    "maximum_candidates": 5,
    "minutes": 60 * hours
}

# 2. strategy.py：包含上面的 strategy 函数

# 3. 执行方式（在 main.py 或 Jupyter Notebook 中）
import strategy
import config

# df 是系统提供的价格数据
df = get_price_data_somehow()
longs, shorts = strategy.strategy(df, {"strategy_config": config.strategy_config})

print("📈 多头候选:", longs)
print("📉 空头候选:", shorts)
```

---

## ✅ 期望输出格式

```python
📈 多头候选:
['BTCUSDT', 'ETHUSDT', 'XRPUSDT']

📉 空头候选:
['SOLUSDT', 'AVAXUSDT', 'DOGEUSDT']
```

---

## ❓ 小提示

- `df` 是由系统自动传入的，不需要你创建
- 返回结果必须是列表类型
- 若要创建更复杂的策略，可基于该模板进行扩展

---

# 🛠 config.py 配置模板

以下是一个最简配置文件示例：

```python
# config.py
# ==========================
# 系统必要设置
# ==========================

system_config = {
    "data_apikey": "Input User Data Api Key", # CoinAPI - 数据 API 密钥
    "strategy_name": "multi_period_momentum", # 用户策略文件名称
    "trading_hours": 72, # 系统运行时间（单位：小时）
    "base_symbol": "BTCUSDT", # 基准交易对
    "symbols": ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BCHUSDT', 'LTCUSDT', 
                'ADAUSDT', 'ETCUSDT', 'TRXUSDT', 'DOTUSDT', 'DOGEUSDT', 
                'SOLUSDT', 'BNBUSDT', 'ICPUSDT', 'FILUSDT', 'XLMUSDT',
                'ONTUSDT', 'QTUMUSDT', 'NKNUSDT', 'AVAXUSDT', 'CELOUSDT',
                'WAXPUSDT', 'DYMUSDT', 'APTUSDT', 'FLOWUSDT', 'GTCUSDT',
                'SEIUSDT', 'ATOMUSDT', 'NEARUSDT', 'STXUSDT', 'MINAUSDT',
                'BSVUSDT', 'EGLDUSDT', 'RVNUSDT', 'ONEUSDT', 'NEOUSDT',
                'JUPUSDT', 'ZILUSDT', 'XTZUSDT', 'LUNCUSDT', 'CKBUSDT',
                'IOTAUSDT', 'THETAUSDT', 'ICXUSDT', 'ALGOUSDT', 'LSKUSDT', 
                'CFXUSDT', 'TONUSDT', 'MEMEUSDT', 'SXPUSDT', 'KASUSDT',
                'HBARUSDT', 'IOSTUSDT', 'BEAMUSDT', 'FETUSDT', 'XVGUSDT', 
                'SUIUSDT', 'VETUSDT', 'KSMUSDT', 'ARBUSDT', 'ARUSDT', 
                'RUNEUSDT', 'IOTXUSDT', 'TAIKOUSDT', 'COREUSDT', 'BBUSDT', 
                'COTIUSDT', 'NTRNUSDT'], # 当前支持的交易对列表：仅填写需要的交易对
    "productType": "usdt-futures", # 产品类型：USDT合约
    "posMode": "hedge_mode", # 持仓模式：one_way_mode（单向）或 hedge_mode（双向）
    "marginMode": "crossed", # 保证金模式：全仓（hedge_mode + isolated时必须指定 holdSide）
    "holdSide": "long",      # 持仓方向：long 或 short（仅在 isolated + hedge_mode 模式下使用）
    "marginCoin": "usdt",    # 保证金币种
    "orderType": "market",   # 订单类型：市价单
    "timeframe": "1min",     # K线周期
    "tradeType": "future",   # 交易类型：合约
    "is_portfolio": True,    # 是否使用投资组合方式交易
    "total_allocation": 1.0, # 使用的总资金比例（0~1之间）
    "leverage": 10,          # 杠杆倍数
    "new_data_window": 60,   # 获取最新数据的时间窗口（建议设为策略参数的最大值）
    "weight_method": "custom", # 权重分配方式：equal、split 或 custom
    "custom_weights": {         # 当 weight_method 为 custom 时必须填写
        "BTCUSDT" : "0.5",
        "ETHUSDT" : "0.3",
        "XRPUSDT" : "0.2"
    }    
}

# ==========================
# 调仓参数设置
# ==========================

rebalancing_config = {
    "rebalancing_interval_hours": 3, # 调仓周期（小时）
    "minimum_candidates": 0          # 最少选中交易对数量
}

# ==========================
# 策略参数设置
# ==========================

hours = 12
strategy_config = {
    "maximum_candidates": 5, # 最多选中交易对数量
    "minutes": 60 * hours    # 策略运行时间（分钟）
}
```

✅ 系统会自动将 strategy_config 传入 strategy 函数
