from flask import Blueprint, request, jsonify
import logging
from services.market_service import get_market_condition_for_symbol, analyze_market_condition
from services.indicator_service import analyze_technical_indicators

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
market_bp = Blueprint('market', __name__, url_prefix='/market')

@market_bp.route('/condition', methods=['POST'])
def get_market_condition():
    """종목의 현재 시장 상황을 분석합니다."""
    data = request.get_json()
    
    # 필수 필드 검증
    if not data.get("symbol"):
        return jsonify({"error": "Missing 'symbol' field"}), 400
    
    try:
        # 종목 심볼 추출
        symbol = data.get("symbol")
        
        # 지표 데이터가 이미 있는 경우
        if data.get("indicators"):
            indicators = data.get("indicators")
            # 시장 상황 분석
            condition_result = analyze_market_condition(indicators)
        else:
            # 지표 데이터가 없으면 새로운 함수 호출
            condition_result = get_market_condition_for_symbol(symbol)
            if "error" in condition_result:
                return jsonify({"error": condition_result["error"]}), 400
        
        # 결과 반환
        return jsonify(condition_result)
        
    except Exception as e:
        logger.error(f"시장 상황 분석 중 오류 발생 ({data.get('symbol', 'unknown')}): {str(e)}")
        return jsonify({"error": str(e)}), 500