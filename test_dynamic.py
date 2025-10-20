"""
테스트 스크립트: security_report_pdf_dynamic.py
S3 업로드 기능 추가
"""

from report_response_f import sample_response_data, SECTION_TITLES, SECTION_TO_MAIN_MAPPING, MAIN_SECTIONS
from security_report_pdf_dynamic import SecurityReportPDF
from s3_manager import S3Manager

print("🚀 동적 PDF 생성 및 S3 업로드 테스트 시작...")
print()

# 1. PDF 생성
output_filename = "final_dynamic_report.pdf"
pdf = SecurityReportPDF()
pdf.generate_from_json(
    json_data=sample_response_data,
    output_path=output_filename,
    section_titles=SECTION_TITLES,
    section_mapping=SECTION_TO_MAIN_MAPPING,
    main_sections=MAIN_SECTIONS
)

print()
print("=" * 60)

# 2. S3 업로드
try:
    print("📤 S3 업로드 시작...")
    s3_manager = S3Manager()
    
    # S3에 업로드 (타임스탬프 자동 추가)
    s3_url = s3_manager.upload_file(
        local_path=output_filename,
        metadata={
            'report-type': 'forensic-analysis',
            'generated-by': 'SecurityReportPDF',
            'company': sample_response_data['report'].get('summary', 'unknown')
        }
    )
    
    if s3_url:
        print(f"✅ S3 업로드 성공!")
        print(f"🌐 접근 URL: {s3_url}")
    else:
        print("❌ S3 업로드 실패")
    
    # 로컬 파일 유지 (삭제하려면 아래 주석 해제)
    # s3_manager.delete_local_file(output_filename)
    
except Exception as e:
    print(f"❌ S3 업로드 중 오류 발생: {e}")

print()
print("=" * 60)
print("✅ 테스트 완료!")
print(f"📄 로컬 파일: {output_filename}")