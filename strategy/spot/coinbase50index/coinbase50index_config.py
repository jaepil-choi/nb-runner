# ==========================
# Required System Settings
# ==========================

system_config = {
    "data_apikey": "Input your Data API key", # CoinAPI - data api key
    "strategy_name": "coinbase50index",
    "trading_hours": 336,
    "base_symbol": "BTCUSDT",
    "symbols": ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'SOLUSDT', 'DOGEUSDT', 'ADAUSDT', 'BCHUSDT', 'XLMUSDT', 'AVAXUSDT', 'LTCUSDT', 'DOTUSDT', 'APTUSDT', 'ICPUSDT', 'NEARUSDT', 'ETCUSDT', 'FETUSDT', 'ATOMUSDT', 'ALGOUSDT', 'STXUSDT', 'XTZUSDT'],
    "orderType": "market",
    "timeframe": "1min",
    "tradeType": "future",
    "is_portfolio": True,
    "total_allocation": 0.90,
    "new_data_window": 5,
    "batchMode": 'multiple'
}

# ==========================
# Rebalancing Trade Parameters
# ==========================

rebalancing_config = {
    "rebalancing_interval_hours": 72, # Rebalancing cycle (hours)
}


# ==========================
# Strategy Parameter Settings
# ==========================

strategy_config = {}
