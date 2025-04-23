# Market Ninja API 문서

## 기본 정보
- 기본 URL: `http://localhost:5050`
- Content-Type: `application/json`

## 엔드포인트

### 1. 전략 분석 (`/strategies`)
- **Method**: POST
- **설명**: 주어진 기술적 지표를 기반으로 매매 전략을 분석합니다.
- **Request Body**:
  ```json
  {
    "symbol": "AAPL",
    "indicators": {
      "RSI": 45.67,
      "MACD": 0.5,
      "MACD_Signal": 0.3,
      "Current_Price": 150.0,
      "BB_High": 155.0,
      "BB_Low": 145.0,
      "SMA_20": 148.0,
      "SMA_50": 146.0,
      "SMA_200": 140.0,
      "Volume": 1000000,
      "Volume_EMA20": 900000,
      "Stoch_K": 35,
      "Stoch_D": 40,
      "ADX": 30
    }
  }
  ```
- **Response**:
  ```json
  {
    "symbol": "AAPL",
    "timestamp": "2025-04-22T18:25:21.829132",
    "analysis": {
      "signals": ["MACD_BULLISH", "MA_BULLISH", "VOLUME_INCREASE", "STRONG_TREND"],
      "analysis": {
        "ADX": "강한 추세",
        "Bollinger_Bands": "밴드 내 위치",
        "MACD": "상승 추세",
        "Moving_Averages": "강한 상승 추세",
        "RSI": "중립 상태",
        "Stochastic": "중립 상태",
        "Volume": "거래량 증가"
      },
      "recommendation": "BUY",
      "confidence": 50.0
    },
    "current_price": 150.0
  }
  ```

### 2. 기술적 지표 계산 (`/indicators`)
- **Method**: POST
- **설명**: 주식 심볼을 받아서 기술적 지표를 계산합니다.
- **Request Body**:
  ```json
  {
    "symbol": "AAPL"
  }
  ```
- **Response**: indicators 객체와 동일한 형식

### 3. 뉴스 감성 분석 (`/sentiment`)
- **Method**: POST
- **설명**: 주식 관련 뉴스의 감성을 분석합니다.
- **Request Body**:
  ```json
  {
    "symbol": "AAPL"
  }
  ```
- **Response**:
  ```json
  {
    "symbol": "AAPL",
    "timestamp": "2025-04-22T18:25:21.829132",
    "sentiment_score": 0.75,
    "sentiment": "POSITIVE",
    "news_count": 10,
    "confidence": 85.5
  }
  ```

## 참고사항
1. n8n에서 Alpha Vantage API로 데이터를 가져와서 `/strategies` 엔드포인트로 전달하면 됩니다.
2. 모든 시간은 ISO 8601 형식입니다.
3. 신뢰도 점수(confidence)는 0-100 사이의 값입니다.
4. 매매 추천(recommendation)은 "BUY", "SELL", "HOLD" 중 하나입니다. 