from flask import Blueprint, request, jsonify
import logging
from services.sentiment_service import analyze_sentiment

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
sentiment_bp = Blueprint('sentiment', __name__, url_prefix='/analyze')

@sentiment_bp.route('', methods=['POST'])
def analyze():
    """뉴스 콘텐츠에 대한 상세 감성 분석을 수행합니다."""
    data = request.get_json()
    
    # 필수 필드 검증
    if not data.get("content"):
        return jsonify({"error": "필수 필드 'content'가 없습니다"}), 400
    
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
        
        # 결과에 에러가 있는지 확인
        if "error" in result:
            logger.warning(f"감성 분석 완료 (오류 발생): {result['error']}")
            # 에러가 있어도 분석 결과는 반환 (n8n에서 처리하도록)
        else:
            logger.info(f"감성 분석 성공: {title[:30] if title else '제목 없음'}...")
        
        # n8n에서 DB 저장하므로 API에서는 결과만 반환
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"감성 분석 중 오류 발생: {str(e)}")
        return jsonify({
            "error": str(e),
            "symbol": data.get("symbol"),
            "title": data.get("title"),
            "content_summary": data.get("content", "")[:200] + "..." if data.get("content") and len(data.get("content")) > 200 else data.get("content"),
            "sentiment": 0.0,
            "sentiment_category": "중립",
            "key_points": ["분석 중 오류가 발생했습니다."],
            "market_impact": "영향을 판단할 수 없습니다.",
            "confidence": 0,
            "analyzed_at": data.get("pub_date")
        }), 500