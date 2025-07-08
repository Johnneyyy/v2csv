# 동영상 처리 설정
class Config:
    def __init__(self):
        # ROI (Region of Interest) 설정 - 숫자가 나타나는 영역
        # 형식: (x, y, width, height)
        self.ROI_REGION_1 = (100, 50, 200, 80)   # 첫 번째 숫자 영역
        self.ROI_REGION_2 = (500, 50, 200, 80)   # 두 번째 숫자 영역
        
        # OCR 설정
        self.OCR_ENGINE = "easyocr"  # "easyocr" 또는 "tesseract"
        self.TESSERACT_CONFIG = '--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789.-'
        
        # 프레임 처리 설정
        self.FRAME_SKIP = 30  # 30프레임마다 처리 (1초마다, 30fps 기준)
        
        # 출력 설정
        self.OUTPUT_CSV = "extracted_numbers.csv"
        
        # 디버그 설정
        self.SAVE_DEBUG_IMAGES = True
        self.DEBUG_DIR = "debug_frames"