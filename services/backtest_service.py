import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, Any, List
from services.indicator_service import get_historical_data
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

# 로깅 설정
logger = logging.getLogger(__name__)

# SMA 교차 전략 클래스 정의
class SMACrossStrategy(Strategy):
    # 전략 파라미터
    short_window = 20
    long_window = 50
    
    def init(self):
        # 이동평균선 계산
        self.sma_short = self.I(SMA, self.data.Close, self.short_window)
        self.sma_long = self.I(SMA, self.data.Close, self.long_window)
        
    def next(self):
        # 매수 신호 (골든 크로스)
        if crossover(self.sma_short, self.sma_long):
            self.position.close()  # 기존 포지션 종료
            self.buy()
            
        # 매도 신호 (데드 크로스)
        elif crossover(self.sma_long, self.sma_short):
            self.position.close()  # 기존 포지션 종료
            self.sell()

def run_backtest(symbol: str, strategy: str, period: str = "1y", params: Dict = None) -> Dict[str, Any]:
    """
    지정된 전략으로 백테스트를 실행합니다.
    
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
        
        # backtesting.py 형식으로 데이터 변환
        df = df.rename(columns={
            'Open': 'Open',
            'High': 'High', 
            'Low': 'Low', 
            'Close': 'Close', 
            'Volume': 'Volume'
        })
        
        # 2. 전략 선택 및 백테스트 설정
        if strategy == 'sma_cross':
            bt_strategy = SMACrossStrategy
            # 동적으로 전략 파라미터 설정
            bt_strategy.short_window = strategy_params['short_window']
            bt_strategy.long_window = strategy_params['long_window']
        else:
            return {"error": f"지원하지 않는 전략입니다: {strategy}"}
        
        # 3. 백테스트 실행
        bt = Backtest(df, bt_strategy, cash=10000, commission=0.0025)
        result = bt.run()
        
        # 4. 결과 처리
        trades = []
        # result.trades가 있으면 공식 API 사용
        trades_list = getattr(result, 'trades', [])
        for t in trades_list:
            # Trade 객체가 아니면 건너뜀
            if not hasattr(t, "entry_time"):
                logger.warning(f"잘못된 trade 객체 감지: {t} (type: {type(t)})")
                continue
            trade_info = {
                'entry_date': str(t.entry_time.date()),
                'exit_date': str(t.exit_time.date()) if t.exit_time else 'open',
                'entry_price': round(t.entry_price, 2),
                'exit_price': round(t.exit_price, 2) if t.exit_price else round(df['Close'].iloc[-1], 2),
                'profit_pct': round(t.pl_pct, 2),
                'type': 'LONG' if t.size > 0 else 'SHORT'
            }
            trades.append(trade_info)
        # 미종료 거래 처리 (현재 포지션이 있는 경우)
        open_trades = [t for t in trades_list if hasattr(t, 'is_closed') and not t.is_closed]
        if open_trades:
            pos = open_trades[-1]
            current_price = df['Close'].iloc[-1]
            pl_pct = ((current_price / pos.entry_price) - 1) * 100 if pos.size > 0 else ((pos.entry_price / current_price) - 1) * 100
            trades.append({
                'entry_date': str(pos.entry_time.date()),
                'exit_date': 'open',
                'entry_price': round(pos.entry_price, 2),
                'exit_price': round(current_price, 2),
                'profit_pct': round(pl_pct, 2),
                'type': 'LONG' if pos.size > 0 else 'SHORT'
            })
        
        # 5. 통계 계산
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t['profit_pct'] > 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # 평균 수익/손실
        profits = [t['profit_pct'] for t in trades if t['profit_pct'] > 0]
        losses = [t['profit_pct'] for t in trades if t['profit_pct'] <= 0]
        avg_profit = np.mean(profits) if profits else 0
        avg_loss = np.mean(losses) if losses else 0
        
        # 자산 가치 곡선 계산
        equity_curve = result._equity_curve['Equity'].values / 10000.0  # 초기 자본으로 정규화
        dates = [str(d.date()) for d in result._equity_curve.index]
        
        # 수익/손실 비율
        profit_loss_ratio = abs(avg_profit / avg_loss) if avg_loss != 0 else 0
        
        return {
            "symbol": symbol,
            "strategy": strategy,
            "period": period,
            "parameters": strategy_params,
            "last_updated": datetime.now().isoformat(),
            "total_return": round(result['Return [%]'], 2),
            "mdd": round(result['Max. Drawdown [%]'], 2),
            "win_rate": round(win_rate, 2),
            "total_trades": total_trades,
            "avg_profit": round(avg_profit, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_loss_ratio": round(profit_loss_ratio, 2),
            "sharpe_ratio": round(result['Sharpe Ratio'], 2),
            "trades": trades,
            "equity_curve": equity_curve.tolist(),
            "dates": dates
        }
        
    except Exception as e:
        logger.error(f"백테스트 실행 중 오류: {str(e)}")
        return {"error": str(e)}

# 다른 전략 클래스들 (볼린저, MACD, RSI 등)을 추가할 수 있음
# 예를 들어:
class BollingerStrategy(Strategy):
    window = 20
    num_std = 2.0
    
    def init(self):
        # 이동평균과 표준편차 계산
        self.sma = self.I(SMA, self.data.Close, self.window)
        self.std = self.data.Close.rolling(self.window).std()
        self.upper = self.sma + self.num_std * self.std
        self.lower = self.sma - self.num_std * self.std
        
    def next(self):
        # 하한선 돌파 시 매수
        if self.data.Close[-1] < self.lower[-1]:
            self.position.close()
            self.buy()
            
        # 상한선 돌파 시 매도
        elif self.data.Close[-1] > self.upper[-1]:
            self.position.close()
            self.sell()

# optimize_strategy 함수도 backtesting.py에 맞게 수정 필요
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
            # 다른 전략 추가 가능
        }
        
        # 파라미터 그리드 병합
        grid = {**default_param_grid.get(strategy, {}), **(param_grid or {})}
        
        # 1. 과거 데이터 조회
        df = get_historical_data(symbol, period)
        if df.empty:
            return {"error": f"데이터를 찾을 수 없습니다: {symbol}"}
        
        # backtesting.py 형식으로 데이터 변환
        df = df.rename(columns={
            'Open': 'Open', 
            'High': 'High', 
            'Low': 'Low', 
            'Close': 'Close', 
            'Volume': 'Volume'
        })
        
        # 2. 최적화 실행
        if strategy == 'sma_cross':
            bt = Backtest(df, SMACrossStrategy, cash=10000, commission=0.0025)
            result = bt.optimize(
                short_window=grid['short_window'],
                long_window=grid['long_window'],
                maximize='Return [%]',
                constraint=lambda p: p.short_window < p.long_window
            )
        elif strategy == 'bollinger':
            bt = Backtest(df, BollingerStrategy, cash=10000, commission=0.0025)
            result = bt.optimize(
                window=grid['window'],
                num_std=grid['num_std'],
                maximize='Return [%]'
            )
        else:
            return {"error": f"지원하지 않는 전략입니다: {strategy}"}
        
        # 3. 최적화 결과 처리
        stats = result._stats
        
        # 상위 5개 파라미터 조합 추출
        top_results = []
        param_combinations = list(stats.index)
        
        for i, params in enumerate(param_combinations[:5]):  # 상위 5개만
            result_dict = {
                "parameters": dict(zip(grid.keys(), params)),
                "total_return": round(stats['Return [%]'].iloc[i], 2),
                "sharpe_ratio": round(stats['Sharpe Ratio'].iloc[i], 2),
                "win_rate": round(stats['Win Rate [%]'].iloc[i], 2),
                "mdd": round(stats['Max. Drawdown [%]'].iloc[i], 2)
            }
            top_results.append(result_dict)
        
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