import cv2
import numpy as np
import pytesseract
import easyocr
import re
from typing import Optional, Tuple
from config import Config

class OCRReader:
    def __init__(self, engine: str = "easyocr"):
        self.engine = engine.lower()
        if self.engine == "easyocr":
            self.reader = easyocr.Reader(['en'], gpu=False)
        elif self.engine == "tesseract":
            # Tesseract 경로 설정 (Linux용)
            # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
            pass
        else:
            raise ValueError("지원되는 OCR 엔진: 'easyocr', 'tesseract'")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """이미지 전처리 - OCR 정확도 향상을 위함"""
        # 그레이스케일 변환
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 이미지 크기 확대 (OCR 정확도 향상)
        scale_factor = 3
        height, width = gray.shape
        resized = cv2.resize(gray, (width * scale_factor, height * scale_factor), 
                           interpolation=cv2.INTER_CUBIC)
        
        # 노이즈 제거
        denoised = cv2.medianBlur(resized, 3)
        
        # 이진화
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 모폴로지 연산으로 글자 연결
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def extract_numbers(self, image: np.ndarray) -> Optional[str]:
        """이미지에서 숫자 추출"""
        processed_image = self.preprocess_image(image)
        
        try:
            if self.engine == "easyocr":
                results = self.reader.readtext(processed_image)
                if results:
                    # 가장 신뢰도가 높은 결과 선택
                    best_result = max(results, key=lambda x: x[2])
                    text = best_result[1]
                else:
                    text = ""
            else:  # tesseract
                text = pytesseract.image_to_string(processed_image, config=Config().TESSERACT_CONFIG)
            
            # 숫자만 추출
            numbers = re.findall(r'-?\d+\.?\d*', text.strip())
            if numbers:
                return numbers[0]  # 첫 번째 숫자 반환
            return None
            
        except Exception as e:
            print(f"OCR 처리 중 오류: {e}")
            return None
    
    def extract_from_regions(self, frame: np.ndarray, regions: list) -> Tuple[Optional[str], Optional[str]]:
        """지정된 영역들에서 숫자 추출"""
        results = []
        
        for region in regions:
            x, y, w, h = region
            roi = frame[y:y+h, x:x+w]
            number = self.extract_numbers(roi)
            results.append(number)
        
        return tuple(results)