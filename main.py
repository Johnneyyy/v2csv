#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import sys
from pathlib import Path
from video_processor import VideoProcessor
from config import Config

def main():
    parser = argparse.ArgumentParser(description='MP4 동영상에서 숫자를 추출하여 CSV로 저장')
    parser.add_argument('video_path', help='처리할 MP4 동영상 파일 경로')
    parser.add_argument('-o', '--output', help='출력 CSV 파일 경로 (기본값: extracted_numbers.csv)')
    parser.add_argument('--setup-roi', action='store_true', help='ROI 영역 설정 도움말 표시')
    parser.add_argument('--edit-roi', action='store_true', help='ROI 편집기 시작 (마우스로 ROI 수정 가능)')
    parser.add_argument('--frame-skip', type=int, default=30, help='프레임 건너뛰기 간격 (기본값: 30)')
    parser.add_argument('--ocr-engine', choices=['easyocr', 'tesseract'], default='easyocr', 
                       help='사용할 OCR 엔진 선택 (기본값: easyocr)')
    
    args = parser.parse_args()
    
    # 동영상 파일 존재 확인
    if not os.path.exists(args.video_path):
        print(f"오류: 동영상 파일을 찾을 수 없습니다: {args.video_path}")
        sys.exit(1)
    
    # 설정 조정
    config = Config()
    config.FRAME_SKIP = args.frame_skip
    config.OCR_ENGINE = args.ocr_engine
    if args.output:
        config.OUTPUT_CSV = args.output
    
    # VideoProcessor 초기화
    processor = VideoProcessor(args.video_path, config)
    
    # ROI 설정 도움말
    if args.setup_roi:
        print("ROI 영역 설정 모드")
        processor.show_roi_setup()
        print("\n설정 방법:")
        print("1. 생성된 'roi_setup.jpg' 이미지를 확인하세요.")
        print("2. 숫자가 나타나는 영역의 좌표를 측정하세요.")
        print("3. config.py 파일의 ROI_REGION_1, ROI_REGION_2 값을 수정하세요.")
        print("4. 형식: (x, y, width, height)")
        return
    
    # ROI 편집기 시작
    if args.edit_roi:
        print("ROI 편집기 시작")
        print("마우스로 ROI1, ROI2 영역을 드래그하여 위치를 수정할 수 있습니다.")
        print("설정 완료 후 'S' 키를 눌러 저장하세요.")
        processor.start_roi_editor()
        return
    
    try:
        print(f"동영상 처리 시작: {args.video_path}")
        print(f"OCR 엔진: {config.OCR_ENGINE}")
        print(f"프레임 건너뛰기: {config.FRAME_SKIP}")
        
        # 동영상 처리
        df = processor.process_video()
        
        # 결과 요약 출력
        print("\n=== 처리 결과 요약 ===")
        print(f"총 처리된 프레임: {len(df)}")
        print(f"숫자1 인식 성공: {df['number_1'].notna().sum()}개")
        print(f"숫자2 인식 성공: {df['number_2'].notna().sum()}개")
        
        # CSV로 저장
        output_file = processor.save_to_csv(df)
        
        # 결과 미리보기
        print(f"\n=== 결과 미리보기 (처음 10행) ===")
        print(df.head(10).to_string())
        
        print(f"\n작업 완료! 결과 파일: {output_file}")
        
        if config.SAVE_DEBUG_IMAGES:
            print(f"디버그 이미지: {config.DEBUG_DIR}/ 폴더")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()