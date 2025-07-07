# ==========================
# Required System Settings
# ==========================

system_config = {
    "data_apikey": "Input User Data Api Key", # CoinAPI - data api key
    "strategy_name": "multi_period_momentum", # User strategy file name
    "trading_hours": 72, # System run time
    "base_symbol": "BTCUSDT",
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
                'COTIUSDT', 'NTRNUSDT'], # List of all currently available symbols: define only the symbols you need as values.
    "productType": "usdt-futures",
    "posMode": "hedge_mode", # one_way_mode , hedge_mode
    "marginMode": "crossed", # isolated
    "holdSide": "long", # long , short
    "marginCoin": "usdt",
    "orderType": "market",
    "timeframe": "1min",
    "tradeType": "future", # future
    "is_portfolio": True,   
    "total_allocation": 1.0, # Proportion of total assets to use
    "leverage": 10, # Leverage
    "new_data_window": 60, # The window value for fetching the latest data (preferably the maximum value of the strategy parameter)
    "weight_method": "custom", # equal, split(long/short), custom
    "custom_weights": {    # Required if weight_method is custom
        "BTCUSDT" : "0.5",
        "ETHUSDT" : "0.3",
        "XRPUSDT" : "0.2"
    }    
}

# ==========================
# Rebalancing Trade Parameters
# ==========================

rebalancing_config = {
    "rebalancing_interval_hours": 3, # Rebalancing cycle (hours)
    "minimum_candidates": 0
}


# ==========================
# Strategy Parameter Settings
# ==========================

hours = [1,3,6]
strategy_config = {
    "long_maximum_candidates": 2,
    "short_maximum_candidates": 1,
    "minutes": [int(i*60) for i in hours]
}
