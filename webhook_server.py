from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    # 시그니처 검증 없이 바로 배포 스크립트 실행
    os.system("./deploy.sh")
    return "✅ Webhook received", 200

if __name__ == "__main__":
    app.run(port=9000)
