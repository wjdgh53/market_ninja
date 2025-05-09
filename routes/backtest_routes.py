from flask import Blueprint, request, jsonify
import logging
from services.backtest_service import run_backtest, optimize_strategy

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
backtest_bp = Blueprint('backtest', __name__, url_prefix='/backtest')

@backtest_bp.route('', methods=['POST'])
def backtest():
    """전략 백테스팅을 실행합니다."""
    data = request.get_json()
    
    # 필수 필드 검증
    if not data.get("symbol"):
        return jsonify({"error": "Missing 'symbol' field"}), 400
    
    if not data.get("strategy"):
        return jsonify({"error": "Missing 'strategy' field"}), 400
        
    try:
        # 필드 추출
        symbol = data.get("symbol")
        strategy = data.get("strategy")
        period = data.get("period", "1y")
        params = data.get("params", {})
        
        # 백테스팅 서비스 호출
        result = run_backtest(
            symbol=symbol,
            strategy=strategy,
            period=period,
            params=params
        )
        
        # 에러 확인
        if "error" in result:
            return jsonify({"error": result["error"]}), 400
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in backtesting: {str(e)}")
        return jsonify({"error": str(e)}), 500

@backtest_bp.route('/optimize', methods=['POST'])
def optimize():
    """전략 파라미터 최적화를 실행합니다."""
    data = request.get_json()
    
    # 필수 필드 검증
    if not data.get("symbol"):
        return jsonify({"error": "Missing 'symbol' field"}), 400
    
    if not data.get("strategy"):
        return jsonify({"error": "Missing 'strategy' field"}), 400
        
    try:
        # 필드 추출
        symbol = data.get("symbol")
        strategy = data.get("strategy")
        period = data.get("period", "1y")
        param_grid = data.get("param_grid", None)
        
        # 최적화 서비스 호출
        result = optimize_strategy(
            symbol=symbol,
            strategy=strategy,
            period=period,
            param_grid=param_grid
        )
        
        # 에러 확인
        if "error" in result:
            return jsonify({"error": result["error"]}), 400
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in strategy optimization: {str(e)}")
        return jsonify({"error": str(e)}), 500