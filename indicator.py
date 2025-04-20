import yfinance as yf
import pandas as pd
import ta
import time
from typing import Dict, Any
import requests

def get_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """주식 데이터를 가져오는 함수"""
    try:
        # 1. yfinance를 통한 시도
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        
        if not df.empty and 'Close' in df.columns:
            return df
            
        # 2. 직접 Yahoo Finance API 호출 시도
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range={period}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                result = data['chart']['result'][0]
                timestamps = result['timestamp']
                indicators = result['indicators']['quote'][0]
                
                df = pd.DataFrame({
                    'Open': indicators['open'],
                    'High': indicators['high'],
                    'Low': indicators['low'],
                    'Close': indicators['close'],
                    'Volume': indicators['volume']
                }, index=pd.to_datetime(timestamps, unit='s'))
                return df
                
        return pd.DataFrame()  # 빈 DataFrame 반환
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()

def analyze_technical(symbol: str, max_retries: int = 3) -> Dict[str, Any]:
    for attempt in range(max_retries):
        try:
            df = get_stock_data(symbol)
            
            if df.empty:
                if attempt < max_retries - 1:
                    time.sleep(2)  # 2초 대기 후 재시도
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
                time.sleep(2)  # 2초 대기 후 재시도
                continue
            return {"error": f"Error fetching data for {symbol}: {str(e)}"}

if __name__ == "__main__":
    result = analyze_technical("AAPL")
    print(result)