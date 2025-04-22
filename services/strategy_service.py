import logging
from typing import Dict, Any, List

# 로깅 설정
logger = logging.getLogger(__name__)

def calculate_trading_strategies(technical: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    기술적 지표를 기반으로 매매 전략을 계산합니다.
    
    Args:
        technical (Dict[str, Any]): 기술적 지표가 포함된 사전
        
    Returns:
        List[Dict[str, Any]]: 매매 전략 목록
    """
    try:
        # 필요한 기술적 지표 추출
        close = technical.get("Current_Price", 0)
        bb_low = technical.get("BB_Low", 0)
        bb_high = technical.get("BB_High", 0)
        rsi = technical.get("RSI", 50)
        macd = technical.get("MACD", 0)
        signal = technical.get("MACD_Signal", 0)
        atr = technical.get("ATR", 0)
        
        # 기본값 설정 (0으로 나눔 등 오류 방지)
        if not atr or atr < 0.01:
            atr = close * 0.02  # 현재 가격의 2%를 ATR 기본값으로 설정

        strategies = []

        # Strategy 1: 볼린저 밴드 하단 매수
        bollinger_score = 0.9 if close < bb_low else 0.2
        strategies.append({
            "name": "bollinger_lower",
            "description": "볼린저 밴드 하단 지지 매수 전략",
            "score": bollinger_score,
            "buy": round(bb_low, 2),
            "take_profit": round(bb_low + 2 * atr, 2),
            "stop_loss": round(bb_low - 1.5 * atr, 2),
            "condition": "close < bb_low" if close < bb_low else "close >= bb_low",
            "remarks": "현재 매수 신호 발생 중" if close < bb_low else "매수 조건 불충족"
        })

        # Strategy 2: RSI 과매도
        rsi_score = 0.8 if rsi < 30 else 0.3
        strategies.append({
            "name": "rsi_oversold",
            "description": "RSI 과매도 반등 매수 전략",
            "score": rsi_score,
            "buy": round(close * 0.98, 2),
            "take_profit": round(close * 1.03, 2),
            "stop_loss": round(close * 0.95, 2),
            "condition": "RSI < 30" if rsi < 30 else "RSI >= 30",
            "remarks": "과매도 상태, 매수 신호 발생" if rsi < 30 else "RSI 정상 범위"
        })

        # Strategy 3: MACD 골든크로스
        macd_cross = macd > signal
        macd_score = 0.85 if macd_cross else 0.2
        strategies.append({
            "name": "macd_cross",
            "description": "MACD 골든크로스 모멘텀 매수 전략",
            "score": macd_score,
            "buy": round(close, 2),
            "take_profit": round(close * 1.04, 2),
            "stop_loss": round(close * 0.97, 2),
            "condition": "MACD > Signal" if macd_cross else "MACD <= Signal",
            "remarks": "골든크로스 발생, 매수 신호" if macd_cross else "골든크로스 미발생"
        })

        # Strategy 4: ATR 돌파 매매
        strategies.append({
            "name": "atr_breakout",
            "description": "ATR 돌파 추세 추종 전략",
            "score": 0.7,
            "buy": round(close + atr, 2),
            "take_profit": round(close + 2 * atr, 2),
            "stop_loss": round(close, 2),
            "condition": "설정된 매수가 돌파 시 매수",
            "remarks": f"현재가 {close}에서 {round(close + atr, 2)}(+{round(atr, 2)}) 돌파 시 매수"
        })

        # Strategy 5: 스토캐스틱 과매도
        stoch_k = technical.get("Stoch_K", 50)
        stoch_d = technical.get("Stoch_D", 50)
        stoch_condition = stoch_k < 20 and stoch_k > stoch_d
        stoch_score = 0.8 if stoch_condition else 0.3
            
        strategies.append({
            "name": "stochastic",
            "description": "스토캐스틱 과매도 반등 매수 전략",
            "score": stoch_score,
            "buy": round(close * 0.99, 2),
            "take_profit": round(close * 1.03, 2),
            "stop_loss": round(close * 0.96, 2),
            "condition": "Stoch_K < 20 and Stoch_K > Stoch_D" if stoch_condition else "조건 미충족",
            "remarks": "과매도 반등 신호 발생" if stoch_condition else "과매도 상태 아님"
        })

        # 점수 내림차순 정렬
        strategies.sort(key=lambda x: x["score"], reverse=True)

        return strategies
        
    except KeyError as e:
        logger.error(f"Missing key in technical indicators: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error calculating strategies: {str(e)}")
        return []