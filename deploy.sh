#!/bin/bash

echo "🔁 시작: 최신 변경사항 배포 중..."

# 절대 경로 설정
PROJECT_DIR="/home/nohdennis/market_ninja"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/app.log"

cd $PROJECT_DIR

# 1. 최신 코드 가져오기
echo "📥 Git 저장소에서 최신 코드 가져오기"
git pull origin main

# 2. 가상환경 확인 및 활성화
echo "🔍 가상환경 확인 중"
if [ ! -d "venv" ]; then
    echo "❌ 가상환경이 없습니다. 새로 생성합니다."
    python3 -m venv venv
fi

echo "📦 필요한 패키지 설치 중"
source venv/bin/activate
pip install -r requirements.txt

# 3. 기존 실행 중인 서버 확인 및 종료
echo "🔍 기존 프로세스 확인 중"
SERVER_PID=$(pgrep -f "python.*app.py")

if [ -n "$SERVER_PID" ]; then
    echo "🛑 기존 서버 종료 (PID: $SERVER_PID)"
    kill -9 $SERVER_PID
    sleep 2
else
    echo "ℹ️ 실행 중인 서버가 없습니다"
fi

# 4. 로그 디렉토리 확인 및 생성
if [ ! -d "$LOG_DIR" ]; then
    echo "📁 로그 디렉토리 생성"
    mkdir -p $LOG_DIR
fi

# 5. 새로운 프로세스로 실행
echo "🚀 새 서버 시작 중"
cd $PROJECT_DIR
source venv/bin/activate
nohup python app.py > $LOG_FILE 2>&1 &

# 6. 실행 확인
sleep 3
NEW_SERVER_PID=$(pgrep -f "python.*app.py")

if [ -n "$NEW_SERVER_PID" ]; then
    echo "✅ 서버가 성공적으로 시작되었습니다 (PID: $NEW_SERVER_PID)"
    echo "📝 로그 확인: tail -f $LOG_FILE"
else
    echo "❌ 서버 시작 실패! 로그를 확인하세요"
    echo "=== 마지막 20줄 로그 ==="
    tail -n 20 $LOG_FILE
    echo "====================="
    exit 1
fi

echo "🎉 배포 완료"