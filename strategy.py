def calculate_strategies(technical):
    close = technical["Current_Price"]
    bb_low = technical["BB_Low"]
    bb_high = technical["BB_High"]
    rsi = technical["RSI"]
    macd = technical["MACD"]
    signal = technical["MACD_Signal"]
    atr = technical["ATR"]

    strategies = []

    # Strategy 1: 볼린저 밴드 하단 매수
    strategies.append({
        "name": "bollinger_lower",
        "score": 0.9 if close < bb_low else 0.2,
        "buy": round(bb_low, 2),
        "take_profit": round(bb_low + 2 * atr, 2),
        "stop_loss": round(bb_low - 1.5 * atr, 2),
    })

    # Strategy 2: RSI 과매도
    strategies.append({
        "name": "rsi_oversold",
        "score": 0.8 if rsi < 30 else 0.3,
        "buy": round(close * 0.98, 2),
        "take_profit": round(close * 1.03, 2),
        "stop_loss": round(close * 0.95, 2),
    })

    # Strategy 3: MACD 골든크로스
    strategies.append({
        "name": "macd_cross",
        "score": 0.85 if macd > signal else 0.2,
        "buy": round(close, 2),
        "take_profit": round(close * 1.04, 2),
        "stop_loss": round(close * 0.97, 2),
    })

    # Strategy 4: ATR 돌파 매매
    strategies.append({
        "name": "atr_breakout",
        "score": 0.7,
        "buy": round(close + atr, 2),
        "take_profit": round(close + 2 * atr, 2),
        "stop_loss": round(close, 2),
    })

    # Strategy 5: 스토캐스틱 과매도
    if "Stoch_K" in technical and "Stoch_D" in technical:
        stoch_k = technical["Stoch_K"]
        stoch_d = technical["Stoch_D"]
        score = 0.8 if stoch_k < 20 and stoch_k > stoch_d else 0.3
    else:
        score = 0.0
    strategies.append({
        "name": "stochastic",
        "score": score,
        "buy": round(close * 0.99, 2),
        "take_profit": round(close * 1.03, 2),
        "stop_loss": round(close * 0.96, 2),
    })

    return strategies