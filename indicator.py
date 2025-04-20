import pandas as pd
import ta
import requests
import os
from typing import Dict, Any
from datetime import datetime, timedelta

def get_stock_data(symbol: str) -> pd.DataFrame:
    """Alpha Vantage API를 사용하여 주식 데이터를 가져오는 함수"""
    try:
        # Alpha Vantage API 키
        api_key = os.getenv('ALPHA_VANTAGE', 'demo')  # 환경 변수 이름 수정
        
        # API 엔드포인트
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=full'
        
        # API 호출
        response = requests.get(url)
        data = response.json()
        
        if 'Time Series (Daily)' not in data:
            print(f"Error: {data.get('Error Message', 'Unknown error')}")
            return pd.DataFrame()
            
        # 데이터 변환
        time_series = data['Time Series (Daily)']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        
        # 컬럼 이름 변경
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # 데이터 타입 변환
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])
            
        # 날짜 인덱스 설정
        df.index = pd.to_datetime(df.index)
        
        # 최근 1년 데이터만 선택
        one_year_ago = datetime.now() - timedelta(days=365)
        df = df[df.index >= one_year_ago]
        
        return df.sort_index()
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()

def analyze_technical(symbol: str) -> Dict[str, Any]:
    try:
        df = get_stock_data(symbol)
        
        if df.empty:
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
        return {"error": f"Error analyzing {symbol}: {str(e)}"}

if __name__ == "__main__":
    result = analyze_technical("AAPL")
    print(result)