import cv2
import os
import pandas as pd
import numpy as np
from typing import List, Tuple, Optional
from tqdm import tqdm
from config import Config
from ocr_reader import OCRReader

class VideoProcessor:
    def __init__(self, video_path: str, config: Optional[Config] = None):
        self.video_path = video_path
        self.config = config or Config()
        self.ocr_reader = OCRReader(self.config.OCR_ENGINE)
        self.results = []
        
        # 디버그 디렉토리 생성
        if self.config.SAVE_DEBUG_IMAGES:
            os.makedirs(self.config.DEBUG_DIR, exist_ok=True)
    
    def process_video(self) -> pd.DataFrame:
        """동영상을 처리하여 숫자를 추출"""
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            raise ValueError(f"동영상을 열 수 없습니다: {self.video_path}")
        
        # 동영상 정보 가져오기
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        print(f"동영상 정보:")
        print(f"- FPS: {fps}")
        print(f"- 총 프레임 수: {total_frames}")
        print(f"- 길이: {duration:.2f}초")
        
        frame_count = 0
        processed_frames = 0
        
        # 진행률 표시
        pbar = tqdm(total=total_frames, desc="동영상 처리 중")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 지정된 간격으로만 프레임 처리
                if frame_count % self.config.FRAME_SKIP == 0:
                    timestamp = frame_count / fps
                    self._process_frame(frame, timestamp, processed_frames)
                    processed_frames += 1
                
                frame_count += 1
                pbar.update(1)
        
        finally:
            cap.release()
            pbar.close()
        
        print(f"처리 완료: {processed_frames}개 프레임 처리됨")
        return self._create_dataframe()
    
    def _process_frame(self, frame: np.ndarray, timestamp: float, frame_idx: int):
        """개별 프레임 처리"""
        regions = [self.config.ROI_REGION_1, self.config.ROI_REGION_2]
        number1, number2 = self.ocr_reader.extract_from_regions(frame, regions)
        
        # 결과 저장
        result = {
            'timestamp': timestamp,
            'frame_index': frame_idx,
            'number_1': number1,
            'number_2': number2
        }
        self.results.append(result)
        
        # 디버그 이미지 저장
        if self.config.SAVE_DEBUG_IMAGES and frame_idx % 10 == 0:  # 10프레임마다 저장
            self._save_debug_frame(frame, regions, frame_idx, number1, number2)
    
    def _save_debug_frame(self, frame: np.ndarray, regions: List[Tuple], 
                         frame_idx: int, number1: Optional[str], number2: Optional[str]):
        """디버그용 프레임 저장"""
        debug_frame = frame.copy()
        
        # ROI 영역 표시
        for i, (x, y, w, h) in enumerate(regions):
            cv2.rectangle(debug_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(debug_frame, f"ROI {i+1}", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 추출된 숫자 표시
        cv2.putText(debug_frame, f"N1: {number1 or 'None'}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(debug_frame, f"N2: {number2 or 'None'}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # 파일 저장
        filename = f"{self.config.DEBUG_DIR}/frame_{frame_idx:06d}.jpg"
        cv2.imwrite(filename, debug_frame)
    
    def _create_dataframe(self) -> pd.DataFrame:
        """결과를 DataFrame으로 변환"""
        df = pd.DataFrame(self.results)
        return df
    
    def save_to_csv(self, df: pd.DataFrame, output_path: Optional[str] = None) -> str:
        """결과를 CSV 파일로 저장"""
        if output_path is None:
            output_path = self.config.OUTPUT_CSV
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"결과가 저장되었습니다: {output_path}")
        return output_path
    
    def show_roi_setup(self, video_path: Optional[str] = None):
        """ROI 영역 설정을 위한 도우미 함수"""
        if video_path is None:
            video_path = self.video_path
            
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"동영상을 열 수 없습니다: {video_path}")
            return
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # ROI 영역 표시
            display_frame = frame.copy()
            regions = [self.config.ROI_REGION_1, self.config.ROI_REGION_2]
            
            for i, (x, y, w, h) in enumerate(regions):
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(display_frame, f"ROI {i+1}", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 이미지 저장
            cv2.imwrite("roi_setup.jpg", display_frame)
            print("ROI 설정 이미지가 'roi_setup.jpg'로 저장되었습니다.")
            print("config.py 파일에서 ROI_REGION_1, ROI_REGION_2 값을 조정하세요.")
        else:
            print("프레임을 읽을 수 없습니다.")
    
    def start_roi_editor(self):
        """ROI 편집기 시작"""
        try:
            from video_roi_editor import VideoROIEditor
            editor = VideoROIEditor(self.video_path, self.config)
            editor.run()
        except ImportError:
            print("video_roi_editor.py 모듈을 찾을 수 없습니다.")
        except Exception as e:
            print(f"ROI 편집기 실행 중 오류 발생: {e}")
