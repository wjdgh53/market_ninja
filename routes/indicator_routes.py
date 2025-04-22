from flask import Blueprint, request, jsonify
import logging
from services.indicator_service import analyze_technical_indicators

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
indicator_bp = Blueprint('indicator', __name__, url_prefix='/indicator')

@indicator_bp.route('', methods=['POST'])
def analyze_indicators():
    """주가 기술 지표를 분석합니다."""
    data = request.get_json()
    
    # 필수 필드 검증
    if not data.get("symbol"):
        return jsonify({"error": "Missing 'symbol' field"}), 400
    
    try:
        # 심볼 추출
        symbol = data.get("symbol")
        
        # 기술 지표 분석 서비스 호출
        result = analyze_technical_indicators(symbol)
        
        # 에러 확인
        if "error" in result:
            return jsonify({"error": result["error"]}), 400
        
        # 타임스탬프 추가 (n8n에서 데이터 저장 시 유용)
        import datetime
        result['timestamp'] = datetime.datetime.now().isoformat()
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in technical indicator analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500