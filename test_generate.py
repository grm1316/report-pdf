"""
PDF 생성 테스트 스크립트
"""

from security_report_pdf import SecurityReportPDF, ReportData


def main():
    print("=" * 60)
    print("보안 진단 보고서 PDF 생성 테스트")
    print("=" * 60)
    print()
    
    # 샘플 데이터 생성
    report_data = ReportData(
        company_name="[테스트 회사]",
        pc_name="[TEST-PC-001]",
        date="2025년 10월 11일"
    )
    
    # PDF 생성기 초기화
    # 한글 폰트 경로를 지정하려면: SecurityReportPDF(font_path='path/to/font.ttf')
    generator = SecurityReportPDF()
    
    # PDF 생성
    output_file = "test_security_report.pdf"
    generator.generate_report(output_file, report_data)
    
    print()
    print("=" * 60)
    print(f"✅ 테스트 완료! {output_file}를 확인하세요.")
    print("=" * 60)


if __name__ == "__main__":
    main()
