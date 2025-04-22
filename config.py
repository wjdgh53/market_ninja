import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE', 'demo')

# 모델 설정
SENTIMENT_MODEL = os.getenv('SENTIMENT_MODEL', 'gpt-4o-mini')

# 기술 지표 설정
INDICATORS_TIMEFRAME = os.getenv('INDICATORS_TIMEFRAME', '1y')  # 1년

# 로깅 설정
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')

# 환경 설정
ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = ENV == 'development'

# Supabase 설정 (참조용, API에서는 DB 연결 안함)
SUPABASE_URL = os.getenv('SUPABASE_URL') 
SUPABASE_KEY = os.getenv('SUPABASE_KEY')