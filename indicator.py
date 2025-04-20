import yfinance as yf
import pandas as pd
import ta
import time
from typing import Dict, Any

def analyze_technical(symbol: str, max_retries: int = 3) -> Dict[str, Any]:
    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period="1y")
            
            if df.empty:
                if attempt < max_retries - 1:
                    time.sleep(1)  # 1초 대기 후 재시도
                    continue
                return {"error": f"No price data found for {symbol}"}
            
            if 'Close' not in df.columns:
                return {"error": "Invalid data format received"}

            df['Current_Price'] = df['Close']

            # 기술적 지표 계산
            df['SMA_20'] = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
            df['EMA_20'] = ta.trend.EMAIndicator(df['Close'], window=20).ema_indicator()
            df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
            macd = ta.trend.MACD(df['Close'])
            df['MACD'] = macd.macd()
            df['MACD_Signal'] = macd.macd_signal()
            bb = ta.volatility.BollingerBands(df['Close'])
            df['BB_High'] = bb.bollinger_hband()
            df['BB_Low'] = bb.bollinger_lband()
            df['ATR'] = ta.volatility.AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close']).average_true_range()  
            df['CCI'] = ta.trend.CCIIndicator(high=df['High'], low=df['Low'], close=df['Close']).cci()
            df['ADX'] = ta.trend.ADXIndicator(high=df['High'], low=df['Low'], close=df['Close']).adx()
            df['Stoch_K'] = ta.momentum.StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close']).stoch()
            df['Stoch_D'] = ta.momentum.StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close']).stoch_signal()
            df['ROC'] = ta.momentum.ROCIndicator(df['Close']).roc()
            df['WILLR'] = ta.momentum.WilliamsRIndicator(high=df['High'], low=df['Low'], close=df['Close']).williams_r()

            latest = df.dropna().iloc[-1]
            result = latest.to_dict()
            result['symbol'] = symbol

            # Key 이름 정리: 공백 → 언더스코어
            result = {k.replace(' ', '_'): v for k, v in result.items()}
            
            return result
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # 1초 대기 후 재시도
                continue
            return {"error": f"Error fetching data for {symbol}: {str(e)}"}

if __name__ == "__main__":
    result = analyze_technical("AAPL")
    print(result)