#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MP4 동영상 숫자 추출기 사용 예제
"""

import os
import sys
from video_processor import VideoProcessor
from config import Config

def main():
    print("=== MP4 동영상 숫자 추출기 예제 ===\n")
    
    # 예제 동영상 파일 경로 (사용자가 변경해야 함)
    video_path = "sample_video.mp4"
    
    if not os.path.exists(video_path):
        print(f"예제 동영상 파일이 없습니다: {video_path}")
        print("실제 MP4 파일 경로로 변경하세요.")
        print("\n사용법:")
        print("1. 이 스크립트에서 video_path 변수를 실제 MP4 파일 경로로 변경")
        print("2. 또는 main.py를 직접 사용:")
        print("   python3 main.py your_video.mp4")
        return
    
    # 설정 사용자 정의
    config = Config()
    
    # ROI 영역 조정 예제 (실제 동영상에 맞게 조정 필요)
    config.ROI_REGION_1 = (100, 50, 200, 80)   # 첫 번째 숫자 영역
    config.ROI_REGION_2 = (500, 50, 200, 80)   # 두 번째 숫자 영역
    
    # 처리 설정
    config.FRAME_SKIP = 30  # 30프레임마다 처리 (약 1초마다)
    config.OCR_ENGINE = "easyocr"  # 또는 "tesseract"
    config.SAVE_DEBUG_IMAGES = True
    config.OUTPUT_CSV = "example_output.csv"
    
    try:
        # VideoProcessor 초기화
        processor = VideoProcessor(video_path, config)
        
        # ROI 설정 확인 (선택사항)
        print("ROI 설정 확인 중...")
        processor.show_roi_setup()
        
        # ROI 편집기 사용 예제 (주석 해제하여 사용)
        # print("ROI 편집기를 사용하려면 다음 라인의 주석을 해제하세요:")
        # processor.start_roi_editor()
        # return  # ROI 편집기를 사용한 후 종료
        
        # 동영상 처리
        print("동영상 처리 시작...")
        df = processor.process_video()
        
        # 결과 저장
        output_file = processor.save_to_csv(df)
        
        # 결과 요약
        print(f"\n=== 처리 결과 ===")
        print(f"총 처리된 프레임: {len(df)}")
        print(f"숫자1 인식 성공: {df['number_1'].notna().sum()}개")
        print(f"숫자2 인식 성공: {df['number_2'].notna().sum()}개")
        print(f"출력 파일: {output_file}")
        
        # 샘플 결과 출력
        print(f"\n=== 샘플 결과 (처음 5행) ===")
        print(df.head().to_string())
        
        print(f"\n디버그 이미지는 '{config.DEBUG_DIR}' 폴더에서 확인하세요.")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()