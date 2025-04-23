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
        rsi = indicators.get("RSI", 50)
        if rsi < 30:
            result["signals"].append("RSI_OVERSOLD")
            result["analysis"]["RSI"] = "과매도 상태"
        elif rsi > 70:
            result["signals"].append("RSI_OVERBOUGHT")
            result["analysis"]["RSI"] = "과매수 상태"
        else:
            result["analysis"]["RSI"] = "중립 상태"
            
        # 2. MACD 분석
        macd = indicators.get("MACD", 0)
        macd_signal = indicators.get("MACD_Signal", 0)
        if macd > macd_signal:
            result["signals"].append("MACD_BULLISH")
            result["analysis"]["MACD"] = "상승 추세"
        else:
            result["signals"].append("MACD_BEARISH")
            result["analysis"]["MACD"] = "하락 추세"
            
        # 3. 볼린저 밴드 분석
        current_price = indicators.get("Current_Price", 0)
        bb_high = indicators.get("BB_High", 0)
        bb_low = indicators.get("BB_Low", 0)
        
        if current_price > bb_high:
            result["signals"].append("BB_OVERBOUGHT")
            result["analysis"]["Bollinger_Bands"] = "상단 밴드 돌파"
        elif current_price < bb_low:
            result["signals"].append("BB_OVERSOLD")
            result["analysis"]["Bollinger_Bands"] = "하단 밴드 돌파"
        else:
            result["analysis"]["Bollinger_Bands"] = "밴드 내 위치"
            
        # 4. 이동평균선 분석
        sma_20 = indicators.get("SMA_20", 0)
        sma_50 = indicators.get("SMA_50", 0)
        sma_200 = indicators.get("SMA_200", 0)
        
        if current_price > sma_20 and sma_20 > sma_50 and sma_50 > sma_200:
            result["signals"].append("MA_BULLISH")
            result["analysis"]["Moving_Averages"] = "강한 상승 추세"
        elif current_price < sma_20 and sma_20 < sma_50 and sma_50 < sma_200:
            result["signals"].append("MA_BEARISH")
            result["analysis"]["Moving_Averages"] = "강한 하락 추세"
        else:
            result["analysis"]["Moving_Averages"] = "혼합된 추세"
            
        # 5. 거래량 분석
        volume = indicators.get("Volume", 0)
        volume_ema20 = indicators.get("Volume_EMA20", 0)
        if volume > volume_ema20:
            result["signals"].append("VOLUME_INCREASE")
            result["analysis"]["Volume"] = "거래량 증가"
        else:
            result["analysis"]["Volume"] = "거래량 감소"
            
        # 6. 스토캐스틱 분석
        stoch_k = indicators.get("Stoch_K", 50)
        stoch_d = indicators.get("Stoch_D", 50)
        if stoch_k > 80 and stoch_d > 80:
            result["signals"].append("STOCH_OVERBOUGHT")
            result["analysis"]["Stochastic"] = "과매수 상태"
        elif stoch_k < 20 and stoch_d < 20:
            result["signals"].append("STOCH_OVERSOLD")
            result["analysis"]["Stochastic"] = "과매도 상태"
        else:
            result["analysis"]["Stochastic"] = "중립 상태"
            
        # 7. ADX 분석
        adx = indicators.get("ADX", 0)
        if adx > 25:
            result["signals"].append("STRONG_TREND")
            result["analysis"]["ADX"] = "강한 추세"
        else:
            result["analysis"]["ADX"] = "약한 추세"
            
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