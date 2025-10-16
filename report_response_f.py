import json
from collections import defaultdict

# PDF 내용을 완벽하게 반영한 데이터
sample_response_data = {
  "report": {
    "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "title": "정보 유출 진단 보고서",
    "summary": "[의뢰 회사 이름]",
    "pc_id": "WORK-PC-001", 
    "created_at": "2025년 9월 18일",
    "created_by": "Forensic Analysis AI Agent", 
    "link": None, 
    "task_id": "test_id"
  },
  "details": [
    # --- 1. 개요 (이전과 동일) ---
    {"id": "d01", "section_type": 0, "order_no": 1, "content": "본 분석의 목적은 대상 PC로부터 사내 주요 기밀정보(고객정보, 사내 데이터 등)의 유출 정황을 파악하는 것입니다."},
    {"id": "d02", "section_type": 1, "order_no": 2, "content": """본 분석은 퇴사 예정자인 **김민재 대리**의 업무용 Windows PC에 대하여 정보를 수집하였으며, 행위에 따라 기록되는 주요 아티팩트 데이터를 확보하였습니다. 수집된 아티팩트 범위는 다음과 같습니다.\n\n| PC 이름 | OS | MAC Address | IP Address |\n|---|---|---|---|\n| WORK-PC-001 | WINDOWS 11 Pro | AAA:BBB:CCC:DDD | 192.142.0.13 |\n\n수집된 아티팩트는 브라우저 사용 내역, USB 연결 기록, 프로그램 실행 기록(프리패치), 파일 실행 및 삭제 흔적, 메신저 이용 내역 등으로, 이를 종합적으로 분석하여 사용자의 활동을 확인할 수 있습니다."""},
    {"id": "d03", "section_type": 2, "order_no": 3, "content": "분석은 자동화 시스템을 통해 이루어졌으며, 총 30분이 소요되었습니다.\n\n**분석 일시**: 2025년 9월 18일 목요일 오후 13:00-13:30"},
    {"id": "d04", "section_type": 3, "order_no": 4, "content": """본 분석은 자동화된 시스템을 통해 아래 4단계의 절차로 수행되었으며, 이를 통해 신속하고 일관된 결과를 도출하였습니다.\n\n1. **데이터 수집**: 분석 시스템이 대상 PC에 접근하여 1.2 데이터 수집에 명시된 브라우저, 외부 저장 매체, 메신저 등 각 영역의 디지털 아티팩트 원본 데이터를 일괄 수집합니다.\n2. **데이터 전처리 및 필터링**: 수집된 로그, 데이터베이스, 시스템 파일 등 비정형 데이터를 분석 가능한 정형 데이터로 변환(파싱)합니다. 이후, 분석 목적과 관련 없는 시스템의 기본 동작 기록(쓰레기 데이터)을 제거하여 사용자의 유의미한 행위 데이터만을 추출합니다.\n3. **ML 기반 분류**: 정제된 데이터를 머신러닝 모델에 입력하여 '파일 다운로드', 'USB 연결', '파일 삭제', '메신저 전송' 등 사전에 정의된 사용자 행위 유형별로 자동 분류합니다. 이 단계는 대량의 데이터 속에서 정보 유출과 관련된 핵심 행위를 신속하게 식별하는 역할을 합니다.\n4. **포렌식 분석 AI 에이전트 분석**: 분류된 행위 데이터를 기반으로, 거대 언어 모델(LLM)이 적용된 포렌식 분석 AI 에이전트가 각 행위 간의 시간적, 논리적 인과관계를 추론합니다. 에이전트는 최종적으로 데이터 간의 연관성을 종합하여 가장 가능성이 높은 사건의 시나리오를 재구성하고, 그 결과를 본 보고서와 같은 자연어 형태로 생성합니다."""},
    {"id": "d05", "section_type": 4, "order_no": 5, "content": """본 분석은 정보유출 징후가 의심되는 사용자 PC에 남아 있는 아티팩트에 국한하여 수행되었습니다.\n\n* 외부 저장매체 자체, 네트워크 기록, 서버 로그 등은 분석 범위에 포함되지 않았습니다.\n* 일부 결과는 정황 및 시간축 기반의 합리적 추정으로, 객관적 증거력이 부족할 수 있습니다.\n* 본 보고서의 내용은 법적 판단을 대신하지 않으며, 중요한 의사결정이나 법적 조치 전에는 추가 검증 및 전문기관의 재검토를 권장합니다."""},
    
    # --- 2. 분석 요약 및 상세 ---
    {"id": "d06", "section_type": 5, "order_no": 6, "content": """* **취득 행위**: 2025년 9월 15일, 구글 클라우드 서비스에 접속하여 기밀로 분류된 고객 정보 파일을 로컬 PC로 다운로드했습니다.\n* **유출 행위**: 파일 다운로드 직후, 개인 소유로 추정되는 USB 저장 장치를 연결하여 파일을 복사했으며, 유사한 시점에 카카오톡 메신저를 통해 파일을 전송한 흔적이 확인되었습니다.\n* **증거 인멸 행위**: 유출에 사용된 파일을 휴지통을 통해 삭제하고, 특정 시간대의 브라우저 접속 기록을 삭제하여 행위를 은닉하려는 시도가 있었습니다.\n\n| **구분** | **일시 (KST)** | **행위 내용** | **관련 증거** |\n|---|---|---|---|\n| **취득 행위** | 2025-09-15 14:22~23 | 구글 드라이브 접속 후 기밀 파일 다운로드 | Chrome History DB, Download Logs, LNK Files |\n| **유출 행위** | 2025-09-15 14:25 | USB 저장 장치(SanDisk Ultra Flair) 연결 후 파일 복사 가능성 | Registry (USBSTOR), setupapi.dev.log |\n| **유출 행위** | 2025-09-15 14:30 | 카카오톡 PC 버전을 통해 동일 파일 전송 정황 | KakaoTalk Cache Data |\n| **증거 인멸** | 2025-09-15 14:40~41 | 다운로드 파일 삭제 및 Chrome 기록 삭제, SDelete 실행 흔적 | \\$Recycle.Bin Metadata, MFT Entry, Chrome Cache/Session, Prefetch Files |"""},
    
    # --- 나머지 섹션 (이전과 동일) ---
    {"id": "d07", "section_type": 6, "order_no": 7, "content": """분석 대상자는 개인 구글 클라우드 계정을 통해 회사 내부 정보를 취득한 것으로 확인되었습니다.\n\n* **상세 분석 결과**:\n  * __2025년 9월 15일 14:22__, Chrome 브라우저를 통해 구글 드라이브(drive.google.com)에 접속한 기록이 확인되었습니다.\n  * 브라우저 다운로드 내역 분석 결과, 같은 날 **14:23**에 **'[대외비]_고객정보_2025_3Q.xlsx'** (크기: 15.4MB) 파일이 C:\\Users\\minjae.kim\\Downloads 경로에 저장된 사실을 확인했습니다.\n  * 바탕화면 및 최근 사용 항목의 LNK 파일 분석 결과, 해당 파일이 다운로드 직후 최소 1회 이상 실행되었음을 나타내는 흔적을 발견했습니다.\n* **관련 증거**:\n  * Chrome History DB: drive.google.com 접속 기록\n  * Chrome Download Logs: [대외비]_고객정보_2025_3Q.xlsx 다운로드 로그\n  * LNK Files: [대외비]_고객정보_2025_3Q.xlsx.lnk 파일 메타데이터"""},
    {"id": "d08", "section_type": 7, "order_no": 8, "content": """취득한 기밀 파일은 **USB 저장 장치**와 **개인 메신저**라는 두 가지 경로를 통해 외부로 유출된 정황이 식별되었습니다.\n\n* **경로 1: USB 저장 장치를 통한 유출**\n  * 레지스트리(USBSTOR) 및 시스템 로그 분석 결과, 파일 다운로드 직후인 **2025년 9월 15일 14:25**에 **'SanDisk Ultra Flair'** 모델의 USB 장치(S/N: AA0123456789BEEF)가 PC에 연결된 기록을 확인했습니다.\n  * 해당 USB는 과거에도 여러 차례 사용된 이력이 있으며, 파일 취득 시점과 저장 매체 연결 시점이 매우 인접하여 데이터 복사를 위한 목적으로 사용되었을 가능성이 높습니다.\n* **경로 2: 메신저를 통한 유출**\n  * 카카오톡 PC 버전의 아티팩트 분석 결과, **2025년 9월 15일 14:30** 경 외부 대화 상대에게 파일이 전송된 기록을 확인했습니다.\n  * 대화 내용은 암호화되어 직접적인 확인은 불가했으나, 메신저 캐시 폴더에서 유출된 파일과 동일한 이름 및 크기(15.4MB)를 가진 파일의 조각(Fragment)이 발견되었습니다. 이는 파일 전송 행위의 강력한 증거로 볼 수 있습니다.\n* **관련 증거**:\n  * Registry (USBSTOR): SanDisk Ultra Flair USB 연결 기록\n  * setupapi.dev.log: 장치 연결 이벤트 로그\n  * KakaoTalk Cache Data: [대외비]_고객정보_2025_3Q.xlsx 파일 조각 데이터"""},
    {"id": "d09", "section_type": 8, "order_no": 9, "content": """분석 대상자는 정보 유출 후 자신의 행적을 숨기기 위해 관련 디지털 증거를 삭제하려 한 것으로 보입니다.\n\n* **상세 분석 결과**:\n  * **파일 삭제**: Downloads 폴더에 있던 **'[대외비]_고객정보_2025_3Q.xlsx'** 파일은 현재 존재하지 않으며, 휴지통(\\$Recycle.Bin) 분석 결과 **2025년 9월 15일 14:40**에 해당 파일이 삭제되었음을 확인했습니다.\n  * **기록 삭제**: Chrome 브라우저의 접속 기록 중, 유출 행위가 발생한 **2025년 9월 15일 14:20~14:30** 사이의 기록이 선택적으로 삭제되었습니다.\n  * **복구 가능성**: MFT(Master File Table) 분석 결과, 삭제된 파일의 메타데이터가 시스템에 그대로 남아있어 원본 파일의 복구가 가능한 상태입니다. 또한, 브라우저 캐시 및 세션 파일에는 삭제된 기록의 일부가 잔존하여 구글 드라이브 접속 사실을 재확인할 수 있었습니다.\n  * Prefetch 분석 결과, 보안 삭제 프로그램인 SDelete64.exe 가 **14:41**에 실행된 흔적이 발견되어, 단순 삭제를 넘어 영구 삭제를 시도했을 가능성도 존재합니다.\n* **관련 증거**:\n  * \\$Recycle.Bin Metadata: 파일 삭제 시간 및 원본 경로 정보\n  * MFT Entry: 삭제된 파일의 메타데이터\n  * Chrome Cache/Session Files: 삭제된 시간대의 웹 접속 흔적\n  * Prefetch Files: SDelete64.exe.pf 실행 기록"""},
    {"id": "d10", "section_type": 9, "order_no": 10, "content": """본 분석을 통해 객관적인 디지털 증거로 확인된 사실은 다음과 같습니다.\n\n* **(사실 1)** 2025년 9월 15일 14시 23분, 분석 대상 PC에서 구글 드라이브를 통해 **'[대외비]_고객정보_2025_3Q.xlsx'** (15.4MB) 파일이 다운로드되었습니다.\n* **(사실 2)** 파일 다운로드 2분 후인 14시 25분, 외부 저장 장치 **'SanDisk Ultra Flair'** 모델이 PC에 연결되었습니다.\n* **(사실 3)** 14시 30분경, 카카오톡 메신저를 통해 상기 파일과 동일한 크기와 이름의 파일이 전송된 흔적이 발견되었습니다.\n* **(사실 4)** 14시 40분, 다운로드되었던 원본 파일이 삭제되었으며, 관련 시간대의 웹 브라우저 접속 기록 또한 삭제되었습니다.\n* **(사실 5)** 14시 41분, 데이터 영구 삭제 유틸리티(SDelete64.exe)가 실행된 기록이 확인되었습니다."""},
    {"id": "d11", "section_type": 10, "order_no": 11, "content": """확인된 디지털 증거를 시간순으로 재구성하면, 정보 유출로 볼 수 있는 일련의 행위가 다음과 같이 식별됩니다.\n\n2025년 9월 15일, 먼저 특정 기밀 파일이 PC로 다운로드되었습니다(사실 1). 그 직후, 외부 저장 매체 연결(사실 2)과 메신저를 통한 파일 전송 흔적(사실 3)이라는 두 가지 잠재적 데이터 유출 경로가 동시에 확인되었습니다. 자료 취득부터 외부 장치 연결, 메신저 사용까지의 행위가 수 분 이내에 집중적으로 발생했다는 점은 각 행위 간의 연관성이 높음을 시사합니다.\n\n이후, 선행된 작업의 흔적을 제거하기 위한 행위가 이어졌습니다. 다운로드된 원본 파일과 관련 웹 접속 기록이 삭제되었고(사실 4), 일반적인 삭제가 아닌 데이터 영구 삭제 전문 도구가 사용된 사실(사실 5)이 확인되었습니다. 이는 단순히 데이터를 정리하는 목적을 넘어, 디지털 증거의 복구를 의도적으로 어렵게 만들려는 시도로 해석될 수 있습니다.\n\n**결론적으로, 이러한 일련의 행위는 우발적인 실수가 아닌 명확한 의도를 가진 계획된 정보 유출 행위로 판단됩니다.**"""}
  ]
}

# PDF 목차에 맞춘 섹션 제목
SECTION_TITLES = {0: "분석 목적", 1: "데이터 수집", 2: "분석 일정", 3: "분석 방법 및 절차", 4: "분석의 한계", 5: "분석 요약", 6: "취득 행위", 7: "유출 행위", 8: "증거 인멸 행위", 9: "확인된 사실", 10: "종합 의견 및 재구성"}

# 대분류 구조 정의
MAIN_SECTIONS = {1: "개요", 2: "분석 요약 및 상세", 3: "분석 결과"}

# 새로운 섹션 제목에 맞춘 대분류 매핑
SECTION_TO_MAIN_MAPPING = {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 2, 9: 3, 10: 3}

def generate_hierarchical_report(data: dict) -> str:
    report_meta = data.get("report", {})
    details = data.get("details", [])
    report_lines = []
    report_lines.append(f"# {report_meta.get('title', '제목 없음')}")
    report_lines.append(f"> {report_meta.get('summary', '요약 없음')}")
    report_lines.append(f"\n**{report_meta.get('created_at', '')}**")
    report_lines.append("\n---")
    grouped_details = defaultdict(list)
    sorted_details = sorted(details, key=lambda d: d.get('order_no', 0))
    for detail in sorted_details:
        main_section_num = SECTION_TO_MAIN_MAPPING.get(detail['section_type'])
        if main_section_num:
            grouped_details[main_section_num].append(detail)
    for main_num in sorted(MAIN_SECTIONS.keys()):
        report_lines.append(f"\n# {main_num}. {MAIN_SECTIONS[main_num]}")
        sub_section_counter = 1
        for detail in grouped_details[main_num]:
            section_type = detail.get("section_type")
            section_title = SECTION_TITLES.get(section_type, "기타")
            content = detail.get("content", "내용 없음")
            report_lines.append(f"\n## {main_num}.{sub_section_counter} {section_title}")
            report_lines.append(content)
            sub_section_counter += 1
    return "\n".join(report_lines)

# --- 실행 ---
if __name__ == "__main__":
    markdown_report = generate_hierarchical_report(sample_response_data)
    file_name = "final_report_with_table.md"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(markdown_report)
    print(f"✅ 표가 추가된 최종 보고서 '{file_name}' 파일이 성공적으로 생성되었습니다.")