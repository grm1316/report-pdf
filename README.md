# 보안 진단 보고서 PDF 생성기 (security_report_pdf_dynamic.py 사용 안내)

security_report_pdf_dynamic.py 를 사용해 test.pdf 형태의 보고서를 생성하는 방법과 입력 형식을 정리합니다.
이 파일은 기존 security_report_pdf.py의 디자인 규칙(폰트·간격·표 처리)을 반영하고, 마크다운 파싱·표 페이징·목차 2패스 렌더링을 지원합니다.

## 빠른 실행 (권장)
1. 터미널 열기 (VS Code 통합 터미널)
2. 작업 디렉터리 이동
```bash
cd /d g:\pdf
```
3. 의존성 설치
```bash
pip install reportlab markdown
```
4. 테스트 스크립트(예: test_dynamic.py) 실행
```bash
python test_dynamic.py
```
- test_dynamic.py 예제는 security_report_pdf_dynamic.py 의 generate_from_json() 를 호출해 PDF를 생성합니다.
- 생성되는 PDF 파일명을 터미널 출력에서 확인하세요.

## 입력 JSON 형식 (generate_from_json에 전달)
security_report_pdf_dynamic.py 의 generate_from_json(json_data, output_path, section_titles, section_mapping, main_sections)
에 넘길 json_data 예시:

```json
{
  "report": {
    "id": "a1b2c3",
    "title": "정보 유출 진단 보고서",
    "summary": "[의뢰 회사 이름]",
    "pc_id": "WORK-PC-001",
    "created_at": "2025년 9월 18일"
  },
  "details": [
    {"id":"d01","section_type":0,"order_no":1,"content":"분석 목적 내용..."},
    {"id":"d02","section_type":1,"order_no":2,"content":"데이터 수집 내용 (마크다운, 표 포함)"},
    {"id":"d06","section_type":5,"order_no":6,"content":"분석 요약 및 상세..."}
  ]
}
```

- section_type: 세부 항목의 타입(숫자 키) — section_titles 맵의 키로 사용됩니다.
- order_no: 문서 내 순서 정렬용.
- content: 마크다운 형식(표, 코드블록, 굵게 등) 사용 가능.

## section_titles / section_mapping / main_sections 예시
generate_from_json 호출 시 아래와 같은 매핑을 전달하세요:

```python
section_titles = {
    0: "분석 목적",
    1: "데이터 수집",
    2: "분석 일정",
    3: "분석 방법",
    4: "분석의 한계",
    5: "분석 요약",
    6: "취득 행위",
    7: "유출 행위",
    8: "증거 인멸 행위",
    9: "확인된 사실",
    10: "종합 의견 및 재구성"
}

# section_type -> main section 매핑 (예: 0~4 -> 1, 5~8 -> 2, 9~10 -> 3)
section_mapping = {i: (1 if i<=4 else 2 if i<=8 else 3) for i in range(0, 11)}

# 대분류 제목
main_sections = {
    1: "개요",
    2: "분석 요약 및 상세",
    3: "분석 결과"
}
```

## test_dynamic.py 예제 (간단)
프로젝트 루트에 다음과 같은 테스트 스크립트를 만들면 바로 확인 가능합니다:

```python
# filepath: g:\pdf\test_dynamic.py
from security_report_pdf_dynamic import SecurityReportPDF
import json

with open("sample_input.json", "r", encoding="utf-8") as f:
    data = json.load(f)

pdf = SecurityReportPDF()
pdf.generate_from_json(data, "output_dynamic.pdf", section_titles, section_mapping, main_sections)
print("output_dynamic.pdf 생성 완료")
```

## 주의사항 / 디버깅
- 한글 폰트: Windows에서 맑은고딕(malgun.ttf) 사용. 폰트가 없으면 Helvetica 대체.
- 배경 이미지: repository 루트의 001.png / 002.png 사용 (없으면 건너뜀).
- 목차 동기화: 코드가 두 패스로 동작하므로 generate_from_json을 호출하면 목차가 표지 다음(2페이지)에 정확히 들어갑니다.
- 만약 PDF가 중간에 멈추거나 SyntaxError가 발생하면 security_report_pdf_dynamic.py 파일이 중간에 잘려있지 않은지(끝까지 저장되었는지) 확인하세요.



