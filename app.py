from flask import Flask
import os
from routes.sentiment_routes import sentiment_bp
from routes.indicator_routes import indicator_bp
from routes.strategy_routes import strategy_bp
from utils.error_handler import register_error_handlers

# Flask 애플리케이션 생성
app = Flask(__name__)

# CORS 설정 - 모든 도메인에서의 요청 허용
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# 라우트 등록
app.register_blueprint(sentiment_bp)
app.register_blueprint(indicator_bp)
app.register_blueprint(strategy_bp)

# 에러 핸들러 등록
register_error_handlers(app)

# 서버 상태 확인용 헬스체크 엔드포인트
@app.route('/health', methods=['GET'])
def health_check():
    return {"status": "ok", "message": "Server is running"}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port)