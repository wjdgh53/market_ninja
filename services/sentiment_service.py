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
    뉴스 기사에 대한 감성 분석을 수행합니다.
    
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
        다음 뉴스 기사에 대해 감성 점수를 0~1 사이의 숫자로 매겨주세요.
        0은 매우 부정적, 1은 매우 긍정적입니다. 숫자만 정확히 반환해주세요.
        
        제목: {title or '제목 없음'}
        
        내용:
        {content}
        """
        
        # OpenAI API 호출
        response = client.chat.completions.create(
            model=SENTIMENT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        # 응답에서 점수 추출
        score_text = response.choices[0].message.content.strip()
        
        # 숫자로 변환 (오류 처리 포함)
        try:
            score = float(score_text)
            # 0-1 범위 확인
            score = max(0.0, min(1.0, score))
        except ValueError:
            logger.warning(f"Failed to parse sentiment score: {score_text}. Using default 0.5")
            score = 0.5
        
        # 결과 구성
        result = {
            "symbol": symbol,
            "title": title,
            "content": content[:200] + "..." if content and len(content) > 200 else content,  # 내용 요약
            "link": link,
            "source": source,
            "pub_date": pub_date,
            "sentiment": score,
            "analyzed_at": datetime.datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error during sentiment analysis: {str(e)}")
        raise