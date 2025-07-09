#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
from typing import Tuple, Optional, List
from config import Config

class VideoROIEditor:
    def __init__(self, video_path: str, config: Optional[Config] = None):
        self.video_path = video_path
        self.config = config or Config()
        self.cap = None
        self.current_frame = None
        self.frame_count = 0
        self.total_frames = 0
        self.fps = 30
        self.playing = False
        self.paused = True
        
        # ROI 설정
        self.roi_regions = [
            list(self.config.ROI_REGION_1),  # [x, y, w, h]
            list(self.config.ROI_REGION_2)   # [x, y, w, h]
        ]
        
        # 마우스 상태
        self.mouse_dragging = False
        self.selected_roi = -1  # -1: 선택 안됨, 0: ROI1, 1: ROI2
        self.drag_start_pos = None
        self.drag_offset = None
        
        # UI 상태
        self.show_roi = True
        self.window_name = "Video ROI Editor"
        
        # 색상 정의
        self.roi_colors = [(0, 255, 0), (0, 0, 255)]  # 초록, 빨강
        self.roi_names = ["ROI1", "ROI2"]
    
    def _init_video(self):
        """동영상 초기화"""
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise ValueError(f"동영상을 열 수 없습니다: {self.video_path}")
        
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        # 첫 번째 프레임 읽기
        ret, self.current_frame = self.cap.read()
        if not ret:
            raise ValueError("첫 번째 프레임을 읽을 수 없습니다.")
    
    def _mouse_callback(self, event, x, y, flags, param):
        """마우스 이벤트 콜백"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self._on_mouse_down(x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            self._on_mouse_move(x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self._on_mouse_up(x, y)
    
    def _on_mouse_down(self, x, y):
        """마우스 버튼 누름"""
        # 어떤 ROI를 선택했는지 확인
        for i, (roi_x, roi_y, roi_w, roi_h) in enumerate(self.roi_regions):
            if roi_x <= x <= roi_x + roi_w and roi_y <= y <= roi_y + roi_h:
                self.selected_roi = i
                self.mouse_dragging = True
                self.drag_start_pos = (x, y)
                self.drag_offset = (x - roi_x, y - roi_y)
                print(f"{self.roi_names[i]} 선택됨")
                break
    
    def _on_mouse_move(self, x, y):
        """마우스 이동"""
        if self.mouse_dragging and self.selected_roi >= 0:
            # ROI 위치 업데이트
            new_x = max(0, x - self.drag_offset[0])
            new_y = max(0, y - self.drag_offset[1])
            
            # 화면 경계 확인
            if self.current_frame is not None:
                h, w = self.current_frame.shape[:2]
                roi_w, roi_h = self.roi_regions[self.selected_roi][2], self.roi_regions[self.selected_roi][3]
                new_x = min(new_x, w - roi_w)
                new_y = min(new_y, h - roi_h)
            
            self.roi_regions[self.selected_roi][0] = new_x
            self.roi_regions[self.selected_roi][1] = new_y
    
    def _on_mouse_up(self, x, y):
        """마우스 버튼 릴리즈"""
        if self.mouse_dragging and self.selected_roi >= 0:
            print(f"{self.roi_names[self.selected_roi]} 위치 업데이트: {tuple(self.roi_regions[self.selected_roi])}")
        
        self.mouse_dragging = False
        self.selected_roi = -1
        self.drag_start_pos = None
        self.drag_offset = None
    
    def _draw_roi_overlay(self, frame):
        """ROI 오버레이 그리기"""
        if not self.show_roi:
            return frame
        
        overlay_frame = frame.copy()
        
        for i, (x, y, w, h) in enumerate(self.roi_regions):
            color = self.roi_colors[i]
            
            # ROI 사각형 그리기
            if self.selected_roi == i:
                # 선택된 ROI는 두껍게
                cv2.rectangle(overlay_frame, (x, y), (x + w, y + h), color, 3)
            else:
                cv2.rectangle(overlay_frame, (x, y), (x + w, y + h), color, 2)
            
            # ROI 이름 표시
            cv2.putText(overlay_frame, self.roi_names[i], (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # ROI 좌표 표시
            coord_text = f"({x},{y},{w},{h})"
            cv2.putText(overlay_frame, coord_text, (x, y + h + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return overlay_frame
    
    def _draw_ui_info(self, frame):
        """UI 정보 그리기"""
        h, w = frame.shape[:2]
        
        # 상태 정보
        status_text = "PLAYING" if self.playing and not self.paused else "PAUSED"
        cv2.putText(frame, f"Status: {status_text}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 프레임 정보
        cv2.putText(frame, f"Frame: {self.frame_count}/{self.total_frames}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 도움말
        help_text = [
            "Controls:",
            "SPACE: Play/Pause",
            "R: Reset ROI",
            "S: Save ROI",
            "H: Toggle Help",
            "Q: Quit"
        ]
        
        for i, text in enumerate(help_text):
            cv2.putText(frame, text, (10, h - 150 + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def _get_next_frame(self):
        """다음 프레임 가져오기"""
        if self.cap is None:
            return False
        
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            self.frame_count += 1
            return True
        else:
            # 동영상 끝에 도달하면 처음으로 돌아가기
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.frame_count = 0
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                self.frame_count += 1
                return True
        
        return False
    
    def _save_roi_config(self):
        """ROI 설정을 config.py에 저장"""
        try:
            config_content = f"""# 동영상 처리 설정
class Config:
    def __init__(self):
        # ROI (Region of Interest) 설정 - 숫자가 나타나는 영역
        # 형식: (x, y, width, height)
        self.ROI_REGION_1 = {tuple(self.roi_regions[0])}   # 첫 번째 숫자 영역
        self.ROI_REGION_2 = {tuple(self.roi_regions[1])}   # 두 번째 숫자 영역
        
        # OCR 설정
        self.OCR_ENGINE = "{self.config.OCR_ENGINE}"  # "easyocr" 또는 "tesseract"
        self.TESSERACT_CONFIG = '{self.config.TESSERACT_CONFIG}'
        
        # 프레임 처리 설정
        self.FRAME_SKIP = {self.config.FRAME_SKIP}  # 30프레임마다 처리 (1초마다, 30fps 기준)
        
        # 출력 설정
        self.OUTPUT_CSV = "{self.config.OUTPUT_CSV}"
        
        # 디버그 설정
        self.SAVE_DEBUG_IMAGES = {self.config.SAVE_DEBUG_IMAGES}
        self.DEBUG_DIR = "{self.config.DEBUG_DIR}"
"""
            
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            print("ROI 설정이 config.py에 저장되었습니다.")
            print(f"ROI1: {tuple(self.roi_regions[0])}")
            print(f"ROI2: {tuple(self.roi_regions[1])}")
            
        except Exception as e:
            print(f"설정 저장 중 오류 발생: {e}")
    
    def _reset_roi(self):
        """ROI를 초기값으로 리셋"""
        self.roi_regions = [
            list(self.config.ROI_REGION_1),
            list(self.config.ROI_REGION_2)
        ]
        print("ROI가 초기값으로 리셋되었습니다.")
    
    def run(self):
        """ROI 에디터 실행"""
        try:
            self._init_video()
            
            cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
            cv2.setMouseCallback(self.window_name, self._mouse_callback)
            
            print("=== Video ROI Editor ===")
            print("조작법:")
            print("- 마우스로 ROI 영역을 드래그하여 이동")
            print("- SPACE: 재생/일시정지")
            print("- R: ROI 리셋")
            print("- S: ROI 설정 저장")
            print("- Q: 종료")
            print("========================")
            
            while True:
                if self.playing and not self.paused:
                    if not self._get_next_frame():
                        break
                
                if self.current_frame is not None:
                    # ROI 오버레이 그리기
                    display_frame = self._draw_roi_overlay(self.current_frame)
                    
                    # UI 정보 그리기
                    display_frame = self._draw_ui_info(display_frame)
                    
                    cv2.imshow(self.window_name, display_frame)
                
                # 키 입력 처리
                key = cv2.waitKey(30) & 0xFF
                
                if key == ord('q') or key == 27:  # Q 또는 ESC
                    break
                elif key == ord(' '):  # SPACE
                    if self.playing:
                        self.paused = not self.paused
                    else:
                        self.playing = True
                        self.paused = False
                elif key == ord('r'):  # R
                    self._reset_roi()
                elif key == ord('s'):  # S
                    self._save_roi_config()
                elif key == ord('h'):  # H
                    self.show_roi = not self.show_roi
        
        except Exception as e:
            print(f"오류 발생: {e}")
        
        finally:
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()

def main():
    """메인 함수"""
    import sys
    
    if len(sys.argv) != 2:
        print("사용법: python video_roi_editor.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"동영상 파일을 찾을 수 없습니다: {video_path}")
        sys.exit(1)
    
    editor = VideoROIEditor(video_path)
    editor.run()

if __name__ == "__main__":
    import os
    main()