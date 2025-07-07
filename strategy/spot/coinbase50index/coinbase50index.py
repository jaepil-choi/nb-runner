import pandas as pd
import requests
from bs4 import BeautifulSoup

def strategy(df, config_dict):
    """
    Refer to https://www.marketvector.com/indexes/digital-assets/coinbase-50
    """

    # Get settings
    strategy_specific_config = config_dict.get('strategy_config')
    
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    symbol_weight = {
        # | Announcement | Implementation |
        # | ------------ | -------------- |
        # | 25/08/26     | 25/08/29       |
        ################################ 
        # Symbols with annotations are not currently supported by the Data API, so their prices are included in BTCUSDT.
        'BTCUSDT': '0.5461', # Origin BTCUSDT : 0.5109
        'ETHUSDT': '0.2274',
        'XRPUSDT': '0.0951',
        'SOLUSDT': '0.0562',
        'DOGEUSDT': '0.0190',
        'ADAUSDT': '0.0158',
        'BCHUSDT': '0.0073',
        # 'LINKUSDT': '0.0064',
        'XLMUSDT': '0.0058',
        'AVAXUSDT': '0.0056',
        # 'SHIBUSDT': '0.0051',
        'LTCUSDT': '0.0048',
        'DOTUSDT': '0.0042',
        # 'UNIUSDT': '0.0035',
        # 'PEPEUSDT': '0.0033',
        # 'AAVEUSDT': '0.0028',
        'APTUSDT': '0.0021',
        'ICPUSDT': '0.0020',
        'NEARUSDT': '0.0020',
        'ETCUSDT': '0.0019',
        'FETUSDT': '0.0013',
        # 'POLUSDT': '0.0013',
        # 'MKRUSDT': '0.0013',
        #'RENDERUSDT': '0.0012',
        'ATOMUSDT': '0.0012',
        'ALGOUSDT': '0.0011',
        # 'QNTUSDT': '0.0011',
        # 'INJUSDT': '0.0009',
        # 'BONKUSDT': '0.0008',
        # 'TIAUSDT': '0.0008',
        'STXUSDT': '0.0007',
        # 'CVXUSDT': '0.0007',
        # 'GRTUSDT': '0.0006',
        # 'CRVUSDT': '0.0006',
        # 'AEROUSDT': '0.0006',
        # 'LDOUSDT': '0.0005',
        # 'SANDUSDT': '0.0005',
        # 'JASMYUSDT': '0.0005',
        'XTZUSDT': '0.0004'
        # 'MANAUSDT': '0.0004',
        # 'APEUSDT': '0.0004',
        # 'COMPUSDT': '0.0003',
        # 'HNTUSDT': '0.0003',
        # 'AXSUSDT': '0.0003',
        # 'CHZUSDT': '0.0003',
        # '1INCHUSDT': '0.0002',
        # 'LPTUSDT': '0.0002',
        # 'SNXUSDT': '0.0002',
        # 'ROSEUSDT': '0.0001'
    }

    return symbol_weight|