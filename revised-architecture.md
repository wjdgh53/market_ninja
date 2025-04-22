# 마켓 닌자 개선된 아키텍처

## 기본 구조

```
market_ninja/
├── app.py                 # 메인 Flask 애플리케이션
├── config.py              # 설정 파일
├── routes/                # API 라우트
│   ├── __init__.py
│   ├── sentiment_routes.py
│   ├── indicator_routes.py
│   └── strategy_routes.py
├── services/              # 비즈니스 로직
│   ├── __init__.py
│   ├── sentiment_service.py
│   ├── indicator_service.py
│   └── strategy_service.py
├── models/                # 데이터 모델
│   └── __init__.py
├── utils/                 # 유틸리티 함수
│   ├── __init__.py
│   └── error_handler.py
├── deploy.sh              # 배포 스크립트
├── webhook_server.py      # 웹훅 서버
├── requirements.txt       # 의존성 목록
└── README.md              # 프로젝트 문서
```

## 책임 분리

### n8n 담당 기능
- 데이터 수집 (RSS, API)
- 데이터 전처리 및 변환
- **데이터베이스 저장 (Supabase)**
- 워크플로우 관리 및 스케줄링

### Flask API 담당 기능
- 데이터 분석 (감성, 기술 지표)
- 전략 계산 및 추천
- 백테스팅 및 시뮬레이션 (추후 구현)
- AI 모델 통합 (추후 구현)

## API 엔드포인트

1. `/analyze` - 뉴스 감성 분석
2. `/indicator` - 기술 지표 분석
3. `/strategies` - 매매 전략 계산
4. `/backtest` - 백테스팅 (추후 구현)
5. `/recommend` - 전략 추천 (추후 구현)

## 데이터 흐름

1. n8n이 데이터 수집 및 전처리
2. Flask API에 분석 요청
3. API에서 분석 결과 반환
4. n8n이 결과를 Supabase에 저장

이 방식은 각 시스템의 강점을 활용하여 효율적인 데이터 처리 파이프라인을 구축합니다.
