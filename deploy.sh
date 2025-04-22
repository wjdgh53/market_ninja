#!/bin/bash

echo "🔁 시작: 최신 변경사항 배포 중..."

cd ~/market_ninja

# 1. 최신 코드 가져오기
echo "📥 Git 저장소에서 최신 코드 가져오기"
git pull origin main

# 2. 패키지 설치 (변동 있을 경우 대비)
echo "📦 필요한 패키지 설치 중"
~/market_ninja/venv/bin/pip install -r requirements.txt

# 3. 기존 실행 중인 서버 확인 및 종료
echo "🔍 기존 프로세스 확인 중"
SERVER_PID=$(pgrep -f "venv/bin/python app.py")

if [ -n "$SERVER_PID" ]; then
    echo "🛑 기존 서버 종료 (PID: $SERVER_PID)"
    kill -9 $SERVER_PID
else
    echo "ℹ️ 실행 중인 서버가 없습니다"
fi

# 4. 로그 디렉토리 확인 및 생성
if [ ! -d "logs" ]; then
    echo "📁 로그 디렉토리 생성"
    mkdir -p logs
fi

# 5. 새로운 프로세스로 실행
echo "🚀 새 서버 시작 중"
nohup ~/market_ninja/venv/bin/python app.py > logs/app.log 2>&1 &

# 6. 실행 확인
sleep 2
NEW_SERVER_PID=$(pgrep -f "venv/bin/python app.py")

if [ -n "$NEW_SERVER_PID" ]; then
    echo "✅ 서버가 성공적으로 시작되었습니다 (PID: $NEW_SERVER_PID)"
else
    echo "❌ 서버 시작 실패! 로그를 확인하세요"
    tail -n 10 logs/app.log
    exit 1
fi

echo "🎉 배포 완료"