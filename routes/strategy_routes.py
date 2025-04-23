from flask import Blueprint, request, jsonify
import logging
import datetime
from services.strategy_service import analyze_strategy

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
strategy_bp = Blueprint('strategy', __name__, url_prefix='/strategies')

@strategy_bp.route('', methods=['POST'])
def get_strategies():
    """종목에 대한 매매 전략을 분석합니다."""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        if not data.get("symbol"):
            return jsonify({"error": "Missing 'symbol' field"}), 400
        if not data.get("indicators"):
            return jsonify({"error": "Missing 'indicators' field"}), 400
            
        symbol = data.get("symbol")
        indicators = data.get("indicators")
        
        # indicators에 symbol 추가
        indicators["symbol"] = symbol
        
        # 전략 분석
        strategy_results = analyze_strategy(indicators)
        
        # 결과 포맷팅
        response = {
            "symbol": symbol,
            "timestamp": datetime.datetime.now().isoformat(),
            "analysis": strategy_results,
            "current_price": indicators.get("Current_Price", 0)
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in strategy calculation: {str(e)}")
        return jsonify({"error": str(e)}), 500