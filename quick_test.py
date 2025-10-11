"""
빠른 테스트용 스크립트 - 수정 후 바로 확인
"""

from security_report_pdf import SecurityReportPDF, ReportData

# 데이터 생성
report_data = ReportData(
    company_name="[의뢰 회사 이름]",
    pc_name="[Unknown]",
    date="2025년 9월 18일"
)

# PDF 생성
print("🔄 PDF 재생성 중...")
generator = SecurityReportPDF()
generator.generate_report("test_security_report.pdf", report_data)
print("✅ 완료! test_security_report.pdf를 확인하세요.")
