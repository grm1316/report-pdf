# 보안 진단 보고서 PDF 생성기

test.pdf와 동일한 형식의 보안 진단 보고서를 자동으로 생성합니다.

## 📋 현재 구현 상태

✅ **완료된 부분:**
- 1페이지: 표지 (회사명, 제목, PC명, 날짜)
- 2페이지: 목차
- 3페이지: 개요 (분석 목적, 데이터 수집, PC 정보 테이블, 분석 일정)

⏳ **다음 단계:**
- 4-8페이지: 나머지 본문 내용 추가
- 배경 이미지 적용
- 워터마크 적용
- Gemini API 연동

## 🚀 빠른 시작

### 1. 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. PDF 생성 테스트

```bash
python test_generate.py
```

실행하면 `test_security_report.pdf` 파일이 생성됩니다.

## 📁 파일 구조

```
C:\Test\pdf\
├── requirements.txt              # 필요한 라이브러리
├── security_report_pdf.py        # 메인 PDF 생성기
├── test_generate.py              # 테스트 실행 스크립트
├── README.md                     # 이 파일
├── background_1.png (옵션)       # 표지 배경 이미지
├── background_2.png (옵션)       # 목차 배경 이미지
└── background_3.png (옵션)       # 본문 배경 이미지
```

## 🎨 커스터마이징

### 한글 폰트 변경

기본적으로 Windows의 맑은고딕을 사용합니다. 다른 폰트를 사용하려면:

```python
from security_report_pdf import SecurityReportPDF, ReportData

# 나눔고딕 사용 예시
generator = SecurityReportPDF(font_path='C:/Windows/Fonts/NanumGothic.ttf')
```

### 데이터 변경

```python
from security_report_pdf import ReportData

# 커스텀 데이터 생성
custom_data = ReportData(
    company_name="[우리 회사]",
    pc_name="[DEV-PC-123]",
    date="2025년 10월 15일",
    pc_info={
        "PC 이름": "DEV-PC-123",
        "OS": "WINDOWS 11 Pro",
        "MAC Address": "AA:BB:CC:DD:EE:FF",
        "IP Address": "192.168.0.100"
    }
)

# PDF 생성
generator = SecurityReportPDF()
generator.generate_report("custom_report.pdf", custom_data)
```

### 배경 이미지 추가

1. `보고서 뒷배경1.png`, `보고서 뒷배경2.png`, `보고서 뒷배경3.png` 파일을 
   `C:\Test\pdf\` 폴더에 배치 (✅ 이미 추가됨!)
2. 이미지 크기: A4 용지 크기 (595x842 픽셀 권장)
3. 자동으로 배경에 적용됩니다

## 🔧 주요 클래스 및 메서드

### `ReportData`
보고서에 들어갈 데이터를 담는 클래스

**주요 필드:**
- `company_name`: 회사명
- `pc_name`: PC 이름
- `date`: 분석 날짜
- `pc_info`: PC 정보 딕셔너리
- `analysis_purpose`: 분석 목적
- `analysis_schedule`: 분석 일정

### `SecurityReportPDF`
PDF를 생성하는 메인 클래스

**주요 메서드:**
- `create_page_1_cover()`: 표지 생성
- `create_page_2_toc()`: 목차 생성
- `create_page_3_overview()`: 개요 생성
- `generate_report()`: 전체 보고서 생성

## 📝 다음 개발 단계

### 4-8페이지 추가
```python
def create_page_4_overview_2(self, c, data):
    """4페이지: 개요 계속"""
    pass

def create_page_5_analysis_summary(self, c, data):
    """5페이지: 분석 요약"""
    pass

def create_page_6_analysis_detail_1(self, c, data):
    """6페이지: 분석 상세 1"""
    pass

def create_page_7_analysis_detail_2(self, c, data):
    """7페이지: 분석 상세 2"""
    pass

def create_page_8_conclusion(self, c, data):
    """8페이지: 결론"""
    pass
```

### Gemini API 연동
```python
# Analyzer.py의 _generate_analysis_result()에서 
# Gemini로 분석 후 ReportData 객체 생성
gemini_result = analyze_with_gemini(artifacts)
report_data = ReportData.from_gemini(gemini_result)
generator.generate_report("output.pdf", report_data)
```

## ⚠️ 주의사항

1. **폰트**: 한글이 깨지면 폰트 경로를 확인하세요
2. **이미지**: 배경 이미지가 없어도 기본 패턴으로 생성됩니다
3. **메모리**: 대량 생성 시 메모리 사용에 주의하세요

## 🐛 문제 해결

### 한글이 깨져요
```python
# 맑은고딕 경로 확인
import os
print(os.path.exists('C:\\Windows\\Fonts\\malgun.ttf'))

# 또는 다른 폰트 사용
generator = SecurityReportPDF(font_path='your_font_path.ttf')
```

### 이미지가 안 보여요
```python
# 현재 디렉토리 확인
import os
print(os.getcwd())

# 이미지 파일 존재 확인
print(os.path.exists('background_1.png'))
```

## 📞 도움말

문제가 있으면 코드의 주석을 참고하거나 질문해주세요!
