#!/bin/bash

echo "🔁 Deploying latest changes..."

cd ~/market_ninja

# 최신 코드 가져오기
git pull origin main

# 패키지 설치 (변동 있을 경우 대비)
~/market_ninja/venv/bin/pip install -r requirements.txt

# 기존 실행 중인 서버 종료
pkill -f "venv/bin/python flask_sentiment_api.py"

# 새로운 프로세스로 실행
nohup ~/market_ninja/venv/bin/python flask_sentiment_api.py > log.txt 2>&1 &

echo "🚀 Deployment complete."
