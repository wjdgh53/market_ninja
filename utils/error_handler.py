from flask import jsonify
import traceback
import logging
from config import LOG_LEVEL, LOG_FILE

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Flask 애플리케이션에 에러 핸들러 등록"""
    
    @app.errorhandler(400)
    def bad_request(e):
        logger.warning(f"400 Bad Request: {str(e)}")
        return jsonify({"error": str(e), "status": "error", "code": 400}), 400
    
    @app.errorhandler(404)
    def not_found(e):
        logger.warning(f"404 Not Found: {str(e)}")
        return jsonify({"error": "Resource not found", "status": "error", "code": 404}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"500 Server Error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "status": "error", "code": 500}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled Exception: {str(e)}")
        traceback.print_exc()
        
        # 사용자에게 보여줄 에러 메시지 (자세한 오류 내용은 로그에만 남김)
        return jsonify({
            "error": "An unexpected error occurred",
            "status": "error",
            "code": 500,
            "message": str(e) if app.debug else "서버에서 오류가 발생했습니다."
        }), 500