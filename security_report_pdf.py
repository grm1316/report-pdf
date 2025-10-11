"""
보안 진단 보고서 PDF 생성기
test.pdf와 동일한 형식의 PDF를 생성합니다.
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from dataclasses import dataclass, field
from typing import Dict, List, Any
import os
from datetime import datetime


@dataclass
class ReportData:
    """보고서에 들어갈 데이터 구조"""
    # 표지 정보
    company_name: str = "[의뢰 회사 이름]"
    pc_name: str = "[Unknown]"
    date: str = "2025년 9월 18일"
    
    # 1. 개요 섹션
    analysis_purpose: str = (
        "본 분석의 목적은 대상 PC로부터 사내 주요 기밀정보(고객정보, 사내 데이터 등)의 "
        "유출 정황을 파악하는 것입니다."
    )
    
    # PC 정보
    pc_info: Dict[str, str] = field(default_factory=lambda: {
        "PC 이름": "WORK-PC-001",
        "OS": "WINDOWS 11 Pro",
        "MAC Address": "AAA:BBB:CCC:DDD",
        "IP Address": "192.142.0.13"
    })
    
    # 분석 일정
    analysis_schedule: str = (
        "분석은 자동화 시스템을 통해 이루어졌으며, 총 30분이 소요되었습니다.\n"
        "분석 일시: 2025년 9월 18일 목요일 오후 13:00 – 13:30"
    )


class SecurityReportPDF:
    """보안 진단 보고서 PDF 생성 클래스"""
    
    def __init__(self, font_path: str = None):
        """
        Args:
            font_path: 한글 폰트 파일 경로 (None이면 맑은고딕 사용)
        """
        self.width, self.height = A4  # (595.27, 841.89) points
        self.font_name = self._setup_fonts(font_path)
        
        # 색상 정의
        self.blue = HexColor('#0066B3')  # 제목용 파란색
        self.gray = HexColor('#808080')  # 회색
        self.dark_blue = HexColor('#003D82')  # 진한 파란색
        
    def _setup_fonts(self, font_path: str = None) -> str:
        """한글 폰트 설정"""
        try:
            if font_path and os.path.exists(font_path):
                # 사용자 지정 폰트
                pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                return 'CustomFont'
            else:
                # Windows 맑은고딕 사용
                malgun_path = 'C:\\Windows\\Fonts\\malgun.ttf'
                malgun_bold_path = 'C:\\Windows\\Fonts\\malgunbd.ttf'
                
                if os.path.exists(malgun_path):
                    pdfmetrics.registerFont(TTFont('Malgun', malgun_path))
                    
                    # Bold 폰트도 등록 (있으면)
                    if os.path.exists(malgun_bold_path):
                        pdfmetrics.registerFont(TTFont('Malgun-Bold', malgun_bold_path))
                        print("✅ 맑은고딕 + Bold 폰트 로드 완료")
                    else:
                        print("⚠️ Bold 폰트 없음. 일반 폰트만 사용합니다.")
                    
                    return 'Malgun'
                else:
                    print("⚠️ 한글 폰트를 찾을 수 없습니다. Helvetica를 사용합니다.")
                    return 'Helvetica'
        except Exception as e:
            print(f"⚠️ 폰트 설정 실패: {e}. Helvetica를 사용합니다.")
            return 'Helvetica'
    
    def _draw_background(self, c: canvas.Canvas, page_num: int = 1):
        """
        배경 그리기 (점무늬 패턴 + 워터마크)
        보고서 뒷배경 이미지를 사용합니다.
        """
        # 배경 이미지 파일이 있으면 사용 (한글 파일명)
        bg_file = f'보고서 뒷배경{page_num}.png'
        if os.path.exists(bg_file):
            try:
                c.drawImage(bg_file, 0, 0, width=self.width, height=self.height, preserveAspectRatio=True, mask='auto')
                return
            except Exception as e:
                print(f"⚠️ 배경 이미지 로드 실패: {e}")
        else:
            # 배경이 없으면 흰색 + 점무늬 패턴
            c.setFillColor(HexColor('#FFFFFF'))
            c.rect(0, 0, self.width, self.height, fill=1)
            
            # 간단한 점무늬 패턴 (옵션)
            c.setFillColor(HexColor('#F0F0F0'))
            for x in range(0, int(self.width), 10):
                for y in range(0, int(self.height), 10):
                    if (x + y) % 20 == 0:
                        c.circle(x, y, 1, fill=1)
    
    def _draw_page_number(self, c: canvas.Canvas, page_num: int):
        """페이지 번호 그리기"""
        c.setFont(self.font_name, 10)
        c.setFillColor(self.gray)
        page_text = f"- {page_num} -"
        text_width = c.stringWidth(page_text, self.font_name, 10)
        c.drawString((self.width - text_width) / 2, 30, page_text)
    
    def create_page_1_cover(self, c: canvas.Canvas, data: ReportData):
        """1페이지: 표지"""
        self._draw_background(c, 1)
        
        # 상단 페이지 번호
        self._draw_page_number(c, 1)
        
        # 상단 작은 텍스트
        c.setFont(self.font_name, 10)
        c.setFillColor(self.gray)
        c.drawString(60, 810, data.company_name)
        
        # 파란색 세로 라인 (왼쪽)
        c.setStrokeColor(self.blue)
        c.setLineWidth(4)
        c.line(60, 300, 60, 600)
        
        # 메인 제목
        c.setFillColor(self.dark_blue)
        c.setFont(self.font_name, 48)
        
        # "정보 유출 진단" - 3줄로 나눔
        title_lines = ["정보 유출 진단", "보고서"]
        y_start = 550
        for i, line in enumerate(title_lines):
            c.drawString(75, y_start - (i * 70), line)
        
        # PC 이름
        c.setFont(self.font_name, 12)
        c.setFillColor(self.gray)
        c.drawString(75, 350, data.pc_name)
        
        # 날짜
        c.setFont(self.font_name, 14)
        c.setFillColor(self.blue)
        c.drawString(75, 120, data.date)
        
        # 배경 이미지에 워터마크가 포함되어 있으므로 별도로 그리지 않음
        
        c.showPage()
    
    def create_page_2_toc(self, c: canvas.Canvas):
        """2페이지: 목차"""
        self._draw_background(c, 2)
        self._draw_page_number(c, 2)
        
        # 목차 제목
        c.setFont(self.font_name, 28)
        c.setFillColor(HexColor('#000000'))
        title_text = "목차"
        title_width = c.stringWidth(title_text, self.font_name, 28)
        c.drawString((self.width - title_width) / 2, 720, title_text)
        
        # 목차 항목들
        c.setFont(self.font_name, 14)
        toc_items = [
            "1. 개요",
            "",
            "1.1 분석 목적",
            "",
            "1.2 데이터 수집",
            "",
            "1.3 분석 일정",
            "",
            "1.4 분석 방법 및 절차",
            "",
            "1.5 분석의 한계",
            "",
            "2. 분석 요약 및 상세",
            "",
            "2.1 분석 요약",
            "",
            "2.2 취득 행위",
            "",
            "2.3 유출 행위",
            "",
            "2.4 증거 인멸 행위",
            "",
            "3. 분석 결과",
            "",
            "3.1 확인된 사실",
            "",
            "3.2 종합 의견 및 재구성"
        ]
        
        y_position = 650
        for item in toc_items:
            if item:  # 빈 줄이 아닐 때만
                # 1, 2, 3으로 시작하는 항목은 볼드 (가능하면)
                if item[0].isdigit() and item[1] == '.':
                    # Bold 폰트 사용 시도, 없으면 일반 폰트
                    try:
                        c.setFont(self.font_name + '-Bold', 14)
                    except:
                        c.setFont(self.font_name, 14)  # Bold 없으면 일반 폰트
                else:
                    c.setFont(self.font_name, 12)
                
                c.drawString(100, y_position, item)
            y_position -= 20
        
        c.showPage()
    
    def create_page_3_overview(self, c: canvas.Canvas, data: ReportData):
        """3페이지: 개요 시작"""
        self._draw_background(c, 3)
        self._draw_page_number(c, 3)
        
        # 대제목
        c.setFont(self.font_name, 24)
        c.setFillColor(self.dark_blue)
        c.drawString(60, 760, "1. 개요")
        
        # 1.1 분석 목적
        c.setFont(self.font_name, 16)
        c.setFillColor(HexColor('#000000'))
        c.drawString(60, 710, "1.1 분석 목적")
        
        # 본문
        c.setFont(self.font_name, 11)
        y_position = 680
        
        # 텍스트 줄바꿈 처리
        text = data.analysis_purpose
        max_width = self.width - 120  # 좌우 여백
        
        # 간단한 줄바꿈 (실제로는 더 정교한 처리 필요)
        words = text.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if c.stringWidth(test_line, self.font_name, 11) < max_width:
                line = test_line
            else:
                c.drawString(60, y_position, line)
                y_position -= 15
                line = word + " "
        if line:
            c.drawString(60, y_position, line)
        
        # 1.2 데이터 수집
        y_position -= 40
        c.setFont(self.font_name, 16)
        c.drawString(60, y_position, "1.2 데이터 수집")
        
        y_position -= 30
        c.setFont(self.font_name, 11)
        text2 = (
            "본 분석은 퇴사 예정자인 김민재 대리의 업무용 Windows PC에 대하여 정보를 수집하였으며, "
            "행위에 따라 기록되는 주요 아티팩트 데이터를 확보하였습니다."
        )
        
        # 간단한 줄바꿈
        words = text2.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if c.stringWidth(test_line, self.font_name, 11) < max_width:
                line = test_line
            else:
                c.drawString(60, y_position, line)
                y_position -= 15
                line = word + " "
        if line:
            c.drawString(60, y_position, line)
        
        # PC 정보 테이블
        y_position -= 30
        
        # 테이블 헤더
        c.setFont(self.font_name, 10)
        c.setFillColor(HexColor('#E0E0E0'))
        c.rect(60, y_position - 20, self.width - 120, 25, fill=1)
        
        c.setFillColor(HexColor('#000000'))
        headers = ["PC 이름", "OS", "MAC Address", "IP Address"]
        col_width = (self.width - 120) / 4
        for i, header in enumerate(headers):
            c.drawString(60 + i * col_width + 5, y_position - 5, header)
        
        # 테이블 데이터
        y_position -= 25
        c.setFillColor(HexColor('#F8F8F8'))
        c.rect(60, y_position - 20, self.width - 120, 25, fill=1)
        
        c.setFillColor(HexColor('#000000'))
        values = [
            data.pc_info["PC 이름"],
            data.pc_info["OS"],
            data.pc_info["MAC Address"],
            data.pc_info["IP Address"]
        ]
        for i, value in enumerate(values):
            c.drawString(60 + i * col_width + 5, y_position - 5, value)
        
        # 1.3 분석 일정
        y_position -= 60
        c.setFont(self.font_name, 16)
        c.drawString(60, y_position, "1.3 분석 일정")
        
        y_position -= 30
        c.setFont(self.font_name, 11)
        for line in data.analysis_schedule.split('\n'):
            c.drawString(60, y_position, line)
            y_position -= 15
        
        c.showPage()
    
    def generate_report(self, output_path: str, data: ReportData = None):
        """
        보고서 생성
        
        Args:
            output_path: 출력 PDF 파일 경로
            data: 보고서 데이터 (None이면 기본값 사용)
        """
        if data is None:
            data = ReportData()
        
        print(f"📄 PDF 생성 시작: {output_path}")
        
        # Canvas 생성
        c = canvas.Canvas(output_path, pagesize=A4)
        
        # 페이지별 생성
        print("  ✅ 1페이지: 표지 생성 중...")
        self.create_page_1_cover(c, data)
        
        print("  ✅ 2페이지: 목차 생성 중...")
        self.create_page_2_toc(c)
        
        print("  ✅ 3페이지: 개요 생성 중...")
        self.create_page_3_overview(c, data)
        
        # PDF 저장
        c.save()
        print(f"✅ PDF 생성 완료: {output_path}")


def main():
    """테스트 실행"""
    # 보고서 데이터 생성
    report_data = ReportData(
        company_name="[의뢰 회사 이름]",
        pc_name="[Unknown]",
        date="2025년 9월 18일"
    )
    
    # PDF 생성
    generator = SecurityReportPDF()
    generator.generate_report("security_report_sample.pdf", report_data)


if __name__ == "__main__":
    main()
