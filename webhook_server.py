from flask import Flask, request, jsonify
import os
import logging
import hmac
import hashlib
import subprocess

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='webhook_log.txt',
    filemode='a'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# GitHub 웹훅 시크릿 (환경 변수에서 가져오거나 기본값 사용)
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')

def verify_signature(payload, signature):
    """GitHub 웹훅 서명을 검증합니다."""
    if not WEBHOOK_SECRET or not signature:
        return True  # 시크릿이 설정되지 않았으면 검증 스킵
        
    # 'sha256=' 접두사 제거
    if signature.startswith('sha256='):
        signature = signature[7:]
        
    # HMAC 서명 계산
    computed_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # 계산된 서명과 받은 서명 비교
    return hmac.compare_digest(computed_signature, signature)

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    GitHub 웹훅을 처리하여 배포 스크립트를 실행합니다.
    """
    logger.info("웹훅 요청 수신")
    
    # 시크릿 키가 설정된 경우 서명 검증
    if WEBHOOK_SECRET:
        signature = request.headers.get('X-Hub-Signature-256', '')
        if not verify_signature(request.data, signature):
            logger.warning("유효하지 않은 웹훅 서명")
            return jsonify({"error": "Invalid signature"}), 403
    
    # 배포 스크립트 실행
    try:
        result = subprocess.run(
            ["./deploy.sh"], 
            capture_output=True, 
            text=True,
            check=True
        )
        
        # 배포 결과 로깅
        logger.info(f"배포 스크립트 실행 결과: {result.returncode}")
        if result.stdout:
            logger.info(f"배포 출력: {result.stdout}")
        if result.stderr:
            logger.warning(f"배포 오류: {result.stderr}")
            
        return jsonify({
            "status": "success",
            "message": "배포 완료"
        }), 200
            
    except subprocess.CalledProcessError as e:
        logger.error(f"배포 스크립트 실행 실패: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "배포 실패",
            "error": str(e)
        }), 500
    except Exception as e:
        logger.error(f"예상치 못한 오류: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "웹훅 처리 실패",
            "error": str(e)
        }), 500

@app.route("/health", methods=["GET"])
def health():
    """웹훅 서버 상태 확인 엔드포인트"""
    return jsonify({"status": "ok"}), 200
    
if __name__ == "__main__":
    # 포트 설정 (환경변수 또는 기본값)
    port = int(os.environ.get('WEBHOOK_PORT', 9000))
    
    # 모든 인터페이스에서 리스닝
    logger.info(f"웹훅 서버 시작 (포트: {port})")
    app.run(host='0.0.0.0', port=port)