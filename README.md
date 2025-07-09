# Video ROI Editor

동영상에서 특정 영역(ROI)의 숫자를 자동으로 인식하여 CSV 파일로 추출하는 Python 프로그램입니다.

## 주요 기능

- 🎯 **대화형 ROI 설정**: 마우스 클릭으로 간편한 ROI 영역 설정
- 📊 **정확한 숫자 인식**: EasyOCR와 Tesseract OCR 엔진 지원
- ⚡ **유연한 프레임 스킵**: 커스터마이징 가능한 프레임 처리 간격
- 📏 **가변 ROI 크기**: 실시간으로 조절 가능한 ROI 영역 크기
- 💾 **설정 저장/불러오기**: JSON 파일로 ROI 설정 관리
- 🔍 **디버그 기능**: 처리 과정 시각화 및 미리보기
- 📈 **CSV 출력**: 구조화된 데이터로 결과 저장

## 설치 방법

### 1. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. Tesseract OCR 설치 (선택사항)

Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr
```

## 사용 방법

### 1. 대화형 ROI 설정

```bash
# ROI 영역 설정 모드
python video_roi_editer.py your_video.mp4 --setup
```

**조작법:**
- 좌클릭: ROI 영역 추가
- 우클릭: 마지막 ROI 영역 삭제
- 'r' 키: 모든 ROI 영역 초기화
- 's' 키: 현재 ROI 설정 저장
- '+/-' 키: ROI 크기 실시간 조절
- 'q' 키: 종료

### 2. 동영상 처리

```bash
# 기본 처리
python video_roi_editer.py your_video.mp4

# 커스텀 설정으로 처리
python video_roi_editer.py your_video.mp4 --frame-skip 60 --roi-width 150 --roi-height 60 --output results.csv
```

### 3. 프로그래밍 방식 사용

```python
from video_roi_editer import VideoROIEditor

# 인스턴스 생성
editor = VideoROIEditor("your_video.mp4")

# 대화형 ROI 설정
editor.interactive_roi_setup()

# 프레임 스킵 설정 (예: 60프레임마다 처리)
editor.set_frame_skip(60)

# ROI 크기 설정
editor.set_roi_size(200, 80)

# 동영상 처리 및 CSV 생성
df = editor.process_video("output.csv")

# 결과 확인
print(df.head())
```

## 커맨드라인 옵션

```bash
python video_roi_editer.py [동영상파일] [옵션]

옵션:
  -s, --setup          ROI 설정 모드
  -p, --preview        ROI 미리보기
  -c, --config FILE    설정 파일 지정 (기본: roi_config.json)
  -o, --output FILE    출력 CSV 파일 지정
  -f, --frame-skip N   프레임 스킵 설정
  -w, --roi-width N    ROI 너비 설정
  -h, --roi-height N   ROI 높이 설정
```

## 설정 파일 구조

ROI 설정은 JSON 파일로 저장됩니다:

```json
{
  "roi_regions": [
    [100, 50, 200, 80],
    [500, 50, 200, 80]
  ],
  "roi_size": [200, 80],
  "frame_skip": 30
}
```

## 출력 형식

CSV 파일에는 다음 컬럼이 포함됩니다:

- `timestamp`: 시간 (초)
- `frame_index`: 프레임 인덱스
- `roi_1_number`: 첫 번째 ROI 영역의 숫자
- `roi_2_number`: 두 번째 ROI 영역의 숫자
- `roi_N_number`: N번째 ROI 영역의 숫자

## 사용 예제

### 예제 1: 기본 사용법
```bash
# 1단계: ROI 설정
python video_roi_editer.py sample.mp4 --setup

# 2단계: 동영상 처리
python video_roi_editer.py sample.mp4
```

### 예제 2: 고급 설정
```bash
# 2초마다 처리, 150x60 ROI 크기, 커스텀 출력 파일
python video_roi_editer.py sample.mp4 --frame-skip 60 --roi-width 150 --roi-height 60 --output my_results.csv
```

### 예제 3: 프로그래밍 방식
```python
# 고급 사용법
editor = VideoROIEditor("sample.mp4")
editor.load_roi_config("my_config.json")
editor.set_frame_skip(30)
df = editor.process_video("results.csv")

# 결과 분석
for col in df.columns:
    if col.startswith('roi_') and col.endswith('_number'):
        success_rate = (df[col].notna().sum() / len(df)) * 100
        print(f"{col}: {success_rate:.1f}% 인식 성공률")
```

## 개선 사항

### 이전 버전 대비 새로운 기능
1. **대화형 ROI 설정**: 마우스 클릭으로 직관적인 ROI 설정
2. **동적 ROI 크기 조절**: 실시간으로 ROI 크기 변경 가능
3. **유연한 프레임 스킵**: 커맨드라인 또는 코드에서 쉽게 설정
4. **다중 ROI 지원**: 무제한 ROI 영역 추가 가능
5. **설정 관리**: JSON 파일로 설정 저장/불러오기
6. **향상된 CSV 출력**: 수치형 데이터 변환 및 통계 정보 제공

## 문제 해결

### OCR 인식률이 낮을 때
1. ROI 영역 크기와 위치를 조정하세요
2. 다른 OCR 엔진을 시도해보세요 (`config.py`에서 변경)
3. 디버그 이미지를 확인하여 전처리가 올바른지 확인하세요

### 처리 속도가 느릴 때
1. `--frame-skip` 값을 증가시키세요
2. 디버그 이미지 저장을 비활성화하세요 (`config.py`에서 `SAVE_DEBUG_IMAGES = False`)

### ROI 설정이 어려울 때
1. `--preview` 옵션으로 현재 ROI 설정을 확인하세요
2. ROI 크기를 더 크게 설정해보세요
3. 동영상의 첫 번째 프레임에서 숫자가 명확히 보이는지 확인하세요

## 라이선스

MIT License