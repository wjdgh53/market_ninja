# 마켓 닌자 프로젝트 다음 단계 구현 계획

프로젝트의 코드 구조 개선을 완료했으니, 이제 다음 단계로 실질적인 기능 구현을 진행합니다. 각 단계별 우선순위와 구현 계획은 다음과 같습니다.

## 1. 백테스팅 시스템 (1순위)

백테스팅은 전략의 유효성을 검증하는 중요한 단계입니다. 다음과 같이 구현합니다:

### 1.1 API 엔드포인트 추가

```
# routes/backtest_routes.py
@backtest_bp.route('', methods=['POST'])
def run_backtest():
    """전략 백테스팅을 실행합니다."""
    data = request.get_json()
    
    # 필수 필드 검증
    if not data.get("symbol") or not data.get("strategy"):
        return jsonify({"error": "Missing required fields"}), 400
        
    # 백테스팅 서비스 호출
    result = backtest_strategy(
        symbol=data.get("symbol"),
        strategy=data.get("strategy"),
        period=data.get("period", "1y"),
        initial_capital=data.get("initial_capital", 10000)
    )
    
    return jsonify(result)
```

### 1.2 백테스팅 서비스 구현

```python
# services/backtest_service.py
def backtest_strategy(symbol, strategy, period="1y", initial_capital=10000):
    """
    지정된 전략을 과거 데이터로 백테스팅합니다.
    """
    # 1. 과거 데이터 가져오기
    historical_data = get_historical_data(symbol, period)
    
    # 2. 전략 로직 적용
    trades = apply_strategy(historical_data, strategy)
    
    # 3. 성과 계산
    performance = calculate_performance(trades, initial_capital)
    
    return {
        "symbol": symbol,
        "strategy": strategy,
        "performance": performance,
        "trades": trades
    }
```

## 2. AI 전략 추천 시스템 (2순위)

백테스팅 결과를 기반으로 AI가 전략을 추천하는 기능을 구현합니다.

### 2.1 API 엔드포인트 추가

```python
# routes/recommend_routes.py
@recommend_bp.route('', methods=['POST'])
def recommend_strategy():
    """현재 시장 상황에 맞는 최적의 전략을 추천합니다."""
    data = request.get_json()
    
    if not data.get("symbol"):
        return jsonify({"error": "Missing 'symbol' field"}), 400
        
    # 추천 서비스 호출
    result = recommend_best_strategy(
        symbol=data.get("symbol"),
        risk_level=data.get("risk_level", "medium")
    )
    
    return jsonify(result)
```

### 2.2 추천 서비스 구현

```python
# services/recommend_service.py
def recommend_best_strategy(symbol, risk_level="medium"):
    """
    현재 시장 상황에 맞는 최적의 전략을 추천합니다.
    """
    # 1. 최근 기술 지표 가져오기
    indicators = analyze_technical_indicators(symbol)
    
    # 2. 최근 감성 점수 가져오기
    sentiment = get_recent_sentiment(symbol)
    
    # 3. 모든 전략의 백테스트 결과 가져오기
    backtest_results = get_strategy_backtest_results(symbol)
    
    # 4. 상황 분석 및 전략 선정
    recommended_strategy = select_best_strategy(
        indicators, 
        sentiment, 
        backtest_results, 
        risk_level
    )
    
    return {
        "symbol": symbol,
        "recommended_strategy": recommended_strategy,
        "market_analysis": {
            "technical": indicators,
            "sentiment": sentiment
        }
    }
```

## 3. 종목 선정 AI (3순위)

특정 전략에 적합한 종목을 자동으로 추천하는 시스템을 구현합니다.

### 3.1 API 엔드포인트 추가

```python
# routes/screener_routes.py
@screener_bp.route('', methods=['POST'])
def screen_stocks():
    """특정 전략에 적합한 종목을 스크리닝합니다."""
    data = request.get_json()
    
    strategy = data.get("strategy")
    market = data.get("market", "US")
    limit = data.get("limit", 10)
    
    # 스크리너 서비스 호출
    result = screen_for_strategy(strategy, market, limit)
    
    return jsonify(result)
```

### 3.2 스크리너 서비스 구현

```python
# services/screener_service.py
def screen_for_strategy(strategy, market="US", limit=10):
    """
    특정 전략에 적합한 종목을 스크리닝합니다.
    """
    # 1. 종목 리스트 가져오기
    stocks = get_market_stocks(market)
    
    # 2. 각 종목별 적합도 점수 계산
    scored_stocks = []
    for stock in stocks:
        score = calculate_strategy_fit(stock["symbol"], strategy)
        scored_stocks.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "score": score,
            "sector": stock["sector"]
        })
    
    # 3. 점수 기준 정렬 및 상위 종목 반환
    top_stocks = sorted(scored_stocks, key=lambda x: x["score"], reverse=True)[:limit]
    
    return {
        "strategy": strategy,
        "market": market,
        "recommendations": top_stocks
    }
```

## 구현 타임라인

| 단계 | 기능 | 예상 소요 시간 | 우선순위 |
|-----|-----|-------------|--------|
| 1 | 백테스팅 시스템 | 2주 | 높음 |
| 2 | AI 전략 추천 | 3주 | 중간 |
| 3 | 종목 선정 AI | 2주 | 중간 |
| 4 | 대시보드 UI | 3주 | 낮음 |

## 병렬 작업 가능 항목

- n8n 워크플로우 개선은 Flask API 개발과 병렬로 진행 가능
- 데이터 수집 및 저장 최적화는 백테스팅 시스템 개발과 병행 가능

이 계획을 바탕으로 순차적으로 구현해 나가면 약 2-3개월 내에 완전한 자동 매매 시스템을 구축할 수 있을 것입니다.
