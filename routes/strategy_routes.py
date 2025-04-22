from flask import Blueprint, request, jsonify
import logging
import datetime
from services.indicator_service import analyze_technical_indicators
from services.strategy_service import calculate_trading_strategies

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
strategy_bp = Blueprint('strategy', __name__, url_prefix='/strategies')

@strategy_bp.route('', methods=['POST'])
def get_strategies():
    """종목에 대한 매매 전략을 계산합니다."""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get("symbol"):
            return jsonify({"error": "Missing 'symbol' field"}), 400
            
        symbol = data.get("symbol")
        
        # 1. 기술 지표 분석
        indicators = analyze_technical_indicators(symbol)
        
        # 에러 확인
        if "error" in indicators:
            return jsonify({"error": indicators["error"]}), 500
            
        # 2. 전략 계산
        strategy_results = calculate_trading_strategies(indicators)
        
        # 3. 결과 포맷팅 (n8n에서 사용하기 쉬운 형태로)
        response = {
            "symbol": symbol,
            "timestamp": datetime.datetime.now().isoformat(),
            "strategies": strategy_results,
            "current_price": indicators.get("Current_Price", 0)
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in strategy calculation: {str(e)}")
        return jsonify({"error": str(e)}), 500