import logging
from typing import Dict, Any
import datetime
from services.indicator_service import analyze_technical_indicators

# 로깅 설정
logger = logging.getLogger(__name__)

def analyze_market_condition(indicators: Dict[str, Any]) -> Dict[str, Any]:
    """
    기술적 지표를 기반으로 현재 시장 상황을 분석합니다.
    
    Args:
        indicators (Dict[str, Any]): 기술적 지표 데이터
        
    Returns:
        Dict[str, Any]: 시장 상황 분석 결과
    """
    # 기본 결과 구조
    result = {
        "symbol": indicators.get("symbol", "Unknown"),
        "timestamp": datetime.datetime.now().isoformat(),
        "market_condition": "NEUTRAL",  # 기본값
        "condition_confidence": 0,      # 신뢰도 (0-100)
        "sub_conditions": [],           # 세부 상태 목록
        "supporting_indicators": {},    # 판단 근거 지표
        "analysis": {}                  # 상세 분석
    }

    # 1. 추세 강도 분석 (ADX 사용)
    adx = indicators.get("adx", 0)
    if adx > 25:
        if adx > 40:
            result["sub_conditions"].append("STRONG_TREND")
        else:
            result["sub_conditions"].append("MODERATE_TREND")
        result["supporting_indicators"]["adx"] = adx
    else:
        result["sub_conditions"].append("WEAK_TREND")

    # 2. 추세 방향 분석 (이동평균선 사용)
    current_price = indicators.get("current_price", 0)
    sma_20 = indicators.get("sma_20", 0)
    sma_50 = indicators.get("sma_50", 0)
    sma_200 = indicators.get("sma_200", 0)
    
    # 골든 크로스/데드 크로스 상태 확인
    if sma_20 > sma_50 > sma_200:
        result["sub_conditions"].append("BULL_TREND")
    elif sma_20 < sma_50 < sma_200:
        result["sub_conditions"].append("BEAR_TREND")
    
    # 현재가 대비 이동평균선 위치
    if current_price > sma_20 > sma_50:
        result["sub_conditions"].append("PRICE_ABOVE_MA")
    elif current_price < sma_20 < sma_50:
        result["sub_conditions"].append("PRICE_BELOW_MA")
    
    # 3. 변동성 분석 (ATR, 볼린저 밴드 폭 사용)
    atr = indicators.get("atr", 0)
    bb_width = indicators.get("bb_width", 0)
    
    if bb_width > 0.1:  # 높은 변동성
        result["sub_conditions"].append("HIGH_VOLATILITY")
        result["supporting_indicators"]["bb_width"] = bb_width
    elif bb_width < 0.03:  # 낮은 변동성
        result["sub_conditions"].append("LOW_VOLATILITY")
        result["supporting_indicators"]["bb_width"] = bb_width
    
    # 변동성 압축/확장 확인
    if bb_width < 0.02:
        result["sub_conditions"].append("VOLATILITY_CONTRACTION")
    
    # 4. 모멘텀 분석 (RSI, MACD 사용)
    rsi = indicators.get("rsi", 50)
    macd = indicators.get("macd", 0)
    macd_signal = indicators.get("macd_signal", 0)
    
    if rsi > 70:
        result["sub_conditions"].append("OVERBOUGHT")
        result["supporting_indicators"]["rsi"] = rsi
    elif rsi < 30:
        result["sub_conditions"].append("OVERSOLD")
        result["supporting_indicators"]["rsi"] = rsi
    
    if macd > macd_signal and macd > 0:
        result["sub_conditions"].append("POSITIVE_MOMENTUM")
    elif macd < macd_signal and macd < 0:
        result["sub_conditions"].append("NEGATIVE_MOMENTUM")
    
    # 5. 최종 시장 상태 결정
    # 세부 상태를 바탕으로 주요 시장 상태 결정
    bull_signals = len([s for s in result["sub_conditions"] if any(
        x in s for x in ["BULL", "ABOVE", "POSITIVE", "OVERSOLD"]
    )])
    bear_signals = len([s for s in result["sub_conditions"] if any(
        x in s for x in ["BEAR", "BELOW", "NEGATIVE", "OVERBOUGHT"]
    )])
    
    # 추세 강도
    trend_strength = "WEAK" if "WEAK_TREND" in result["sub_conditions"] else \
                     "STRONG" if "STRONG_TREND" in result["sub_conditions"] else "MODERATE"
    
    # 변동성 상태
    volatility = "HIGH" if "HIGH_VOLATILITY" in result["sub_conditions"] else \
                 "LOW" if "LOW_VOLATILITY" in result["sub_conditions"] else "NORMAL"
    
    # 최종 시장 상태 결정
    if "BULL_TREND" in result["sub_conditions"] and trend_strength != "WEAK":
        if volatility == "HIGH":
            result["market_condition"] = "STRONG_UPTREND"
        else:
            result["market_condition"] = "UPTREND"
        result["condition_confidence"] = min(100, 50 + (bull_signals - bear_signals) * 10)
    
    elif "BEAR_TREND" in result["sub_conditions"] and trend_strength != "WEAK":
        if volatility == "HIGH":
            result["market_condition"] = "STRONG_DOWNTREND"
        else:
            result["market_condition"] = "DOWNTREND"
        result["condition_confidence"] = min(100, 50 + (bear_signals - bull_signals) * 10)
    
    elif trend_strength == "WEAK" and volatility != "HIGH":
        result["market_condition"] = "SIDEWAYS"
        result["condition_confidence"] = min(100, 50 + (5 - abs(bull_signals - bear_signals)) * 10)
    
    elif "VOLATILITY_CONTRACTION" in result["sub_conditions"]:
        result["market_condition"] = "VOLATILITY_COMPRESSION"
        result["condition_confidence"] = 70
    
    elif volatility == "HIGH" and trend_strength == "WEAK":
        result["market_condition"] = "CHOPPY"  # 높은 변동성의 횡보장
        result["condition_confidence"] = 60
    
    # 상세 분석 메시지 작성
    result["analysis"] = {
        "trend": {
            "strength": trend_strength,
            "direction": "BULLISH" if bull_signals > bear_signals else 
                         "BEARISH" if bear_signals > bull_signals else "NEUTRAL",
            "description": f"추세 강도는 {trend_strength}이며 방향은 {'상승' if bull_signals > bear_signals else '하락' if bear_signals > bull_signals else '중립'}입니다."
        },
        "volatility": {
            "level": volatility,
            "description": f"변동성은 {volatility} 수준입니다."
        }
    }
    
    return result

def get_market_condition_for_symbol(symbol: str) -> Dict[str, Any]:
    """
    심볼에 대한 시장 상황을 분석합니다.
    
    Args:
        symbol (str): 주식 심볼
        
    Returns:
        Dict[str, Any]: 시장 상황 분석 결과
    """
    try:
        # 1. 먼저 기술적 지표를 계산
        indicators = analyze_technical_indicators(symbol)
        
        if "error" in indicators:
            return {"error": indicators["error"]}
            
        # 2. 지표를 기반으로 시장 상황 분석
        return analyze_market_condition(indicators)
        
    except Exception as e:
        logger.error(f"시장 상황 분석 중 오류: {str(e)}")
        return {"error": str(e)}

def save_market_condition(market_condition: Dict[str, Any], db_connection) -> bool:
    """
    시장 상황 분석 결과를 데이터베이스에 저장합니다.
    
    Args:
        market_condition (Dict[str, Any]): 시장 상황 분석 결과
        db_connection: 데이터베이스 연결 객체
        
    Returns:
        bool: 저장 성공 여부
    """
    try:
        # 여기에 데이터베이스 저장 로직 구현
        # 예시: Supabase나 PostgreSQL 직접 연결 코드
        
        # 성공 반환
        return True
        
    except Exception as e:
        logger.error(f"시장 상황 저장 중 오류: {str(e)}")
        return False