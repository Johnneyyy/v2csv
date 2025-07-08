#!/bin/bash

echo "MP4 동영상 숫자 추출기 설치 시작..."

# Python 및 pip 확인
if ! command -v python3 &> /dev/null; then
    echo "Python3이 설치되어 있지 않습니다."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "pip3이 설치되어 있지 않습니다."
    exit 1
fi

# 시스템 패키지 업데이트 및 설치
echo "시스템 패키지 설치 중..."
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-kor libgl1-mesa-glx libglib2.0-0

# Python 패키지 설치
echo "Python 패키지 설치 중..."
pip3 install -r requirements.txt

# 디렉토리 생성
mkdir -p debug_frames

echo "설치 완료!"
echo ""
echo "사용법:"
echo "1. ROI 설정: python3 main.py video.mp4 --setup-roi"
echo "2. 동영상 처리: python3 main.py video.mp4"
echo ""
echo "자세한 사용법은 README.md를 참조하세요."