import cv2
import os
import pandas as pd
import numpy as np
from typing import List, Tuple, Optional, Dict
from tqdm import tqdm
import argparse
import json
from config import Config
from ocr_reader import OCRReader

class VideoROIEditor:
    def __init__(self, video_path: str, config: Optional[Config] = None):
        self.video_path = video_path
        self.config = config or Config()
        self.ocr_reader = OCRReader(self.config.OCR_ENGINE)
        self.results = []
        self.roi_regions = []
        self.frame_skip = self.config.FRAME_SKIP
        self.roi_size = (200, 80)  # 기본 ROI 크기 (width, height)
        
        # 디버그 디렉토리 생성
        if self.config.SAVE_DEBUG_IMAGES:
            os.makedirs(self.config.DEBUG_DIR, exist_ok=True)
    
    def interactive_roi_setup(self):
        """대화형 ROI 영역 설정"""
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print(f"동영상을 열 수 없습니다: {self.video_path}")
            return
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            return
        
        print("\n=== ROI 영역 설정 ===")
        print("클릭하여 ROI 영역을 설정하세요.")
        print("- 좌클릭: ROI 영역 추가")
        print("- 우클릭: 마지막 ROI 영역 삭제")
        print("- 'r' 키: 모든 ROI 영역 초기화")
        print("- 's' 키: 현재 ROI 설정 저장")
        print("- 'q' 키: 종료")
        print("- '+/-' 키: ROI 크기 조절")
        
        self.roi_regions = []
        self.setup_frame = frame.copy()
        
        cv2.namedWindow("ROI Setup", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("ROI Setup", self._mouse_callback)
        
        while True:
            display_frame = self.setup_frame.copy()
            
            # ROI 영역 표시
            for i, (x, y, w, h) in enumerate(self.roi_regions):
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(display_frame, f"ROI {i+1}", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 현재 ROI 크기 표시
            cv2.putText(display_frame, f"ROI Size: {self.roi_size[0]}x{self.roi_size[1]}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display_frame, f"ROI Count: {len(self.roi_regions)}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("ROI Setup", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.roi_regions = []
                print("모든 ROI 영역이 초기화되었습니다.")
            elif key == ord('s'):
                self._save_roi_config()
                print("ROI 설정이 저장되었습니다.")
            elif key == ord('+') or key == ord('='):
                self.roi_size = (min(self.roi_size[0] + 20, 500), min(self.roi_size[1] + 20, 300))
                print(f"ROI 크기: {self.roi_size}")
            elif key == ord('-'):
                self.roi_size = (max(self.roi_size[0] - 20, 50), max(self.roi_size[1] - 20, 30))
                print(f"ROI 크기: {self.roi_size}")
        
        cv2.destroyAllWindows()
    
    def _mouse_callback(self, event, x, y, flags, param):
        """마우스 콜백 함수"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # ROI 영역 추가
            w, h = self.roi_size
            roi = (x - w//2, y - h//2, w, h)
            self.roi_regions.append(roi)
            print(f"ROI {len(self.roi_regions)} 추가: {roi}")
        
        elif event == cv2.EVENT_RBUTTONDOWN:
            # 마지막 ROI 영역 삭제
            if self.roi_regions:
                removed = self.roi_regions.pop()
                print(f"ROI 삭제: {removed}")
    
    def _save_roi_config(self):
        """ROI 설정을 파일로 저장"""
        config_data = {
            'roi_regions': self.roi_regions,
            'roi_size': self.roi_size,
            'frame_skip': self.frame_skip
        }
        
        with open('roi_config.json', 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print("ROI 설정이 roi_config.json에 저장되었습니다.")
    
    def load_roi_config(self, config_file: str = 'roi_config.json'):
        """ROI 설정을 파일에서 불러오기"""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            self.roi_regions = config_data.get('roi_regions', [])
            self.roi_size = tuple(config_data.get('roi_size', (200, 80)))
            self.frame_skip = config_data.get('frame_skip', self.frame_skip)
            
            print(f"ROI 설정을 {config_file}에서 불러왔습니다.")
            print(f"ROI 영역 수: {len(self.roi_regions)}")
            print(f"ROI 크기: {self.roi_size}")
            print(f"Frame skip: {self.frame_skip}")
        else:
            print(f"설정 파일 {config_file}이 존재하지 않습니다.")
    
    def set_frame_skip(self, skip: int):
        """프레임 스킵 설정"""
        self.frame_skip = max(1, skip)
        print(f"Frame skip을 {self.frame_skip}로 설정했습니다.")
    
    def set_roi_size(self, width: int, height: int):
        """ROI 크기 설정"""
        self.roi_size = (max(50, width), max(30, height))
        print(f"ROI 크기를 {self.roi_size}로 설정했습니다.")
    
    def process_video(self, output_csv: Optional[str] = None) -> pd.DataFrame:
        """동영상을 처리하여 숫자를 추출하고 CSV로 저장"""
        if not self.roi_regions:
            print("ROI 영역이 설정되지 않았습니다. interactive_roi_setup()을 먼저 실행하세요.")
            return pd.DataFrame()
        
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            raise ValueError(f"동영상을 열 수 없습니다: {self.video_path}")
        
        # 동영상 정보 가져오기
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        print(f"\n=== 동영상 처리 시작 ===")
        print(f"동영상 정보:")
        print(f"- FPS: {fps}")
        print(f"- 총 프레임 수: {total_frames}")
        print(f"- 길이: {duration:.2f}초")
        print(f"- ROI 영역 수: {len(self.roi_regions)}")
        print(f"- Frame skip: {self.frame_skip}")
        
        frame_count = 0
        processed_frames = 0
        self.results = []
        
        # 진행률 표시
        pbar = tqdm(total=total_frames, desc="동영상 처리 중")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 지정된 간격으로만 프레임 처리
                if frame_count % self.frame_skip == 0:
                    timestamp = frame_count / fps
                    self._process_frame(frame, timestamp, processed_frames)
                    processed_frames += 1
                
                frame_count += 1
                pbar.update(1)
        
        finally:
            cap.release()
            pbar.close()
        
        print(f"처리 완료: {processed_frames}개 프레임 처리됨")
        
        # DataFrame 생성
        df = self._create_dataframe()
        
        # CSV 저장
        if output_csv is None:
            output_csv = self.config.OUTPUT_CSV
        
        self.save_to_csv(df, output_csv)
        
        return df
    
    def _process_frame(self, frame: np.ndarray, timestamp: float, frame_idx: int):
        """개별 프레임 처리"""
        result = {
            'timestamp': timestamp,
            'frame_index': frame_idx,
        }
        
        # 각 ROI 영역에서 숫자 추출
        for i, (x, y, w, h) in enumerate(self.roi_regions):
            roi = frame[y:y+h, x:x+w]
            number = self.ocr_reader.extract_numbers(roi)
            result[f'roi_{i+1}_number'] = number
        
        self.results.append(result)
        
        # 디버그 이미지 저장
        if self.config.SAVE_DEBUG_IMAGES and frame_idx % 10 == 0:
            self._save_debug_frame(frame, frame_idx, result)
    
    def _save_debug_frame(self, frame: np.ndarray, frame_idx: int, result: Dict):
        """디버그용 프레임 저장"""
        debug_frame = frame.copy()
        
        # ROI 영역 표시
        for i, (x, y, w, h) in enumerate(self.roi_regions):
            cv2.rectangle(debug_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(debug_frame, f"ROI {i+1}", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 추출된 숫자 표시
            number = result.get(f'roi_{i+1}_number', 'None')
            number_text = str(number) if number is not None else 'None'
            cv2.putText(debug_frame, number_text, (x, y+h+20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # 타임스탬프 표시
        cv2.putText(debug_frame, f"Time: {result['timestamp']:.2f}s", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # 파일 저장
        filename = f"{self.config.DEBUG_DIR}/frame_{frame_idx:06d}.jpg"
        cv2.imwrite(filename, debug_frame)
    
    def _create_dataframe(self) -> pd.DataFrame:
        """결과를 DataFrame으로 변환"""
        df = pd.DataFrame(self.results)
        
        # 숫자 컬럼들을 수치형으로 변환
        for col in df.columns:
            if col.startswith('roi_') and col.endswith('_number'):
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def save_to_csv(self, df: pd.DataFrame, output_path: str) -> str:
        """결과를 CSV 파일로 저장"""
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"결과가 CSV로 저장되었습니다: {output_path}")
        
        # 통계 정보 출력
        print(f"\n=== 추출 결과 통계 ===")
        print(f"총 프레임 수: {len(df)}")
        
        for col in df.columns:
            if col.startswith('roi_') and col.endswith('_number'):
                roi_num = col.split('_')[1]
                valid_count = df[col].notna().sum()
                print(f"ROI {roi_num}: {valid_count}/{len(df)} 프레임에서 숫자 인식 성공")
        
        return output_path
    
    def preview_roi_regions(self):
        """ROI 영역 미리보기"""
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print(f"동영상을 열 수 없습니다: {self.video_path}")
            return
        
        ret, frame = cap.read()
        cap.release()
        
        if ret and self.roi_regions:
            display_frame = frame.copy()
            
            for i, (x, y, w, h) in enumerate(self.roi_regions):
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(display_frame, f"ROI {i+1} ({w}x{h})", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 미리보기 이미지 저장
            cv2.imwrite("roi_preview.jpg", display_frame)
            print("ROI 미리보기가 'roi_preview.jpg'로 저장되었습니다.")
        else:
            print("ROI 영역이 설정되지 않았거나 프레임을 읽을 수 없습니다.")

def main():
    """메인 함수 - 커맨드라인 인터페이스"""
    parser = argparse.ArgumentParser(description='Video ROI Editor - 동영상에서 ROI 영역 설정 및 숫자 추출')
    parser.add_argument('video_path', help='처리할 동영상 파일 경로')
    parser.add_argument('--config', '-c', default='roi_config.json', help='ROI 설정 파일 경로')
    parser.add_argument('--output', '-o', help='출력 CSV 파일 경로')
    parser.add_argument('--frame-skip', '-f', type=int, help='프레임 스킵 설정')
    parser.add_argument('--roi-width', '-w', type=int, help='ROI 너비')
    parser.add_argument('--roi-height', '--height', type=int, help='ROI 높이')
    parser.add_argument('--setup', '-s', action='store_true', help='ROI 설정 모드')
    parser.add_argument('--preview', '-p', action='store_true', help='ROI 미리보기')
    
    args = parser.parse_args()
    
    # VideoROIEditor 인스턴스 생성
    editor = VideoROIEditor(args.video_path)
    
    # 설정 불러오기
    editor.load_roi_config(args.config)
    
    # 프레임 스킵 설정
    if args.frame_skip:
        editor.set_frame_skip(args.frame_skip)
    
    # ROI 크기 설정
    if args.roi_width and args.roi_height:
        editor.set_roi_size(args.roi_width, args.roi_height)
    
    # 모드에 따른 실행
    if args.setup:
        editor.interactive_roi_setup()
    elif args.preview:
        editor.preview_roi_regions()
    else:
        # 동영상 처리 실행
        editor.process_video(args.output)

if __name__ == "__main__":
    main()