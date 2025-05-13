import logging
from typing import Dict, Any
import datetime
import pandas as pd
import yfinance as yf
from services.indicator_service import analyze_technical_indicators, get_historical_data

# 로깅 설정
logger = logging.getLogger(__name__)

def get_vix_data(period: str = "1m") -> pd.DataFrame:
    """
    VIX(공포지수) 데이터를 yfinance로 가져옵니다.
    Args:
        period (str): 데이터 가져올 기간 (예: '1m', '3mo', '1y')
    Returns:
        pd.DataFrame: VIX 데이터가 포함된 DataFrame
    """
    try:
        # yfinance에서 ^VIX 데이터 조회
        period_map = {
            "1m": "1mo",
            "3m": "3mo",
            "6m": "6mo",
            "1y": "1y"
        }
        yf_period = period_map.get(period, "1mo")
        df = yf.download("VIX", period=yf_period, interval="1d", progress=False)
        if df.empty:
            logger.warning(f"yfinance로 ^VIX 데이터 조회 실패: {period}")
        return df
    except Exception as e:
        logger.error(f"yfinance로 VIX 데이터 가져오기 실패: {str(e)}")
        return pd.DataFrame()

def get_fear_level_description(fear_level: str) -> str:
    """
    공포 레벨에 대한 설명을 반환합니다.
    """
    descriptions = {
        "EXTREME_FEAR": "시장이 극도의 공포 상태입니다. 역발상 매수 기회일 수 있으나, 추가 하락 가능성도 있습니다.",
        "FEAR": "시장이 공포 상태입니다. 일부 종목은 저평가되어 있을 수 있습니다.",
        "NEUTRAL": "시장이 중립적인 상태입니다.",
        "GREED": "시장이 탐욕 상태입니다. 일부 종목은 과매수 상태일 수 있습니다.",
        "EXTREME_GREED": "시장이 극도의 탐욕 상태입니다. 고점 도달 가능성이 있으니 주의하세요."
    }
    
    return descriptions.get(fear_level, "")

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
            result["analysis"]["trend_strength"] = "강한 추세 (ADX > 40)"
        else:
            result["sub_conditions"].append("MODERATE_TREND")
            result["analysis"]["trend_strength"] = "보통 추세 (ADX 25-40)"
        result["supporting_indicators"]["adx"] = adx
    else:
        result["sub_conditions"].append("WEAK_TREND")
        result["analysis"]["trend_strength"] = "약한 추세 (ADX < 25)"
        result["supporting_indicators"]["adx"] = adx

    # 2. 추세 방향 분석 (이동평균선 사용)
    current_price = indicators.get("current_price", 0)
    sma_20 = indicators.get("sma_20", 0)
    sma_50 = indicators.get("sma_50", 0)
    sma_200 = indicators.get("sma_200", 0)
    
    # 골든 크로스/데드 크로스 상태 확인
    if sma_20 > sma_50 > sma_200:
        result["sub_conditions"].append("BULL_TREND")
        result["analysis"]["trend_direction"] = "상승 추세 (SMA20 > SMA50 > SMA200)"
        result["supporting_indicators"]["sma_20"] = sma_20
        result["supporting_indicators"]["sma_50"] = sma_50
        result["supporting_indicators"]["sma_200"] = sma_200
    elif sma_20 < sma_50 < sma_200:
        result["sub_conditions"].append("BEAR_TREND")
        result["analysis"]["trend_direction"] = "하락 추세 (SMA20 < SMA50 < SMA200)"
        result["supporting_indicators"]["sma_20"] = sma_20
        result["supporting_indicators"]["sma_50"] = sma_50
        result["supporting_indicators"]["sma_200"] = sma_200
    
    # 현재가 대비 이동평균선 위치
    if current_price > sma_20 > sma_50:
        result["sub_conditions"].append("PRICE_ABOVE_MA")
        result["analysis"]["price_position"] = "가격이 이동평균선 위에 위치 (강세)"
        result["supporting_indicators"]["current_price"] = current_price
    elif current_price < sma_20 < sma_50:
        result["sub_conditions"].append("PRICE_BELOW_MA")
        result["analysis"]["price_position"] = "가격이 이동평균선 아래에 위치 (약세)"
        result["supporting_indicators"]["current_price"] = current_price
    
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
        result["analysis"]["volatility"] = f"높은 변동성 (BB Width: {bb_width:.4f})"
        result["supporting_indicators"]["bb_width"] = bb_width
    elif bb_width < 0.03:  # 낮은 변동성
        result["sub_conditions"].append("LOW_VOLATILITY")
        result["analysis"]["volatility"] = f"낮은 변동성 (BB Width: {bb_width:.4f})"
        result["supporting_indicators"]["bb_width"] = bb_width
    else:
        result["analysis"]["volatility"] = f"보통 변동성 (BB Width: {bb_width:.4f})"
    
    # 변동성 압축/확장 확인
    if bb_width < 0.02:
        result["sub_conditions"].append("VOLATILITY_CONTRACTION")
        result["analysis"]["volatility_state"] = "변동성 압축 (돌파 가능성 있음)"
    
    # 4. RSI 과매수/과매도 분석
    rsi = indicators.get("rsi", 50)
    if rsi > 70:
        result["sub_conditions"].append("RSI_OVERBOUGHT")
        result["analysis"]["rsi_condition"] = f"과매수 상태 (RSI: {rsi:.2f})"
        result["supporting_indicators"]["rsi"] = rsi
    elif rsi < 30:
        result["sub_conditions"].append("RSI_OVERSOLD")
        result["analysis"]["rsi_condition"] = f"과매도 상태 (RSI: {rsi:.2f})"
        result["supporting_indicators"]["rsi"] = rsi
    else:
        result["analysis"]["rsi_condition"] = f"중립 상태 (RSI: {rsi:.2f})"
    
    # 5. MACD 신호 분석
    macd = indicators.get("macd", 0)
    macd_signal = indicators.get("macd_signal", 0)
    if macd > macd_signal:
        result["sub_conditions"].append("MACD_BULLISH")
        result["analysis"]["macd_signal"] = "MACD 상승 신호"
        result["supporting_indicators"]["macd"] = macd
        result["supporting_indicators"]["macd_signal"] = macd_signal
    elif macd < macd_signal:
        result["sub_conditions"].append("MACD_BEARISH")
        result["analysis"]["macd_signal"] = "MACD 하락 신호"
        result["supporting_indicators"]["macd"] = macd
        result["supporting_indicators"]["macd_signal"] = macd_signal
    
    # 6. 볼린저 밴드 위치 분석
    bb_high = indicators.get("bb_high", 0)
    bb_low = indicators.get("bb_low", 0)
    if current_price > bb_high:
        result["sub_conditions"].append("PRICE_ABOVE_BB")
        result["analysis"]["bb_position"] = "가격이 볼린저 밴드 상단 돌파 (과매수 가능성)"
        result["supporting_indicators"]["bb_high"] = bb_high
    elif current_price < bb_low:
        result["sub_conditions"].append("PRICE_BELOW_BB")
        result["analysis"]["bb_position"] = "가격이 볼린저 밴드 하단 돌파 (과매도 가능성)"
        result["supporting_indicators"]["bb_low"] = bb_low
    
    # 7. 거래량 분석
    volume = indicators.get("volume", 0)
    volume_ema20 = indicators.get("volume_ema20", 0)
    if volume > volume_ema20 * 1.5:
        result["sub_conditions"].append("HIGH_VOLUME")
        result["analysis"]["volume_condition"] = "높은 거래량 (추세 확인 신호)"
        result["supporting_indicators"]["volume"] = volume
        result["supporting_indicators"]["volume_ema20"] = volume_ema20
    
    # 8. 시장 상황 결정 (트랜드 방향과 강도, 가격 위치 등을 종합)
    bullish_signals = sum(1 for cond in result["sub_conditions"] if any(x in cond for x in ["BULL", "ABOVE", "BULLISH", "OVERSOLD"]))
    bearish_signals = sum(1 for cond in result["sub_conditions"] if any(x in cond for x in ["BEAR", "BELOW", "BEARISH", "OVERBOUGHT"]))
    
    # 최종 시장 상황 판단
    if bullish_signals > bearish_signals + 1:
        result["market_condition"] = "BULLISH"
    elif bearish_signals > bullish_signals + 1:
        result["market_condition"] = "BEARISH"
    else:
        result["market_condition"] = "NEUTRAL"
    
    # 신뢰도 계산 (조건 수와 지표 일치도 기반)
    total_signals = len(result["sub_conditions"])
    if total_signals > 0:
        # 불리언/베어리쉬 신호의 차이가 클수록 신뢰도가 높음
        signal_diff = abs(bullish_signals - bearish_signals)
        signal_ratio = signal_diff / total_signals
        
        # 신뢰도 계산 (신호 차이와 총 신호 수 고려)
        result["condition_confidence"] = min(100, int(signal_ratio * 50) + min(50, total_signals * 5))
    
    # 9. 시장 분석 요약
    result["analysis"]["summary"] = f"{result['market_condition']} 시장 상황. "
    
    if result["market_condition"] == "BULLISH":
        result["analysis"]["summary"] += "기술적 지표들이 상승 추세를 지지하고 있습니다."
    elif result["market_condition"] == "BEARISH":
        result["analysis"]["summary"] += "기술적 지표들이 하락 추세를 지지하고 있습니다."
    else:
        result["analysis"]["summary"] += "혼합된 신호들로 시장 방향성이 불확실합니다."
    
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