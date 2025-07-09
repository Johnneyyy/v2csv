#!/usr/bin/env python3
"""
Video ROI Editor 사용 예제

이 파일은 video_roi_editer.py의 사용법을 보여줍니다.
"""

from video_roi_editer import VideoROIEditor

def example_usage():
    """기본 사용법 예제"""
    
    # 1. 동영상 파일 경로 설정
    video_path = "your_video.mp4"  # 실제 동영상 파일 경로로 변경하세요
    
    # 2. VideoROIEditor 인스턴스 생성
    editor = VideoROIEditor(video_path)
    
    # 3. 대화형 ROI 설정 (처음 사용 시)
    print("=== 대화형 ROI 설정 ===")
    print("동영상의 첫 번째 프레임이 표시됩니다.")
    print("마우스로 숫자가 있는 영역을 클릭하여 ROI를 설정하세요.")
    
    # editor.interactive_roi_setup()
    
    # 4. 프레임 스킵 설정 (옵션)
    editor.set_frame_skip(30)  # 30프레임마다 처리 (1초마다, 30fps 기준)
    
    # 5. ROI 크기 설정 (옵션)
    editor.set_roi_size(200, 80)  # 너비 200, 높이 80
    
    # 6. 동영상 처리 및 CSV 생성
    print("=== 동영상 처리 시작 ===")
    df = editor.process_video("output_numbers.csv")
    
    # 7. 결과 확인
    print("\n=== 결과 확인 ===")
    print(df.head())
    print(f"총 {len(df)}개의 프레임이 처리되었습니다.")

def advanced_usage():
    """고급 사용법 예제"""
    
    video_path = "your_video.mp4"
    editor = VideoROIEditor(video_path)
    
    # 1. 기존 ROI 설정 불러오기
    editor.load_roi_config("my_roi_config.json")
    
    # 2. 설정 확인
    editor.preview_roi_regions()
    
    # 3. 커스텀 설정으로 처리
    editor.set_frame_skip(60)  # 2초마다 처리
    editor.set_roi_size(150, 60)  # 더 작은 ROI 크기
    
    # 4. 처리 실행
    df = editor.process_video("custom_output.csv")
    
    # 5. 결과 분석
    print("\n=== 결과 분석 ===")
    for col in df.columns:
        if col.startswith('roi_') and col.endswith('_number'):
            roi_num = col.split('_')[1]
            valid_count = df[col].notna().sum()
            success_rate = (valid_count / len(df)) * 100
            print(f"ROI {roi_num}: {success_rate:.1f}% 인식 성공률")

def command_line_examples():
    """커맨드라인 사용법 예제"""
    
    print("=== 커맨드라인 사용법 ===")
    print()
    
    print("1. ROI 설정 모드:")
    print("   python video_roi_editer.py video.mp4 --setup")
    print()
    
    print("2. 기본 동영상 처리:")
    print("   python video_roi_editer.py video.mp4")
    print()
    
    print("3. 커스텀 설정으로 처리:")
    print("   python video_roi_editer.py video.mp4 --frame-skip 60 --roi-width 150 --roi-height 60")
    print()
    
    print("4. 특정 출력 파일로 저장:")
    print("   python video_roi_editer.py video.mp4 --output my_results.csv")
    print()
    
    print("5. ROI 미리보기:")
    print("   python video_roi_editer.py video.mp4 --preview")
    print()
    
    print("6. 커스텀 설정 파일 사용:")
    print("   python video_roi_editer.py video.mp4 --config my_config.json")

if __name__ == "__main__":
    print("Video ROI Editor 사용 예제")
    print("=" * 50)
    
    # 커맨드라인 사용법 설명
    command_line_examples()
    
    print("\n" + "=" * 50)
    print("프로그래밍 방식 사용법:")
    print("실제 동영상 파일이 있을 때 아래 함수들을 실행하세요.")
    print("- example_usage(): 기본 사용법")
    print("- advanced_usage(): 고급 사용법")