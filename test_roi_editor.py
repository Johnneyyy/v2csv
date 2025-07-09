#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ROI 편집기 테스트 스크립트
"""

import os
import sys
from pathlib import Path

def test_roi_editor():
    """ROI 편집기 테스트"""
    
    print("=== ROI 편집기 테스트 ===")
    print()
    
    # 테스트 동영상 파일 경로 입력
    while True:
        video_path = input("동영상 파일 경로를 입력하세요 (또는 'q'로 종료): ").strip()
        
        if video_path.lower() == 'q':
            print("종료합니다.")
            return
        
        if not video_path:
            print("파일 경로를 입력해주세요.")
            continue
            
        if not os.path.exists(video_path):
            print(f"파일을 찾을 수 없습니다: {video_path}")
            continue
        
        break
    
    print(f"동영상 파일: {video_path}")
    print()
    
    # 모드 선택
    print("모드를 선택하세요:")
    print("1. 기본 ROI 설정 확인 (이미지 저장)")
    print("2. ROI 편집기 시작 (대화형)")
    print("3. 동영상 처리 실행")
    print("4. 종료")
    
    while True:
        choice = input("\n선택 (1-4): ").strip()
        
        if choice == '1':
            # 기본 ROI 설정 확인
            print("기본 ROI 설정 확인 중...")
            try:
                from video_processor import VideoProcessor
                processor = VideoProcessor(video_path)
                processor.show_roi_setup()
                print("roi_setup.jpg 파일이 생성되었습니다.")
            except Exception as e:
                print(f"오류 발생: {e}")
            break
            
        elif choice == '2':
            # ROI 편집기 시작
            print("ROI 편집기를 시작합니다...")
            print("조작법:")
            print("- 마우스로 ROI1, ROI2 영역을 드래그하여 이동")
            print("- SPACE: 재생/일시정지")
            print("- R: ROI 리셋")
            print("- S: ROI 설정 저장")
            print("- Q: 종료")
            print()
            
            try:
                from video_roi_editor import VideoROIEditor
                editor = VideoROIEditor(video_path)
                editor.run()
            except Exception as e:
                print(f"오류 발생: {e}")
            break
            
        elif choice == '3':
            # 동영상 처리 실행
            print("동영상 처리를 시작합니다...")
            try:
                from video_processor import VideoProcessor
                processor = VideoProcessor(video_path)
                df = processor.process_video()
                output_file = processor.save_to_csv(df)
                print(f"처리 완료! 결과 파일: {output_file}")
            except Exception as e:
                print(f"오류 발생: {e}")
            break
            
        elif choice == '4':
            print("종료합니다.")
            return
        else:
            print("올바른 번호를 입력해주세요 (1-4)")

def main():
    """메인 함수"""
    try:
        test_roi_editor()
    except KeyboardInterrupt:
        print("\n사용자가 중단했습니다.")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")

if __name__ == "__main__":
    main()