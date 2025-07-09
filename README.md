# MP4 동영상 숫자 추출기

MP4 동영상에서 화면의 2곳에 나타나는 숫자를 자동으로 인식하여 CSV 데이터로 변환하는 프로젝트입니다.

## 기능

- MP4 동영상 파일 읽기
- 화면의 지정된 2곳 영역에서 숫자 인식 (OCR)
- EasyOCR 또는 Tesseract OCR 엔진 지원
- 인식 결과를 CSV 파일로 저장
- 디버그 이미지 생성으로 ROI 설정 도움
- 프레임별 타임스탬프 기록

## 설치

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. Tesseract OCR 설치 (선택사항):
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# 다른 OS의 경우 Tesseract 공식 설치 가이드 참조
```

## 사용법

### 기본 사용법
```bash
python main.py video.mp4
```

### 고급 옵션
```bash
# 출력 파일명 지정
python main.py video.mp4 -o result.csv

# OCR 엔진 선택
python main.py video.mp4 --ocr-engine tesseract

# 프레임 처리 간격 조정 (60프레임마다 처리)
python main.py video.mp4 --frame-skip 60

# ROI 영역 설정 도움말
python main.py video.mp4 --setup-roi

# ROI 편집기 시작 (마우스로 ROI 수정 가능)
python main.py video.mp4 --edit-roi

```

### ROI (관심 영역) 설정

#### 방법 1: 이미지 기반 설정 (기존 방법)

1. ROI 설정 모드 실행:
```bash
python main.py video.mp4 --setup-roi
```

2. 생성된 `roi_setup.jpg` 이미지를 확인

3. `config.py` 파일에서 좌표 수정:
```python
ROI_REGION_1 = (x1, y1, width1, height1)  # 첫 번째 숫자 영역
ROI_REGION_2 = (x2, y2, width2, height2)  # 두 번째 숫자 영역
```

#### 방법 2: 대화형 ROI 편집기 (새로운 방법)
1. ROI 편집기 시작:
```bash
python main.py video.mp4 --edit-roi
```

2. 동영상 재생 창에서 마우스로 ROI 영역 드래그하여 위치 수정

3. 키보드 조작:
   - `SPACE`: 재생/일시정지
   - `R`: ROI 위치 초기화
   - `S`: 현재 ROI 설정을 config.py에 저장
   - `H`: 도움말 표시/숨기기
   - `Q`: 종료

4. 설정 완료 후 동영상 처리 실행

#### 독립 실행 모드
ROI 편집기를 독립적으로 실행하려면:
```bash
python video_roi_editor.py video.mp4
```

## 출력 형식

생성되는 CSV 파일은 다음과 같은 구조를 가집니다:

| timestamp | frame_index | number_1 | number_2 |
|-----------|-------------|----------|----------|
| 0.0       | 0           | 123      | 456      |
| 1.0       | 1           | 124      | 457      |
| 2.0       | 2           | 125      | 458      |

- `timestamp`: 동영상에서의 시간 (초)
- `frame_index`: 처리된 프레임 순서
- `number_1`: 첫 번째 ROI에서 인식된 숫자
- `number_2`: 두 번째 ROI에서 인식된 숫자

## 설정

`config.py` 파일에서 다음 설정들을 조정할 수 있습니다:

- `ROI_REGION_1`, `ROI_REGION_2`: 숫자 인식 영역
- `OCR_ENGINE`: 사용할 OCR 엔진 ("easyocr" 또는 "tesseract")
- `FRAME_SKIP`: 프레임 처리 간격
- `SAVE_DEBUG_IMAGES`: 디버그 이미지 저장 여부

## 디버그

`debug_frames/` 폴더에 처리된 프레임 이미지가 저장되어 ROI 영역과 인식 결과를 시각적으로 확인할 수 있습니다.

## 문제 해결

### OCR 정확도가 낮은 경우
1. ROI 영역을 더 정확하게 설정
2. 동영상 해상도가 낮은 경우 더 큰 ROI 영역 사용
3. Tesseract와 EasyOCR 중 더 나은 결과를 주는 엔진 선택

### 성능 최적화
- `FRAME_SKIP` 값을 높여서 처리하는 프레임 수 줄이기
- GPU가 있는 경우 EasyOCR의 GPU 옵션 활성화