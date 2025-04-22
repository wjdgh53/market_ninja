import pandas as pd
import ta
import requests
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from config import ALPHA_VANTAGE_API_KEY, INDICATORS_TIMEFRAME, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

# 로깅 설정
logger = logging.getLogger(__name__)

# Supabase 클라이언트 초기화
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 데이터베이스 접근 함수
def get_indicators_from_db(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Supabase DB에서 최신 기술 지표 데이터를 가져옵니다.
    
    Args:
        symbol (str): 주식 심볼(티커)
        
    Returns:
        Optional[Dict[str, Any]]: 기술 지표가 포함된 사전 또는 None
    """
    try:
        # DB에서 최신 데이터 조회
        response = supabase.table('technical_indicators') \
            .select('*') \
            .eq('symbol', symbol) \
            .order('created_at', desc=True) \
            .limit(1) \
            .execute()
            
        if not response.data:
            logger.info(f"DB에 {symbol} 데이터가 없습니다.")
            return None
            
        # 데이터가 24시간 이내인지 확인
        latest_data = response.data[0]
        data_timestamp = datetime.fromisoformat(latest_data['created_at'].replace('Z', '+00:00'))
        current_time = datetime.now(data_timestamp.tzinfo)  # 같은 시간대로 맞춤
        
        if current_time - data_timestamp > timedelta(hours=24):
            logger.info(f"{symbol} 데이터가 24시간이 지났습니다. 새로 계산이 필요합니다.")
            return None
            
        logger.info(f"DB에서 {symbol} 데이터를 성공적으로 가져왔습니다.")
        return latest_data
        
    except Exception as e:
        logger.error(f"DB에서 기술 지표 가져오기 실패 ({symbol}): {str(e)}")
        return None

def get_historical_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """
    Alpha Vantage API를 사용하여 주식의 역사적 데이터를 가져옵니다.
    
    Args:
        symbol (str): 주식 심볼(티커)
        period (str): 데이터 가져올 기간 (1d, 1w, 1m, 1y 등)
        
    Returns:
        pd.DataFrame: 주가 데이터가 포함된 DataFrame
    """
    try:
        # API 엔드포인트
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}&outputsize=full'
        
        # API 호출
        logger.info(f"Alpha Vantage API 호출: {symbol}")
        response = requests.get(url)
        data = response.json()
        
        # 데이터 검증
        if 'Time Series (Daily)' not in data:
            error_msg = data.get('Error Message', data.get('Information', 'Unknown error'))
            logger.error(f"Alpha Vantage API 오류: {error_msg}")
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
        
        # 기간에 따른 데이터 필터링
        if period == "1y" or period == "1년":
            cutoff_date = datetime.now() - timedelta(days=365)
        elif period == "6m" or period == "6개월":
            cutoff_date = datetime.now() - timedelta(days=182)
        elif period == "3m" or period == "3개월":
            cutoff_date = datetime.now() - timedelta(days=91)
        elif period == "1m" or period == "1개월":
            cutoff_date = datetime.now() - timedelta(days=30)
        elif period == "1w" or period == "1주":
            cutoff_date = datetime.now() - timedelta(days=7)
        else:
            # 기본값: 1년
            cutoff_date = datetime.now() - timedelta(days=365)
        
        df = df[df.index >= cutoff_date]
        
        # 인덱스 기준 정렬
        return df.sort_index()
        
    except Exception as e:
        logger.error(f"주가 데이터 가져오기 실패 ({symbol}): {str(e)}")
        return pd.DataFrame()

def calculate_technical_indicators(df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
    """
    주가 데이터프레임으로부터 기술적 지표를 계산합니다.
    
    Args:
        df (pd.DataFrame): 주가 데이터가 포함된 DataFrame
        symbol (str): 주식 심볼(티커)
        
    Returns:
        Dict[str, Any]: 기술적 지표가 포함된 사전
    """
    try:
        # 데이터 검증
        if df.empty:
            return {"error": f"No price data found for {symbol}"}
        
        if 'Close' not in df.columns:
            return {"error": "Invalid data format received"}

        # 현재 가격 설정
        df['Current_Price'] = df['Close'].iloc[-1]

        # 기술적 지표 계산
        # 이동평균
        df['SMA_20'] = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
        df['EMA_20'] = ta.trend.EMAIndicator(df['Close'], window=20).ema_indicator()
        df['SMA_50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
        df['SMA_200'] = ta.trend.SMAIndicator(df['Close'], window=200).sma_indicator()
        
        # 모멘텀 지표
        df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
        df['ROC'] = ta.momentum.ROCIndicator(df['Close']).roc()
        df['WILLR'] = ta.momentum.WilliamsRIndicator(
            high=df['High'], low=df['Low'], close=df['Close']
        ).williams_r()
        
        # 추세 지표
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Histogram'] = macd.macd_diff()
        
        df['ADX'] = ta.trend.ADXIndicator(
            high=df['High'], low=df['Low'], close=df['Close']
        ).adx()
        
        # 변동성 지표
        bb = ta.volatility.BollingerBands(df['Close'])
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Low'] = bb.bollinger_lband()
        df['BB_Width'] = (df['BB_High'] - df['BB_Low']) / df['Close']
        
        df['ATR'] = ta.volatility.AverageTrueRange(
            high=df['High'], low=df['Low'], close=df['Close']
        ).average_true_range()
        
        # 거래량 지표
        df['Volume_EMA20'] = ta.trend.EMAIndicator(df['Volume'], window=20).ema_indicator()
        df['Volume_Change'] = df['Volume'] / df['Volume'].shift(1) - 1
        
        # 오실레이터
        stoch = ta.momentum.StochasticOscillator(
            high=df['High'], low=df['Low'], close=df['Close']
        )
        df['Stoch_K'] = stoch.stoch()
        df['Stoch_D'] = stoch.stoch_signal()
        
        df['CCI'] = ta.trend.CCIIndicator(
            high=df['High'], low=df['Low'], close=df['Close']
        ).cci()

        # 최신 데이터 추출 (NaN 값 없는 행)
        latest = df.dropna().iloc[-1]
        result = latest.to_dict()
        
        # 추가 정보
        result['symbol'] = symbol
        result['last_updated'] = datetime.now().isoformat()
        result['data_period'] = INDICATORS_TIMEFRAME
        
        # 가독성을 위한 반올림
        for key, value in result.items():
            if isinstance(value, float):
                result[key] = round(value, 4)
        
        # Key 이름 정리: 공백 → 언더스코어
        result = {k.replace(' ', '_'): v for k, v in result.items()}
        
        return result
        
    except Exception as e:
        logger.error(f"기술적 지표 계산 실패 ({symbol}): {str(e)}")
        return {"error": f"Error calculating indicators for {symbol}: {str(e)}"}

def analyze_technical_indicators(symbol: str) -> Dict[str, Any]:
    """
    주식의 기술적 지표를 분석합니다.
    먼저 DB에서 데이터를 확인하고, 없거나 오래된 경우 새로 계산합니다.
    
    Args:
        symbol (str): 주식 심볼(티커)
        
    Returns:
        Dict[str, Any]: 기술적 지표가 포함된 사전
    """
    try:
        # 1. DB에서 데이터 확인
        db_data = get_indicators_from_db(symbol)
        if db_data:
            logger.info(f"DB에서 {symbol} 데이터를 사용합니다.")
            return db_data
            
        # 2. DB에 데이터가 없거나 오래된 경우 새로 계산
        logger.info(f"{symbol} 데이터를 새로 계산합니다.")
        df = get_historical_data(symbol)
        if df.empty:
            return {"error": f"No price data found for {symbol}"}
            
        # 3. 기술적 지표 계산
        result = calculate_technical_indicators(df, symbol)
        
        # 4. DB에 저장 (n8n에서 처리)
        # TODO: n8n 웹훅 호출 또는 메시지 큐 사용
        
        return result
        
    except Exception as e:
        logger.error(f"기술 지표 분석 중 오류 발생 ({symbol}): {str(e)}")
        return {"error": str(e)}

def get_or_calculate_indicators(symbol: str) -> Dict[str, Any]:
    """
    주식에 대한 기술적 지표를 가져오거나 계산합니다.
    DB에서 최신 데이터를 먼저 확인하고, 없는 경우에만 계산합니다.
    백테스팅 등 내부 사용을 위한 함수입니다.
    
    Args:
        symbol (str): 주식 심볼(티커)
        
    Returns:
        Dict[str, Any]: 기술적 지표가 포함된 사전
    """
    return analyze_technical_indicators(symbol)