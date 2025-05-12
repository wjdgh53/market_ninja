import pandas as pd
import ta
import requests
import logging
from typing import Dict, Any
from datetime import datetime
from config import ALPHA_VANTAGE_API_KEY, INDICATORS_TIMEFRAME
import os
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def get_historical_data(symbol: str, period: str = "1y", refresh: bool = False, cache_expire_days: int = 1) -> pd.DataFrame:
    """
    Alpha Vantage API를 사용하여 주식의 역사적 데이터를 가져옵니다.
    (파일 캐시: data_cache/{symbol}_{period}.csv, 1일 자동 만료 + refresh 옵션)
    Args:
        symbol (str): 주식 심볼(티커)
        period (str): 데이터 가져올 기간 (1d, 1w, 1m, 1y 등)
        refresh (bool): True면 무조건 새로 받아옴
        cache_expire_days (int): 캐시 만료 일수(기본 1일)
    Returns:
        pd.DataFrame: 주가 데이터가 포함된 DataFrame
    """
    try:
        cache_dir = "data_cache"
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"{symbol}_{period}.csv")

        use_cache = False
        if not refresh and os.path.exists(cache_file):
            mtime = os.path.getmtime(cache_file)
            age_days = (time.time() - mtime) / (60*60*24)
            if age_days < cache_expire_days:
                use_cache = True
                logger.info(f"[CACHE VALID] {cache_file} (age: {age_days:.2f}일) → 캐시 사용")
            else:
                logger.info(f"[CACHE EXPIRED] {cache_file} (age: {age_days:.2f}일) → API 새로 호출")
        elif refresh:
            logger.info(f"[REFRESH] refresh=True로 API 새로 호출")
        else:
            logger.info(f"[CACHE MISS] {cache_file} 없음, API 호출 진행")

        if use_cache:
            try:
                logger.info(f"[CACHE HIT] {cache_file}에서 데이터 읽기 시도")
                df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                logger.info(f"[CACHE READ] {cache_file} shape={df.shape}")
                if not df.empty:
                    logger.info(f"[CACHE RETURN] {symbol} {period} 데이터 반환 (행:{df.shape[0]})")
                    return df
                else:
                    logger.warning(f"[CACHE EMPTY] {cache_file} 파일이 비어 있음")
            except Exception as e:
                logger.warning(f"[CACHE ERROR] 캐시 파일 읽기 실패: {cache_file} ({e})")

        # API 엔드포인트
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}&outputsize=full'
        logger.info(f"[API REQUEST] Alpha Vantage API 호출 시작: {symbol}")
        response = requests.get(url)
        data = response.json()
        logger.info(f"[API RESPONSE] Alpha Vantage 응답 수신: {symbol}")
        if 'Time Series (Daily)' not in data:
            error_msg = data.get('Error Message', data.get('Information', 'Unknown error'))
            logger.error(f"[API ERROR] Alpha Vantage API 오류: {error_msg}")
            return pd.DataFrame()
        time_series = data['Time Series (Daily)']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])
        df.index = pd.to_datetime(df.index)
        # 기간에 따른 데이터 필터링
        if period == "1y" or period == "1년":
            cutoff_date = datetime.now() - pd.Timedelta(days=365)
        elif period == "6m" or period == "6개월":
            cutoff_date = datetime.now() - pd.Timedelta(days=182)
        elif period == "3m" or period == "3개월":
            cutoff_date = datetime.now() - pd.Timedelta(days=91)
        elif period == "1m" or period == "1개월":
            cutoff_date = datetime.now() - pd.Timedelta(days=30)
        elif period == "1w" or period == "1주":
            cutoff_date = datetime.now() - pd.Timedelta(days=7)
        else:
            cutoff_date = datetime.now() - pd.Timedelta(days=365)
        df = df[df.index >= cutoff_date]
        df = df.sort_index()
        logger.info(f"[API DATA] {symbol} {period} 데이터 shape={df.shape}")
        # 받아온 데이터가 있으면 파일로 저장
        if not df.empty:
            try:
                df.to_csv(cache_file)
                logger.info(f"[CACHE SAVE] API 데이터 캐시 저장 성공: {cache_file} (행:{df.shape[0]})")
            except Exception as e:
                logger.warning(f"[CACHE SAVE ERROR] 캐시 파일 저장 실패: {cache_file} ({e})")
        else:
            logger.warning(f"[API DATA EMPTY] {symbol} {period} 데이터가 비어 있음")
        return df
    except Exception as e:
        logger.error(f"[FATAL] 주가 데이터 가져오기 실패 ({symbol}): {str(e)}")
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
        
        # 볼린저 밴드 폭 로깅
        logger.info(f"볼린저 밴드 폭 계산: 마지막 3개 값 = {df['BB_Width'].tail(3).tolist()}")
        logger.info(f"볼린저 밴드 폭에 0 또는 NaN 값이 있는지: {(df['BB_Width'] <= 0).any() or df['BB_Width'].isna().any()}")
        
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
        
        # BB_Width 값 로깅
        logger.info(f"result 딕셔너리의 BB_Width 값: {result.get('BB_Width')}")
        
        # 추가 정보
        result['symbol'] = symbol
        result['last_updated'] = datetime.now().isoformat()
        result['data_period'] = INDICATORS_TIMEFRAME
        
        # 가독성을 위한 반올림
        for key, value in result.items():
            if isinstance(value, float):
                result[key] = round(value, 4)
        
        # 볼린저 밴드 폭 추가 검사
        if 'BB_Width' in result:
            if result['BB_Width'] <= 0 or pd.isna(result['BB_Width']):
                logger.warning(f"비정상적인 BB_Width 값 감지({result['BB_Width']}). 기본값 0.03으로 설정")
                result['BB_Width'] = 0.03
        else:
            logger.warning(f"BB_Width 키가 result에 없음. 기본값 0.03으로 추가")
            result['BB_Width'] = 0.03
            
        # Key 이름 정리: 공백 → 언더스코어
        result = {k.replace(' ', '_').lower(): v for k, v in result.items()}
        logger.info(f"bb_width가 result에 있는지: {'bb_width' in result}")
        logger.info(f"최종 bb_width 값: {result.get('bb_width')}")
        
        return result
        
    except Exception as e:
        logger.error(f"기술적 지표 계산 실패 ({symbol}): {str(e)}")
        return {"error": f"Error calculating indicators for {symbol}: {str(e)}"}

def analyze_technical_indicators(symbol: str) -> Dict[str, Any]:
    """
    주식의 기술적 지표를 분석합니다.
    
    Args:
        symbol (str): 주식 심볼(티커)
        
    Returns:
        Dict[str, Any]: 기술적 지표가 포함된 사전 임
    """
    try:
        # 1. 주가 데이터 가져오기
        logger.info(f"{symbol} 데이터를 새로 계산합니다.")
        df = get_historical_data(symbol)
        if df.empty:
            return {"error": f"No price data found for {symbol}"}
            
        # 2. 기술적 지표 계산
        result = calculate_technical_indicators(df, symbol)
        
        return result
        
    except Exception as e:
        logger.error(f"기술 지표 분석 중 오류 발생 ({symbol}): {str(e)}")
        return {"error": str(e)}