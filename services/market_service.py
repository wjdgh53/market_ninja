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
    # 디버깅을 위한 로그 추가
    logger.info(f"indicators 키 목록: {list(indicators.keys())}")
    logger.info(f"볼린저 밴드 폭 (bb_width): {indicators.get('bb_width')}")
    logger.info(f"볼린저 밴드 폭 (BB_Width): {indicators.get('BB_Width')}")
    
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
    # 대소문자 검사 및 기본값 설정
    bb_width = indicators.get("bb_width", None) or indicators.get("BB_Width", None)
    logger.info(f"원래 bb_width 값: {bb_width}")
    
    # 0 또는 None인 경우 기본값 설정
    if bb_width is None or bb_width <= 0:
        bb_width = 0.03
        logger.info(f"bb_width가 0 또는 None이어서 기본값 0.03으로 설정")
    
    logger.info(f"최종 사용된 bb_width 값: {bb_width}")
    
    if bb_width > 0.1:  # 높은 변동성
        result["sub_conditions"].append("HIGH_VOLATILITY")
        result["supporting_indicators"]["bb_width"] = bb_width
    elif bb_width < 0.03:  # 낮은 변동성
        result["sub_conditions"].append("LOW_VOLATILITY")
        result["supporting_indicators"]["bb_width"] = bb_width
    
    # 변동성 압축/확장 확인
    if bb_width < 0.02:
        result["sub_conditions"].append("VOLATILITY_CONTRACTION")
    
    # 나머지 코드는 그대로 유지...
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
        if not isinstance(indicators, dict):
            logger.error(f"analyze_technical_indicators가 dict가 아닌 값을 반환: {indicators}")
            return {"error": "기술적 지표 계산 결과가 올바르지 않습니다."}
        if "error" in indicators:
            return {"error": indicators["error"]}
        # 2. 지표를 기반으로 시장 상황 분석
        result = analyze_market_condition(indicators)
        if not isinstance(result, dict):
            logger.error(f"analyze_market_condition이 dict가 아닌 값을 반환: {result}")
            return {"error": "시장 상황 분석 결과가 올바르지 않습니다."}
        return result
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