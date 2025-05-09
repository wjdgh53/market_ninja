import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, Any, List
from services.indicator_service import get_historical_data

# 로깅 설정
logger = logging.getLogger(__name__)

def calculate_sma_signals(df: pd.DataFrame, short_window: int = 20, long_window: int = 50) -> pd.DataFrame:
    """
    단순 이동평균 교차 전략의 매매 시그널을 계산합니다.
    
    Args:
        df (pd.DataFrame): OHLCV 데이터
        short_window (int): 단기 이동평균 기간
        long_window (int): 장기 이동평균 기간
    
    Returns:
        pd.DataFrame: 시그널이 추가된 데이터프레임
    """
    try:
        # 이동평균 계산
        df['SMA_Short'] = df['Close'].rolling(window=short_window).mean()
        df['SMA_Long'] = df['Close'].rolling(window=long_window).mean()
        
        # 골든 크로스/데드 크로스 시그널 생성
        df['Signal'] = 0
        df.loc[df['SMA_Short'] > df['SMA_Long'], 'Signal'] = 1  # 골든 크로스 (매수)
        df.loc[df['SMA_Short'] < df['SMA_Long'], 'Signal'] = -1  # 데드 크로스 (매도)
        
        # 시그널 변화 포인트 감지
        df['Position'] = df['Signal'].diff()
        
        return df
        
    except Exception as e:
        logger.error(f"SMA 시그널 계산 중 오류: {str(e)}")
        raise

def calculate_bollinger_signals(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    """
    볼린저 밴드 전략의 매매 시그널을 계산합니다.
    
    Args:
        df (pd.DataFrame): OHLCV 데이터
        window (int): 이동평균 기간
        num_std (float): 표준편차 승수
    
    Returns:
        pd.DataFrame: 시그널이 추가된 데이터프레임
    """
    try:
        # 볼린저 밴드 계산
        df['BB_Middle'] = df['Close'].rolling(window=window).mean()
        std = df['Close'].rolling(window=window).std()
        df['BB_Upper'] = df['BB_Middle'] + (std * num_std)
        df['BB_Lower'] = df['BB_Middle'] - (std * num_std)
        
        # 매매 시그널 생성
        df['Signal'] = 0
        df.loc[df['Close'] < df['BB_Lower'], 'Signal'] = 1  # 하단 돌파 (매수)
        df.loc[df['Close'] > df['BB_Upper'], 'Signal'] = -1  # 상단 돌파 (매도)
        
        # 시그널 변화 포인트 감지
        df['Position'] = df['Signal'].diff()
        
        return df
        
    except Exception as e:
        logger.error(f"볼린저 밴드 시그널 계산 중 오류: {str(e)}")
        raise

def calculate_macd_signals(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
    """
    MACD 전략의 매매 시그널을 계산합니다.
    
    Args:
        df (pd.DataFrame): OHLCV 데이터
        fast_period (int): 빠른 EMA 기간
        slow_period (int): 느린 EMA 기간
        signal_period (int): 시그널 라인 기간
    
    Returns:
        pd.DataFrame: 시그널이 추가된 데이터프레임
    """
    try:
        # MACD 계산
        df['EMA_Fast'] = df['Close'].ewm(span=fast_period, adjust=False).mean()
        df['EMA_Slow'] = df['Close'].ewm(span=slow_period, adjust=False).mean()
        df['MACD'] = df['EMA_Fast'] - df['EMA_Slow']
        df['MACD_Signal'] = df['MACD'].ewm(span=signal_period, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # 매매 시그널 생성
        df['Signal'] = 0
        df.loc[df['MACD'] > df['MACD_Signal'], 'Signal'] = 1  # MACD가 시그널선 상향 돌파 (매수)
        df.loc[df['MACD'] < df['MACD_Signal'], 'Signal'] = -1  # MACD가 시그널선 하향 돌파 (매도)
        
        # 시그널 변화 포인트 감지
        df['Position'] = df['Signal'].diff()
        
        return df
        
    except Exception as e:
        logger.error(f"MACD 시그널 계산 중 오류: {str(e)}")
        raise

def calculate_rsi_signals(df: pd.DataFrame, period: int = 14, overbought: int = 70, oversold: int = 30) -> pd.DataFrame:
    """
    RSI 전략의 매매 시그널을 계산합니다.
    
    Args:
        df (pd.DataFrame): OHLCV 데이터
        period (int): RSI 계산 기간
        overbought (int): 과매수 기준값
        oversold (int): 과매도 기준값
    
    Returns:
        pd.DataFrame: 시그널이 추가된 데이터프레임
    """
    try:
        # RSI 계산
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 매매 시그널 생성
        df['Signal'] = 0
        df.loc[df['RSI'] < oversold, 'Signal'] = 1  # 과매도 상태 (매수)
        df.loc[df['RSI'] > overbought, 'Signal'] = -1  # 과매수 상태 (매도)
        
        # 시그널 변화 포인트 감지
        df['Position'] = df['Signal'].diff()
        
        return df
        
    except Exception as e:
        logger.error(f"RSI 시그널 계산 중 오류: {str(e)}")
        raise

def calculate_strategy_returns(df: pd.DataFrame, initial_capital: float = 10000.0, commission: float = 0.0025) -> Dict[str, Any]:
    """
    매매 시그널을 기반으로 수익률과 기타 지표를 계산합니다.
    
    Args:
        df (pd.DataFrame): 시그널이 포함된 데이터프레임
        initial_capital (float): 초기 자본금
        commission (float): 거래 수수료 (기본값 0.25%)
    
    Returns:
        Dict[str, Any]: 백테스트 결과
    """
    try:
        # 포지션 진입/청산 포인트 식별
        df['Trade'] = 0
        df.loc[df['Position'] == 2, 'Trade'] = 1  # 매수 진입
        df.loc[df['Position'] == -2, 'Trade'] = -1  # 매도 진입
        
        # 수익률 계산
        df['Returns'] = df['Close'].pct_change()
        df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']
        
        # 수수료 적용
        df['Trade_Cost'] = 0.0
        df.loc[df['Position'] != 0, 'Trade_Cost'] = commission
        df['Net_Returns'] = df['Strategy_Returns'] - df['Trade_Cost']
        
        # 누적 수익률
        df['Cumulative_Returns'] = (1 + df['Net_Returns']).cumprod()
        
        # 트레이드 기록
        trades = []
        current_position = None
        entry_price = 0
        entry_date = None
        
        for idx, row in df.iterrows():
            if row['Position'] == 2 and current_position is None:  # 매수 진입
                current_position = 'LONG'
                entry_price = row['Close']
                entry_date = idx
            elif row['Position'] == -2 and current_position == 'LONG':  # 매수 청산
                profit = (row['Close'] - entry_price) / entry_price * 100
                trades.append({
                    'entry_date': entry_date.strftime('%Y-%m-%d'),
                    'exit_date': idx.strftime('%Y-%m-%d'),
                    'entry_price': round(entry_price, 2),
                    'exit_price': round(row['Close'], 2),
                    'profit_pct': round(profit, 2),
                    'type': 'LONG'
                })
                current_position = None
            elif row['Position'] == -2 and current_position is None:  # 매도 진입(Short)
                current_position = 'SHORT'
                entry_price = row['Close']
                entry_date = idx
            elif row['Position'] == 2 and current_position == 'SHORT':  # 매도 청산
                profit = (entry_price - row['Close']) / entry_price * 100
                trades.append({
                    'entry_date': entry_date.strftime('%Y-%m-%d'),
                    'exit_date': idx.strftime('%Y-%m-%d'),
                    'entry_price': round(entry_price, 2),
                    'exit_price': round(row['Close'], 2),
                    'profit_pct': round(profit, 2),
                    'type': 'SHORT'
                })
                current_position = None
        
        # 미청산 포지션 처리
        if current_position is not None:
            if current_position == 'LONG':
                profit = (df['Close'].iloc[-1] - entry_price) / entry_price * 100
            else:  # SHORT
                profit = (entry_price - df['Close'].iloc[-1]) / entry_price * 100
                
            trades.append({
                'entry_date': entry_date.strftime('%Y-%m-%d'),
                'exit_date': 'open',
                'entry_price': round(entry_price, 2),
                'exit_price': round(df['Close'].iloc[-1], 2),
                'profit_pct': round(profit, 2),
                'type': current_position
            })
        
        # 최종 수익률
        total_return = (df['Cumulative_Returns'].iloc[-1] - 1) * 100
        
        # MDD (Maximum Drawdown) 계산
        cumulative_max = df['Cumulative_Returns'].expanding().max()
        drawdown = (df['Cumulative_Returns'] - cumulative_max) / cumulative_max
        mdd = drawdown.min() * 100
        
        # 승률 계산
        winning_trades = len([t for t in trades if t.get('profit_pct', 0) > 0])
        total_trades = len(trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # 평균 수익/손실
        profits = [t['profit_pct'] for t in trades if t.get('profit_pct', 0) > 0]
        losses = [t['profit_pct'] for t in trades if t.get('profit_pct', 0) <= 0]
        avg_profit = np.mean(profits) if profits else 0
        avg_loss = np.mean(losses) if losses else 0
        
        # 샤프 비율 계산
        risk_free_rate = 0.02  # 연 2% 무위험 수익률 가정
        daily_risk_free = ((1 + risk_free_rate) ** (1/252)) - 1
        excess_returns = df['Net_Returns'] - daily_risk_free
        sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252) if excess_returns.std() != 0 else 0
        
        # 수익/손실 비율
        profit_loss_ratio = abs(avg_profit / avg_loss) if avg_loss != 0 else 0
        
        return {
            'total_return': round(total_return, 2),
            'mdd': round(abs(mdd), 2),
            'win_rate': round(win_rate, 2),
            'total_trades': total_trades,
            'avg_profit': round(avg_profit, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_loss_ratio': round(profit_loss_ratio, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'trades': trades,
            'equity_curve': df['Cumulative_Returns'].tolist(),
            'dates': [d.strftime('%Y-%m-%d') for d in df.index]
        }
        
    except Exception as e:
        logger.error(f"수익률 계산 중 오류: {str(e)}")
        raise

def run_backtest(symbol: str, strategy: str, period: str = "1y", params: Dict = None) -> Dict[str, Any]:
    """
    지정된 전략으로 백테스트를 실행합니다.체크
    
    Args:
        symbol (str): 종목 심볼
        strategy (str): 전략 이름 ('sma_cross', 'bollinger', 'macd', 'rsi')
        period (str): 백테스트 기간
        params (Dict): 전략별 파라미터
    
    Returns:
        Dict[str, Any]: 백테스트 결과
    """
    try:
        # 기본 파라미터 설정
        default_params = {
            'sma_cross': {'short_window': 20, 'long_window': 50},
            'bollinger': {'window': 20, 'num_std': 2.0},
            'macd': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
            'rsi': {'period': 14, 'overbought': 70, 'oversold': 30}
        }
        
        # 파라미터 병합
        strategy_params = {**(default_params.get(strategy, {})), **(params or {})}
        
        # 1. 과거 데이터 조회
        df = get_historical_data(symbol, period)
        if df.empty:
            return {"error": f"데이터를 찾을 수 없습니다: {symbol}"}
            
        # 2. 전략별 시그널 생성
        if strategy == 'sma_cross':
            df = calculate_sma_signals(
                df,
                short_window=strategy_params['short_window'],
                long_window=strategy_params['long_window']
            )
        elif strategy == 'bollinger':
            df = calculate_bollinger_signals(
                df,
                window=strategy_params['window'],
                num_std=strategy_params['num_std']
            )
        elif strategy == 'macd':
            df = calculate_macd_signals(
                df,
                fast_period=strategy_params['fast_period'],
                slow_period=strategy_params['slow_period'],
                signal_period=strategy_params['signal_period']
            )
        elif strategy == 'rsi':
            df = calculate_rsi_signals(
                df,
                period=strategy_params['period'],
                overbought=strategy_params['overbought'],
                oversold=strategy_params['oversold']
            )
        else:
            return {"error": f"지원하지 않는 전략입니다: {strategy}"}
            
        # 3. 수익률 계산
        results = calculate_strategy_returns(df)
        
        # 4. 결과 구성
        return {
            "symbol": symbol,
            "strategy": strategy,
            "period": period,
            "parameters": strategy_params,
            "last_updated": datetime.now().isoformat(),
            **results
        }
        
    except Exception as e:
        logger.error(f"백테스트 실행 중 오류: {str(e)}")
        return {"error": str(e)}

def optimize_strategy(symbol: str, strategy: str, period: str = "1y", param_grid: Dict[str, List] = None) -> Dict[str, Any]:
    """
    지정된 전략의 최적 파라미터를 찾기 위한 그리드 서치를 실행합니다.
    
    Args:
        symbol (str): 종목 심볼
        strategy (str): 전략 이름 ('sma_cross', 'bollinger', 'macd', 'rsi')
        period (str): 백테스트 기간
        param_grid (Dict[str, List]): 최적화할 파라미터 그리드
    
    Returns:
        Dict[str, Any]: 최적화 결과
    """
    try:
        # 기본 파라미터 그리드 설정
        default_param_grid = {
            'sma_cross': {
                'short_window': [5, 10, 15, 20, 25],
                'long_window': [30, 40, 50, 60, 70]
            },
            'bollinger': {
                'window': [10, 15, 20, 25, 30],
                'num_std': [1.5, 2.0, 2.5, 3.0]
            },
            'macd': {
                'fast_period': [8, 10, 12, 14, 16],
                'slow_period': [20, 24, 26, 28, 30],
                'signal_period': [7, 8, 9, 10, 11]
            },
            'rsi': {
                'period': [7, 10, 14, 20, 25],
                'overbought': [65, 70, 75, 80],
                'oversold': [20, 25, 30, 35]
            }
        }
        
        # 파라미터 그리드 병합
        grid = {**default_param_grid.get(strategy, {}), **(param_grid or {})}
        
        # 기본 파라미터 조합 생성 (그리드 서치)
        import itertools
        param_keys = list(grid.keys())
        param_values = list(grid.values())
        param_combinations = list(itertools.product(*param_values))
        
        # 결과 저장 리스트
        results = []
        
        # 각 파라미터 조합에 대해 백테스트 실행
        for params in param_combinations:
            param_dict = {param_keys[i]: params[i] for i in range(len(param_keys))}
            backtest_result = run_backtest(symbol, strategy, period, param_dict)
            
            # 에러 확인
            if "error" in backtest_result:
                continue
                
            # 결과 저장
            results.append({
                "parameters": param_dict,
                "total_return": backtest_result["total_return"],
                "sharpe_ratio": backtest_result.get("sharpe_ratio", 0),
                "win_rate": backtest_result["win_rate"],
                "mdd": backtest_result["mdd"]
            })
        
        # 수익률 기준 정렬
        results = sorted(results, key=lambda x: x["total_return"], reverse=True)
        
        # 상위 5개 결과 반환
        top_results = results[:5]
        
        return {
            "symbol": symbol,
            "strategy": strategy,
            "period": period,
            "top_results": top_results,
            "parameter_count": len(param_combinations),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"전략 최적화 중 오류: {str(e)}")
        return {"error": str(e)}

def calculate_strategy_weights(symbol: str, period: str = "1y", strategies: List[str] = None) -> Dict[str, Any]:
    """
    여러 전략의 백테스팅 결과를 기반으로 전략 가중치를 계산합니다.
    
    Args:
        symbol (str): 종목 심볼
        period (str): 백테스트 기간
        strategies (List[str]): 평가할 전략 목록
        
    Returns:
        Dict[str, Any]: 계산된 전략 가중치
    """
    try:
        # 기본 전략 목록
        if not strategies:
            strategies = ['sma_cross', 'bollinger', 'macd', 'rsi']
            
        # 결과 저장
        strategy_results = {}
        
        # 각 전략에 대해 백테스팅 실행
        for strategy in strategies:
            backtest_result = run_backtest(symbol, strategy, period)
            
            # 에러 확인
            if "error" in backtest_result:
                continue
                
            # 주요 지표 저장
            strategy_results[strategy] = {
                "total_return": backtest_result["total_return"],
                "sharpe_ratio": backtest_result.get("sharpe_ratio", 0),
                "win_rate": backtest_result["win_rate"],
                "mdd": backtest_result["mdd"],
                "parameters": backtest_result["parameters"]
            }
        
        # 가중치 계산 (복합 점수 기반)
        weights = {}
        total_score = 0
        
        for strategy, result in strategy_results.items():
            # 각 지표에 가중치 부여
            return_score = result["total_return"] * 1.0
            sharpe_score = result["sharpe_ratio"] * 20.0
            win_rate_score = result["win_rate"] * 0.5
            mdd_score = max(0, 100 - result["mdd"]) * 0.3
            
            # 종합 점수
            score = return_score + sharpe_score + win_rate_score + mdd_score
            strategy_results[strategy]["score"] = score
            total_score += score
        
        # 가중치 정규화
        if total_score > 0:
            for strategy, result in strategy_results.items():
                weights[strategy] = round(result["score"] / total_score, 4)
        else:
            # 모든 전략의 점수가 0 이하인 경우 균등 배분
            for strategy in strategy_results:
                weights[strategy] = round(1.0 / len(strategy_results), 4)
        
        return {
            "symbol": symbol,
            "period": period,
            "weights": weights,
            "strategy_results": strategy_results,
            "calculation_basis": "composite_score",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"전략 가중치 계산 중 오류: {str(e)}")
        return {"error": str(e)}