# 전략 가이드
## 📘 나만의 전략 함수 만들기

이 가이드는 코딩에 익숙하지 않은 사용자도 쉽게 따라 할 수 있도록 설계되었습니다.  
단계별로 전략 함수를 만드는 과정을 설명하며, 아래 예제를 참고해 같은 구조로 자신만의 전략을 만들 수 있습니다.

---

## ✅ 필수 구조 (고정 규칙)

- 함수 이름은 반드시 `strategy` 여야 합니다
- 함수 입력값: `df`, `config_dict`
- 함수 반환값: `long_candidates`, `short_candidates` (둘 다 리스트여야 함)
- 설정(config)은 다음과 같이 접근해야 합니다:

```python
strategy_specific_config = config_dict.get('strategy_config')
```

전략 설정은 다음과 같이 별도 파일 (예: config.py) 에 정의되어야 합니다:

```python
# config.py 예시
hours = 12  # 시간 단위

strategy_config = {
    "maximum_candidates": 5,  # 상하위 자산 개수
    "minutes": 60*hours       # 분 단위로 변환
}
```

> ⚠️ 시스템이 이 strategy_config를 config_dict로 감싸서 아래와 같이 전달합니다:

```python
longs, shorts = strategy.strategy(df, {'strategy_config': config.strategy_config})
```

사용자가 config_dict를 직접 만들 필요는 없습니다—위와 같이 호출만 하면 됩니다.

---

## 🧾 입력 데이터 구조 (`df`)

전략 함수로 들어오는 `df`는 시계열 가격 데이터프레임입니다:

- 인덱스: 분 단위 타임스탬프
- 컬럼: 자산 이름 (예: BTCUSDT, ETHUSDT 등)
- 값: 각 시점의 종가 (float)

예시 구조:

| 시간               | BTCUSDT | ETHUSDT | XRPUSDT | ... |
|--------------------|---------|---------|---------|-----|
| 2025-04-13 00:00:00| 84817.0 | 1655.26 | 2.1568  | ... |
| 2025-04-13 00:01:00| 84836.7 | 1655.39 | 2.1565  | ... |
| 2025-04-13 00:02:00| 84891.7 | 1656.20 | 2.1593  | ... |

> ✅ 전략 함수는 이 DataFrame을 기반으로 종목을 선택합니다.

---

## 🪄 전략 예시: 단순 수익률 기반 전략

```python
# strategy.py
import pandas as pd

def strategy(df, config_dict):
    """
    단순 수익률 기반 전략 예제.
    최신 가격과 N분 전 가격을 비교하여
    수익률이 가장 높은 자산을 long, 낮은 자산을 short로 선택합니다.
    """
    strategy_specific_config = config_dict.get('strategy_config')

    period = strategy_specific_config.get("minutes")[0]  # 첫 번째 값만 사용
    maximum_candidates = strategy_specific_config.get("maximum_candidates")

    returns = df.iloc[-1] / df.iloc[-period] - 1  # 단순 수익률 계산
    sorted_returns = returns.sort_values(ascending=False)

    long_candidates = list(sorted_returns.head(maximum_candidates).index)
    short_candidates = list(sorted_returns.tail(maximum_candidates).index)

    return long_candidates, short_candidates
```

---

## 🧱 전략 검증 테스트 예시 (Config 포함)

```python
# 1. config.py 예시
hours = 12

strategy_config = {
    "maximum_candidates": 5,
    "minutes": 60 * hours
}

# 2. strategy.py: 위 전략 함수 포함

# 3. 실행 예시 (main.py 또는 Jupyter Notebook 등에서)
import strategy
import config

df = get_price_data_somehow()
longs, shorts = strategy.strategy(df, {"strategy_config": config.strategy_config})

print("📈 Long 종목:", longs)
print("📉 Short 종목:", shorts)
```

---

## ✅ 기대되는 출력 형식

```python
📈 Long 종목:
['BTCUSDT', 'ETHUSDT', 'XRPUSDT']

📉 Short 종목:
['SOLUSDT', 'AVAXUSDT', 'DOGEUSDT']
```

---

## ❓ 팁

- df는 시스템에서 자동으로 제공됩니다.
- 결과는 반드시 리스트 형태로 반환해야 합니다.
- 복잡한 전략은 이 예시를 기반으로 확장 가능합니다.


---

## 🛠 config.py 전체 예시 템플릿

```python
# config.py
# ==========================
# 필수 시스템 설정
# ==========================

system_config = {
    "data_apikey": "Input User Data Api Key", # CoinAPI - 데이터 API 키 입력
    "strategy_name": "multi_period_momentum", # 사용자 전략 파일 이름
    "trading_hours": 72, # 시스템 실행 시간 (단위: 시간)
    "base_symbol": "BTCUSDT", # 기준 종목
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
                'COTIUSDT', 'NTRNUSDT'], # 사용 가능한 전체 종목 리스트 중 필요한 종목만 선택
    "productType": "usdt-futures", # 상품 종류 (USDT 선물)
    "posMode": "hedge_mode", # 포지션 모드: one_way_mode(단방향), hedge_mode(양방향)
    "marginMode": "crossed", # 마진 모드: 교차마진 (hedge_mode + isolated일 때만 holdSide 필요)
    "holdSide": "long",      # 포지션 방향: long 또는 short (isolated + hedge_mode일 때만 사용됨)   
    "marginCoin": "usdt",    # 마진으로 사용할 코인
    "orderType": "market",   # 주문 유형: 시장가 주문
    "timeframe": "1min",     # 캔들 타임프레임
    "tradeType": "future",   # 거래 종류: 선물
    "is_portfolio": True,    # 포트폴리오 거래 여부
    "total_allocation": 1.0, # 총 자산 중 사용할 비율 (0~1)
    "leverage": 10,          # 레버리지 설정
    "new_data_window": 60,   # 최신 데이터 수집 윈도우 (전략 파라미터의 최대값에 맞추는 것이 좋음)
    "weight_method": "custom", # 종목별 비중 계산 방식: equal, split, custom 중 선택
    "custom_weights": {        # weight_method가 custom일 때 필수
        "BTCUSDT" : "0.5",
        "ETHUSDT" : "0.3",
        "XRPUSDT" : "0.2"
    }    
}

# ==========================
# 리밸런싱 트레이딩 설정
# ==========================

rebalancing_config = {
    "rebalancing_interval_hours": 3, # 리밸런싱 주기 (단위: 시간)
    "minimum_candidates": 0          # 리밸런싱 시 최소 종목 수
}

# ==========================
# 전략 파라미터 설정
# ==========================

hours = 12
strategy_config = {
    "maximum_candidates": 5, # 최대 선택 종목 수
    "minutes": 60 * hours    # 전략 실행 시간 (분 단위)
}
```

✅ strategy_config는 시스템이 자동으로 strategy 함수에 전달합니다.


