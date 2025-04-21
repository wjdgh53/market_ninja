from pprint import pprint

from strategy import calculate_strategies

# 기술 지표 입력 (예시)
sample_input = {
    "symbol": "TSLA",
    "Current_Price": 241.36,
    "BB_Low": 224.07,
    "BB_High": 292.18,
    "RSI": 43.56,
    "MACD": -9.18,
    "MACD_Signal": -10.22,
    "ATR": 21.89,
    "Stoch_K": 38.3,
    "Stoch_D": 42.7
}

results = calculate_strategies(sample_input)
pprint(results)