from openai import OpenAI
import logging
import datetime
from config import OPENAI_API_KEY, SENTIMENT_MODEL

# 로깅 설정
logger = logging.getLogger(__name__)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_sentiment(symbol=None, title=None, content=None, link=None, source=None, pub_date=None):
    """
    뉴스 기사에 대한 상세 감성 분석을 수행합니다.
    
    Args:
        symbol (str): 주식 심볼(티커)
        title (str): 기사 제목
        content (str): 기사 내용
        link (str): 기사 링크
        source (str): 기사 출처
        pub_date (str): 기사 발행일
        
    Returns:
        dict: 감성 분석 결과가 포함된 사전
    """
    # 내용 필드 검증
    if not content:
        raise ValueError("Content is required for sentiment analysis")
    
    try:
        # 내용 요약 및 감성 분석 프롬프트
        prompt = f"""
        다음 뉴스 기사를 읽고 주식 시장 관점에서 상세한 감성 분석을 제공해주세요.
        응답은 반드시 JSON 형식으로 다음 필드를 포함해야 합니다:
        
        1. sentiment_score: -1~1 사이의 숫자 (-1: 매우 부정적, 0: 중립, 1: 매우 긍정적)
        2. sentiment_category: 다음 카테고리 중 하나 ["매우 부정적", "부정적", "중립", "긍정적", "매우 긍정적"]
        3. key_points: 기사에서 주식/기업 가치에 영향을 미칠 수 있는 주요 포인트들의 배열 (최대 3개)
        4. market_impact: 이 뉴스가 주가에 미칠 수 있는 영향에 대한 짧은 설명
        5. confidence: 분석의 신뢰도 (0~100 사이의 정수)
        
        주식 심볼: {symbol or '(지정되지 않음)'}
        제목: {title or '제목 없음'}
        
        내용:
        {content}
        
        JSON 형식으로만 응답해주세요.
        """
        
        # OpenAI API 호출
        response = client.chat.completions.create(
            model=SENTIMENT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        # 응답에서 JSON 추출
        analysis_result = response.choices[0].message.content.strip()
        
        # JSON 파싱
        import json
        try:
            parsed_result = json.loads(analysis_result)
            
            # 필수 필드 검증
            required_fields = ["sentiment_score", "sentiment_category", "key_points", "market_impact", "confidence"]
            for field in required_fields:
                if field not in parsed_result:
                    logger.warning(f"필수 필드 {field}가 API 응답에 없습니다. 기본값을 추가합니다.")
                    if field == "sentiment_score":
                        parsed_result[field] = 0.0
                    elif field == "sentiment_category":
                        parsed_result[field] = "중립"
                    elif field == "key_points":
                        parsed_result[field] = []
                    elif field == "market_impact":
                        parsed_result[field] = "영향을 판단할 수 없습니다."
                    elif field == "confidence":
                        parsed_result[field] = 50
            
            # 값 타입/범위 검증
            parsed_result["sentiment_score"] = max(-1.0, min(1.0, float(parsed_result["sentiment_score"])))
            parsed_result["confidence"] = max(0, min(100, int(parsed_result["confidence"])))
            
            # 카테고리 검증
            valid_categories = ["매우 부정적", "부정적", "중립", "긍정적", "매우 긍정적"]
            if parsed_result["sentiment_category"] not in valid_categories:
                # 점수 기반으로 카테고리 할당
                score = parsed_result["sentiment_score"]
                if score < -0.6:
                    parsed_result["sentiment_category"] = "매우 부정적"
                elif score < -0.2:
                    parsed_result["sentiment_category"] = "부정적"
                elif score < 0.2:
                    parsed_result["sentiment_category"] = "중립"
                elif score < 0.6:
                    parsed_result["sentiment_category"] = "긍정적"
                else:
                    parsed_result["sentiment_category"] = "매우 긍정적"
            
        except json.JSONDecodeError:
            logger.error(f"JSON 응답 파싱 실패: {analysis_result}")
            # 기본 응답 생성
            parsed_result = {
                "sentiment_score": 0.0,
                "sentiment_category": "중립",
                "key_points": ["분석 중 오류가 발생했습니다."],
                "market_impact": "영향을 판단할 수 없습니다.",
                "confidence": 0
            }
        
        # 응답 결합
        result = {
            "symbol": symbol,
            "title": title,
            "content_summary": content[:200] + "..." if content and len(content) > 200 else content,
            "link": link,
            "source": source,
            "pub_date": pub_date,
            "sentiment": parsed_result["sentiment_score"],  # -1~1 범위의 점수
            "sentiment_category": parsed_result["sentiment_category"],
            "key_points": parsed_result["key_points"],
            "market_impact": parsed_result["market_impact"],
            "confidence": parsed_result["confidence"],
            "analyzed_at": datetime.datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"감성 분석 중 오류 발생: {str(e)}")
        # 에러가 발생해도 기본 응답 반환
        return {
            "symbol": symbol,
            "title": title,
            "content_summary": content[:200] + "..." if content and len(content) > 200 else content,
            "link": link,
            "source": source,
            "pub_date": pub_date,
            "sentiment": 0.0,
            "sentiment_category": "중립",
            "key_points": ["분석 중 오류가 발생했습니다: " + str(e)],
            "market_impact": "영향을 판단할 수 없습니다.",
            "confidence": 0,
            "analyzed_at": datetime.datetime.now().isoformat(),
            "error": str(e)
        }