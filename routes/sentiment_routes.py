from flask import Blueprint, request, jsonify
import logging
from services.sentiment_service import analyze_sentiment

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
sentiment_bp = Blueprint('sentiment', __name__, url_prefix='/analyze')

@sentiment_bp.route('', methods=['POST'])
def analyze():
    """뉴스 콘텐츠에 대한 감성 분석을 수행합니다."""
    data = request.get_json()
    
    # 필수 필드 검증
    if not data.get("content"):
        return jsonify({"error": "Missing 'content' field"}), 400
    
    try:
        # 필드 추출
        symbol = data.get("symbol")
        content = data.get("content")
        title = data.get("title")
        link = data.get("link")
        source = data.get("source")
        pub_date = data.get("pub_date")
        
        # 감성 분석 서비스 호출
        result = analyze_sentiment(
            symbol=symbol,
            title=title,
            content=content,
            link=link,
            source=source,
            pub_date=pub_date
        )
        
        # n8n에서 DB 저장하므로 API에서는 결과만 반환
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500