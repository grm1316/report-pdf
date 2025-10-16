"""
테스트 스크립트: security_report_pdf_dynamic.py
"""

from report_response_f import sample_response_data, SECTION_TITLES, SECTION_TO_MAIN_MAPPING, MAIN_SECTIONS
from security_report_pdf_dynamic import SecurityReportPDF

print("🚀 동적 PDF 생성 테스트 시작...")
print()

pdf = SecurityReportPDF()
pdf.generate_from_json(
    json_data=sample_response_data,
    output_path="final_dynamic_report.pdf",
    section_titles=SECTION_TITLES,
    section_mapping=SECTION_TO_MAIN_MAPPING,
    main_sections=MAIN_SECTIONS
)

print()
print("✅ 테스트 완료!")
print("📄 final_dynamic_report.pdf를 확인하세요.")
