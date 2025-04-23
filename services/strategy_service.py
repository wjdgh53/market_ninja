import logging
from typing import Dict, Any, List
from datetime import datetime

# 로깅 설정
logger = logging.getLogger(__name__)

def analyze_strategy(indicators: Dict[str, Any]) -> Dict[str, Any]:
    """
    기술적 지표를 기반으로 매매 전략을 분석합니다.
    
    Args:
        indicators (Dict[str, Any]): 기술적 지표 데이터
        
    Returns:
        Dict[str, Any]: 전략 분석 결과
    """
    try:
        # 기본 결과 구조
        result = {
            "symbol": indicators.get("symbol", "Unknown"),
            "timestamp": datetime.now().isoformat(),
            "signals": [],
            "analysis": {},
            "recommendation": "HOLD"  # 기본값: 홀딩
        }
        
        # 1. RSI 분석
        rsi = indicators.get("rsi", 50)
        if rsi < 30:
            result["signals"].append("RSI_OVERSOLD")
            result["analysis"]["rsi"] = "과매도 상태"
        elif rsi > 70:
            result["signals"].append("RSI_OVERBOUGHT")
            result["analysis"]["rsi"] = "과매수 상태"
        else:
            result["analysis"]["rsi"] = "중립 상태"
            
        # 2. MACD 분석
        macd = indicators.get("macd", 0)
        macd_signal = indicators.get("macd_signal", 0)
        if macd > macd_signal:
            result["signals"].append("MACD_BULLISH")
            result["analysis"]["macd"] = "상승 추세"
        else:
            result["signals"].append("MACD_BEARISH")
            result["analysis"]["macd"] = "하락 추세"
            
        # 3. 볼린저 밴드 분석
        current_price = indicators.get("current_price", 0)
        bb_high = indicators.get("bb_high", 0)
        bb_low = indicators.get("bb_low", 0)
        
        if current_price > bb_high:
            result["signals"].append("BB_OVERBOUGHT")
            result["analysis"]["bollinger_bands"] = "상단 밴드 돌파"
        elif current_price < bb_low:
            result["signals"].append("BB_OVERSOLD")
            result["analysis"]["bollinger_bands"] = "하단 밴드 돌파"
        else:
            result["analysis"]["bollinger_bands"] = "밴드 내 위치"
            
        # 4. 이동평균선 분석
        sma_20 = indicators.get("sma_20", 0)
        sma_50 = indicators.get("sma_50", 0)
        sma_200 = indicators.get("sma_200", 0)
        
        if current_price > sma_20 and sma_20 > sma_50 and sma_50 > sma_200:
            result["signals"].append("MA_BULLISH")
            result["analysis"]["moving_averages"] = "강한 상승 추세"
        elif current_price < sma_20 and sma_20 < sma_50 and sma_50 < sma_200:
            result["signals"].append("MA_BEARISH")
            result["analysis"]["moving_averages"] = "강한 하락 추세"
        else:
            result["analysis"]["moving_averages"] = "혼합된 추세"
            
        # 5. 거래량 분석
        volume = indicators.get("volume", 0)
        volume_ema20 = indicators.get("volume_ema20", 0)
        if volume > volume_ema20:
            result["signals"].append("VOLUME_INCREASE")
            result["analysis"]["volume"] = "거래량 증가"
        else:
            result["analysis"]["volume"] = "거래량 감소"
            
        # 6. 스토캐스틱 분석
        stoch_k = indicators.get("stoch_k", 50)
        stoch_d = indicators.get("stoch_d", 50)
        if stoch_k > 80 and stoch_d > 80:
            result["signals"].append("STOCH_OVERBOUGHT")
            result["analysis"]["stochastic"] = "과매수 상태"
        elif stoch_k < 20 and stoch_d < 20:
            result["signals"].append("STOCH_OVERSOLD")
            result["analysis"]["stochastic"] = "과매도 상태"
        else:
            result["analysis"]["stochastic"] = "중립 상태"
            
        # 7. ADX 분석
        adx = indicators.get("adx", 0)
        if adx > 25:
            result["signals"].append("STRONG_TREND")
            result["analysis"]["adx"] = "강한 추세"
        else:
            result["analysis"]["adx"] = "약한 추세"
            
        # 8. 최종 매매 추천 결정
        bullish_signals = sum(1 for signal in result["signals"] if "BULLISH" in signal or "OVERSOLD" in signal)
        bearish_signals = sum(1 for signal in result["signals"] if "BEARISH" in signal or "OVERBOUGHT" in signal)
        
        if bullish_signals > bearish_signals:
            result["recommendation"] = "BUY"
        elif bearish_signals > bullish_signals:
            result["recommendation"] = "SELL"
        else:
            result["recommendation"] = "HOLD"
            
        # 9. 신뢰도 점수 계산 (0-100)
        total_signals = len(result["signals"])
        if total_signals > 0:
            confidence = (bullish_signals + bearish_signals) / total_signals * 100
        else:
            confidence = 0
        result["confidence"] = round(confidence, 2)
        
        return result
        
    except Exception as e:
        logger.error(f"전략 분석 중 오류 발생: {str(e)}")
        return {
            "error": str(e),
            "symbol": indicators.get("symbol", "Unknown"),
            "timestamp": datetime.now().isoformat()
        }

# 전략별 계산 함수들
def calculate_bollinger_strategy(current_price, bb_high, bb_low, bb_width):
    """볼린저 밴드 기반 전략 계산"""
    width = bb_width or 0.1  # 기본값 설정
    band_range = bb_high - bb_low
    
    # 기본값 설정
    signal = "HOLD"
    confidence = 0
    target_price = current_price
    stop_loss = current_price
    
    # 신호 로직
    if current_price <= bb_low:
        # 하단 밴드 터치 또는 이탈 시 매수 신호
        signal = "BUY"
        # 밴드 이탈 정도에 따른 신뢰도 계산
        penetration = max(0, (bb_low - current_price) / bb_low * 100)
        confidence = min(100, int(penetration * 2 + 50))
        
        # 목표가는 중앙 또는 상단 밴드
        target_price = current_price + band_range * 0.7
        # 손절가는 하단 밴드 추가 이탈
        stop_loss = current_price - (band_range * 0.2)
        
    elif current_price >= bb_high:
        # 상단 밴드 터치 또는 이탈 시 매도 신호
        signal = "SELL"
        # 밴드 이탈 정도에 따른 신뢰도 계산
        penetration = max(0, (current_price - bb_high) / bb_high * 100)
        confidence = min(100, int(penetration * 2 + 50))
        
        # 목표가는 중앙 또는 하단 밴드
        target_price = current_price - band_range * 0.7
        # 손절가는 상단 밴드 추가 이탈
        stop_loss = current_price + (band_range * 0.2)
    else:
        # 밴드 내에 있는 경우
        middle_band = (bb_high + bb_low) / 2
        if current_price > middle_band:
            # 중앙선 위에 있으면 약한 매도
            signal = "WEAK_SELL"
            target_price = bb_high
            stop_loss = bb_low
            confidence = int(((current_price - middle_band) / (bb_high - middle_band)) * 40) + 10
        else:
            # 중앙선 아래에 있으면 약한 매수
            signal = "WEAK_BUY"
            target_price = middle_band
            stop_loss = bb_low * 0.98
            confidence = int(((middle_band - current_price) / (middle_band - bb_low)) * 40) + 10
    
    return {
        "signal": signal,
        "confidence": confidence,
        "target_price": round(target_price, 2),
        "stop_loss": round(stop_loss, 2),
        "parameters": {
            "bb_high": bb_high,
            "bb_low": bb_low,
            "bb_width": bb_width
        }
    }

def calculate_macd_strategy(current_price, macd, macd_signal, macd_histogram):
    """MACD 기반 전략 계산"""
    # 기본값 설정
    signal = "HOLD"
    confidence = 0
    target_price = current_price
    stop_loss = current_price
    
    # 기본 상승/하락률 설정
    base_move_up = 0.03  # 기본 3% 상승
    base_move_down = 0.03  # 기본 3% 하락
    
    # 신호 로직
    if macd > macd_signal:
        # MACD가 시그널 라인을 상향 돌파 (매수 신호)
        signal = "BUY"
        # 매수 신호 강도 계산
        diff = macd - macd_signal
        diff_relative = diff / (abs(macd) + 0.0001)  # 0으로 나누기 방지
        
        # 신호 강도에 따른 신뢰도 및 목표가/손절가 조정
        confidence = min(100, int(diff_relative * 100) + 50)
        multiplier = min(2, max(1, 1 + diff_relative))
        
        target_price = current_price * (1 + base_move_up * multiplier)
        stop_loss = current_price * (1 - base_move_down * 0.7)
        
    elif macd < macd_signal:
        # MACD가 시그널 라인을 하향 돌파 (매도 신호)
        signal = "SELL"
        # 매도 신호 강도 계산
        diff = macd_signal - macd
        diff_relative = diff / (abs(macd) + 0.0001)  # 0으로 나누기 방지
        
        # 신호 강도에 따른 신뢰도 및 목표가/손절가 조정
        confidence = min(100, int(diff_relative * 100) + 50)
        multiplier = min(2, max(1, 1 + diff_relative))
        
        target_price = current_price * (1 - base_move_down * multiplier)
        stop_loss = current_price * (1 + base_move_up * 0.7)
    
    return {
        "signal": signal,
        "confidence": confidence,
        "target_price": round(target_price, 2),
        "stop_loss": round(stop_loss, 2),
        "parameters": {
            "macd": macd,
            "macd_signal": macd_signal,
            "macd_histogram": macd_histogram
        }
    }

def calculate_rsi_strategy(current_price, rsi, atr):
    """RSI 기반 전략 계산"""
    # 기본값 설정
    signal = "HOLD"
    confidence = 0
    target_price = current_price
    stop_loss = current_price
    
    # 기본 ATR 배수 설정
    atr_multiplier = 2.0
    
    # 신호 로직
    if rsi < 30:
        # 과매도 상태 (매수 신호)
        signal = "BUY"
        # 30에서의 거리에 따른 신뢰도 계산
        confidence = min(100, int((30 - rsi) * 3 + 50))
        
        # 목표가는 현재가 + ATR의 배수
        # RSI가 낮을수록 큰 반등 가능성
        rsi_factor = max(0.5, (30 - rsi) / 30)  # RSI가 0이면 1, 30이면 0.5
        target_price = current_price * (1 + (atr / current_price) * atr_multiplier * rsi_factor)
        
        # 손절가는 현재가 - ATR의 일부
        stop_loss = current_price * (1 - (atr / current_price) * 1.0)
        
    elif rsi > 70:
        # 과매수 상태 (매도 신호)
        signal = "SELL"
        # 70에서의 거리에 따른 신뢰도 계산
        confidence = min(100, int((rsi - 70) * 3 + 50))
        
        # 목표가는 현재가 - ATR의 배수
        # RSI가 높을수록 큰 하락 가능성
        rsi_factor = max(0.5, (rsi - 70) / 30)  # RSI가 100이면 1, 70이면 0.5
        target_price = current_price * (1 - (atr / current_price) * atr_multiplier * rsi_factor)
        
        # 손절가는 현재가 + ATR의 일부
        stop_loss = current_price * (1 + (atr / current_price) * 1.0)
        
    else:
        # 중립 상태
        if rsi > 50:
            # 50 이상은 약한 매도 신호
            signal = "WEAK_SELL"
            confidence = int((rsi - 50) * 2)
            target_price = current_price * (1 - (atr / current_price) * 1.0)
            stop_loss = current_price * (1 + (atr / current_price) * 0.7)
        else:
            # 50 미만은 약한 매수 신호
            signal = "WEAK_BUY"
            confidence = int((50 - rsi) * 2)
            target_price = current_price * (1 + (atr / current_price) * 1.0)
            stop_loss = current_price * (1 - (atr / current_price) * 0.7)
    
    return {
        "signal": signal,
        "confidence": confidence,
        "target_price": round(target_price, 2),
        "stop_loss": round(stop_loss, 2),
        "parameters": {
            "rsi": rsi,
            "atr_used": atr
        }
    }

def calculate_ma_strategy(current_price, sma_20, sma_50, sma_200, atr):
    """이동평균선 기반 전략 계산"""
    # 기본값 설정
    signal = "HOLD"
    confidence = 0
    target_price = current_price
    stop_loss = current_price
    
    # 기본 ATR 배수 설정
    atr_multiplier = 2.5
    
    # 이동평균선 배치 확인
    if current_price > sma_20 > sma_50 > sma_200:
        # 완전한 상승 추세 (강한 매수)
        signal = "BUY"
        confidence = 90
        
        # 추세 강도에 따른 목표가 설정
        trend_strength = (current_price / sma_200 - 1)
        target_price = current_price * (1 + (atr / current_price) * atr_multiplier)
        stop_loss = min(sma_20, current_price * (1 - (atr / current_price) * 0.8))
        
    elif current_price < sma_20 < sma_50 < sma_200:
        # 완전한 하락 추세 (강한 매도)
        signal = "SELL"
        confidence = 90
        
        # 추세 강도에 따른 목표가 설정
        trend_strength = (1 - current_price / sma_200)
        target_price = current_price * (1 - (atr / current_price) * atr_multiplier)
        stop_loss = max(sma_20, current_price * (1 + (atr / current_price) * 0.8))
        
    elif current_price > sma_20 and sma_20 < sma_50:
        # 잠재적 상승 반전 (약한 매수)
        signal = "WEAK_BUY"
        confidence = 60
        target_price = sma_50
        stop_loss = min(current_price * 0.95, sma_20 * 0.98)
        
    elif current_price < sma_20 and sma_20 > sma_50:
        # 잠재적 하락 반전 (약한 매도)
        signal = "WEAK_SELL"
        confidence = 60
        target_price = sma_50
        stop_loss = max(current_price * 1.05, sma_20 * 1.02)
        
    else:
        # 혼합된 신호
        if current_price > sma_50:
            # 중기적으로는 상승세
            signal = "WEAK_BUY"
            confidence = 40
            target_price = current_price * (1 + (atr / current_price) * 1.5)
            stop_loss = min(sma_50, current_price * (1 - (atr / current_price) * 0.5))
        else:
            # 중기적으로는 하락세
            signal = "WEAK_SELL"
            confidence = 40
            target_price = current_price * (1 - (atr / current_price) * 1.5)
            stop_loss = max(sma_50, current_price * (1 + (atr / current_price) * 0.5))
    
    return {
        "signal": signal,
        "confidence": confidence,
        "target_price": round(target_price, 2),
        "stop_loss": round(stop_loss, 2),
        "parameters": {
            "sma_20": sma_20,
            "sma_50": sma_50,
            "sma_200": sma_200
        }
    }

def calculate_consensus_target(current_price, recommendation, strategies, atr):
    """
    여러 전략의 목표가를 기반으로 합의된 목표가를 계산합니다.
    각 전략의 신뢰도를 가중치로 사용합니다.
    """
    if recommendation == "HOLD":
        # 홀딩 추천시에는 현재가 반환
        return current_price
    
    # 매수/매도 신호에 맞는 전략들만 필터링
    relevant_strategies = {}
    for name, strategy in strategies.items():
        if (recommendation == "BUY" and any(x in strategy["signal"] for x in ["BUY", "WEAK_BUY"])) or \
           (recommendation == "SELL" and any(x in strategy["signal"] for x in ["SELL", "WEAK_SELL"])):
            relevant_strategies[name] = strategy
    
    # 관련 전략이 없으면 ATR 기반 기본값 반환
    if not relevant_strategies:
        if recommendation == "BUY":
            return round(current_price * (1 + (atr / current_price) * 2.0), 2)
        else:  # SELL
            return round(current_price * (1 - (atr / current_price) * 2.0), 2)
    
    # 각 전략의 목표가와 신뢰도 기반 가중평균
    total_weight = 0
    weighted_sum = 0
    
    for name, strategy in relevant_strategies.items():
        confidence = strategy.get("confidence", 0)
        target_price = strategy.get("target_price", current_price)
        
        # 신뢰도가 높을수록 더 큰 가중치 부여
        weight = confidence
        total_weight += weight
        weighted_sum += target_price * weight
    
    # 가중평균 계산
    if total_weight > 0:
        return round(weighted_sum / total_weight, 2)
    else:
        # 가중치가 없는 경우 단순 평균
        avg_target = sum(s.get("target_price", current_price) for s in relevant_strategies.values()) / len(relevant_strategies)
        return round(avg_target, 2)

def calculate_consensus_stop_loss(current_price, recommendation, strategies, atr):
    """
    여러 전략의 손절가를 기반으로 합의된 손절가를 계산합니다.
    각 전략의 신뢰도를 가중치로 사용합니다.
    """
    if recommendation == "HOLD":
        # 홀딩 추천시에는 현재가의 3% 손실을 기본 손절가로 설정
        if atr:
            # ATR이 있으면 ATR의 1.5배를 손실폭으로 사용
            return round(current_price * (1 - (atr / current_price) * 1.5), 2)
        else:
            return round(current_price * 0.97, 2)
    
    # 매수/매도 신호에 맞는 전략들만 필터링
    relevant_strategies = {}
    for name, strategy in strategies.items():
        if (recommendation == "BUY" and any(x in strategy["signal"] for x in ["BUY", "WEAK_BUY"])) or \
           (recommendation == "SELL" and any(x in strategy["signal"] for x in ["SELL", "WEAK_SELL"])):
            relevant_strategies[name] = strategy
    
    # 관련 전략이 없으면 ATR 기반 기본값 반환
    if not relevant_strategies:
        if recommendation == "BUY":
            return round(current_price * (1 - (atr / current_price) * 1.0), 2)
        else:  # SELL
            return round(current_price * (1 + (atr / current_price) * 1.0), 2)
    
    # 각 전략의 손절가와 신뢰도 기반 가중평균
    total_weight = 0
    weighted_sum = 0
    
    for name, strategy in relevant_strategies.items():
        confidence = strategy.get("confidence", 0)
        stop_loss = strategy.get("stop_loss", current_price)
        
        # 신뢰도가 높을수록 더 큰 가중치 부여
        weight = confidence
        total_weight += weight
        weighted_sum += stop_loss * weight
    
    # 가중평균 계산
    if total_weight > 0:
        return round(weighted_sum / total_weight, 2)
    else:
        # 가중치가 없는 경우 단순 평균
        avg_stop_loss = sum(s.get("stop_loss", current_price) for s in relevant_strategies.values()) / len(relevant_strategies)
        return round(avg_stop_loss, 2)