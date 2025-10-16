"""
보안 진단 보고서 PDF 생성기 - 들여쓰기 최적화 버전
본문 작성 공간을 최대화하도록 레이아웃 개선
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from dataclasses import dataclass
from typing import List, Dict
import os


@dataclass
class ReportData:
    """보고서 데이터"""
    company_name: str = "[의뢰 회사 이름]"
    pc_name: str = "[TEST-PC-001]"
    date: str = "2025년 10월 13일"


class SecurityReportPDF:
    """보안 진단 보고서 PDF - 들여쓰기 최적화 버전"""
    
    def __init__(self):
        self.width, self.height = A4
        self.font = self._setup_fonts()
        
        # 여백
        self.left = 25
        self.top = 780
        self.min_y = 100
        
        # 상태 관리
        self.canvas = None
        self.current_y = self.top
        self.current_page = 1
        
        # 색상
        self.blue = HexColor('#0066B3')
        self.gray = HexColor('#808080')
        self.black = HexColor('#000000')
        self.light_gray = HexColor('#E0E0E0')
        self.very_light_gray = HexColor('#F8F8F8')
        
        # ========================================
        # 들여쓰기 레벨 최적화 (본문 공간 확보)
        # ========================================
        self.L0 = self.left           # 대제목 (1. 개요) = 25
        self.L1 = self.left           # 소제목 (1.1) = 25 (같은 라인!)
        self.L2 = self.left + 10      # 본문, 표 = 35 (최소 들여쓰기)
        self.L3 = self.left + 20      # 번호 리스트 제목 = 45
        self.L4 = self.left + 35      # 번호 리스트 내용 = 60
        
        # 배경
        d = os.path.dirname(os.path.abspath(__file__))
        self.bg1 = os.path.join(d, '보고서 뒷배경1.png')
        self.bg2 = os.path.join(d, '보고서 뒷배경2.png')
        self.bg3 = os.path.join(d, '보고서 뒷배경3.png')
        
        print(f"✅ 폰트: {self.font}")
        print(f"✅ BG1: {os.path.exists(self.bg1)}")
        print(f"✅ BG2: {os.path.exists(self.bg2)}")
        print(f"✅ BG3: {os.path.exists(self.bg3)}")
    
    def _setup_fonts(self):
        """폰트 설정"""
        try:
            m = 'C:\\Windows\\Fonts\\malgun.ttf'
            mb = 'C:\\Windows\\Fonts\\malgunbd.ttf'
            if os.path.exists(m):
                pdfmetrics.registerFont(TTFont('Malgun', m))
                if os.path.exists(mb):
                    pdfmetrics.registerFont(TTFont('MalgunBold', mb))
                return 'Malgun'
        except:
            pass
        return 'Helvetica'
    
    def _bg(self, c, p):
        """배경 이미지"""
        bg = [self.bg1, self.bg2, self.bg3][min(p-1, 2)]
        if os.path.exists(bg):
            try:
                c.drawImage(bg, 0, 0, 
                           width=self.width, 
                           height=self.height,
                           preserveAspectRatio=False)
            except Exception as e:
                print(f"배경 이미지 로드 실패: {e}")
    
    def _pgn(self, c, n):
        """페이지 번호"""
        c.setFont(self.font, 10)
        c.setFillColor(self.gray)
        t = f"- {n} -"
        w = c.stringWidth(t, self.font, 10)
        c.drawString((self.width - w) / 2, 30, t)
    
    def _wrap_text(self, text, max_width, font_size):
        """텍스트 자동 줄바꿈 (개선 버전)"""
        if not text or not text.strip():
            return []
        
        # 최소 max_width 보장
        safe_max_width = max(max_width, 80)
        
        words = text.split()
        lines = []
        line = ""
        
        for w in words:
            test = line + " " + w if line else w
            # 10px 여유 추가
            actual_width = self.canvas.stringWidth(test, self.font, font_size)
            
            if actual_width <= (safe_max_width - 10):
                line = test
            else:
                if line:
                    lines.append(line)
                
                # 단어가 너무 긴 경우 강제 분할
                word_width = self.canvas.stringWidth(w, self.font, font_size)
                if word_width > (safe_max_width - 10):
                    chars = list(w)
                    temp = ""
                    for char in chars:
                        test_char = temp + char
                        if self.canvas.stringWidth(test_char, self.font, font_size) <= (safe_max_width - 10):
                            temp += char
                        else:
                            if temp:
                                lines.append(temp)
                            temp = char
                    line = temp
                else:
                    line = w
        
        if line:
            lines.append(line)
        
        return lines
    
    # ===================================================================
    # 페이지 관리
    # ===================================================================
    
    def check_space(self, needed_height):
        """공간 확인 및 페이지 넘김"""
        if self.current_y - needed_height - 20 < self.min_y:
            self.new_page()
            return True
        return False
    
    def new_page(self):
        """새 페이지 생성"""
        self.canvas.showPage()
        self.current_page += 1
        self._bg(self.canvas, min(self.current_page, 3))
        self._pgn(self.canvas, self.current_page)
        
        self.canvas.saveState()
        self.canvas.setFillColorRGB(0, 0, 0)
        self.canvas.setStrokeColorRGB(0, 0, 0)
        
        self.current_y = self.top
    
    def add_spacing(self, height):
        """수동 여백"""
        self.current_y -= height
    
    # ===================================================================
    # 기본 컴포넌트
    # ===================================================================
    
    def draw_text(self, x, y, text, font_size, color=None):
        """텍스트 그리기"""
        if color:
            self.canvas.setFillColor(color)
        else:
            self.canvas.setFillColor(self.black)
        self.canvas.setFont(self.font, font_size)
        self.canvas.drawString(x, y, text)
    
    def draw_paragraph(self, x, text, font_size, max_width, line_spacing=17):
        """문단 그리기"""
        self.canvas.setFont(self.font, font_size)
        self.canvas.setFillColor(self.black)
        
        safe_max_width = max(max_width, 100)
        lines = self._wrap_text(text, safe_max_width, font_size)
        
        for line in lines:
            self.check_space(line_spacing + 10)
            self.canvas.drawString(x, self.current_y, line)
            self.current_y -= line_spacing
    
    def draw_bullet_list(self, items, indent, font_size=12, line_spacing=16):
        """불릿 리스트"""
        self.canvas.setFont(self.font, font_size)
        self.canvas.setFillColor(self.black)
        
        max_w = self.width - indent - 40
        for item in items:
            lines = self._wrap_text(item, max_w, font_size)
            self.check_space(len(lines) * line_spacing + 5)
            
            self.canvas.drawString(indent, self.current_y, "•")
            
            for line in lines:
                self.canvas.drawString(indent + 15, self.current_y, line)
                self.current_y -= line_spacing
            self.current_y -= 5
    
    def draw_table(self, headers, rows, col_widths, x, row_height=25):
        """표 그리기"""
        total_height = row_height
        for row in rows:
            max_lines = max(str(cell).count('\n') + 1 for cell in row)
            total_height += max(row_height, max_lines * 15)
        
        self.check_space(total_height + 30)
        
        # 헤더
        self.canvas.setFont(self.font, 10)
        self.canvas.setFillColor(self.light_gray)
        self.canvas.rect(x, self.current_y - row_height, sum(col_widths), row_height, fill=1)
        self.canvas.setFillColor(self.black)
        
        for i, h in enumerate(headers):
            self.canvas.drawString(x + sum(col_widths[:i]) + 5, self.current_y - 15, h)
        self.current_y -= row_height
        
        # 데이터
        for row in rows:
            max_lines = max(str(cell).count('\n') + 1 for cell in row)
            actual_height = max(row_height, max_lines * 15)
            
            self.canvas.setFillColor(self.very_light_gray)
            self.canvas.rect(x, self.current_y - actual_height, sum(col_widths), actual_height, fill=1)
            self.canvas.setFillColor(self.black)
            
            for i, cell in enumerate(row):
                cell_text = str(cell)
                lines = cell_text.split('\n')
                cell_y = self.current_y - 12
                
                for line in lines:
                    if self.canvas.stringWidth(line, self.font, 10) > col_widths[i] - 10:
                        wrapped = []
                        words = line.split()
                        current_line = ""
                        for word in words:
                            test = current_line + " " + word if current_line else word
                            if self.canvas.stringWidth(test, self.font, 9) <= col_widths[i] - 10:
                                current_line = test
                            else:
                                if current_line:
                                    wrapped.append(current_line)
                                current_line = word
                        if current_line:
                            wrapped.append(current_line)
                        
                        for wrap_line in wrapped:
                            self.canvas.setFont(self.font, 9)
                            self.canvas.drawString(x + sum(col_widths[:i]) + 5, cell_y, wrap_line)
                            cell_y -= 12
                    else:
                        self.canvas.setFont(self.font, 10)
                        self.canvas.drawString(x + sum(col_widths[:i]) + 5, cell_y, line)
                        cell_y -= 13
            
            self.current_y -= actual_height
    
    # ===================================================================
    # 페이지별 생성
    # ===================================================================
    
    def page1(self, c, data):
        """1페이지: 표지"""
        self._bg(c, 1)
        self._pgn(c, 1)

        c.setStrokeColor(self.blue)
        c.setLineWidth(3)
        c.line(50, 480, 50, 700)

        c.setFont(self.font, 9)
        c.setFillColor(self.gray)
        c.drawString(60, 680, data.company_name)

        try:
            c.setFont('MalgunBold', 44)
        except:
            c.setFont(self.font, 44)
        c.setFillColor(self.blue)
        c.drawString(60, 600, "정보 유출 진단")
        c.drawString(60, 540, "보고서")

        c.setFont(self.font, 11)
        c.setFillColor(self.gray)
        c.drawString(60, 500, "[Unknown]")

        c.setFont(self.font, 14)
        c.setFillColor(self.blue)
        c.drawString(60, 120, data.date)

        c.showPage()
    
    def page2(self, c):
        """2페이지: 목차"""
        self._bg(c, 2)
        self._pgn(c, 2)
        
        try:
            c.setFont('MalgunBold', 28)
        except:
            c.setFont(self.font, 28)
        c.setFillColor(self.black)
        title_text = "목차"
        registered_fonts = pdfmetrics.getRegisteredFontNames()
        font_name = 'MalgunBold' if 'MalgunBold' in registered_fonts else self.font
        text_width = c.stringWidth(title_text, font_name, 28)
        c.drawString((self.width - text_width) / 2, 750, title_text)
        
        y = 680
        
        try:
            c.setFont('MalgunBold', 19)
        except:
            c.setFont(self.font, 19)
        c.drawString(50, y, "1. 개요")
        y -= 35
        
        c.setFont(self.font, 16)
        c.drawString(70, y, "1.1 분석 목적")
        y -= 35
        c.drawString(70, y, "1.2 데이터 수집")
        y -= 35
        c.drawString(70, y, "1.3 분석 일정")
        y -= 35
        c.drawString(70, y, "1.4 분석 방법 및 절차")
        y -= 35
        c.drawString(70, y, "1.5 분석의 한계")
        y -= 40
        
        try:
            c.setFont('MalgunBold', 19)
        except:
            c.setFont(self.font, 19)
        c.drawString(50, y, "2. 분석 요약 및 상세")
        y -= 35
        
        c.setFont(self.font, 16)
        c.drawString(70, y, "2.1 분석 요약")
        y -= 35
        c.drawString(70, y, "2.2 취득 행위")
        y -= 35
        c.drawString(70, y, "2.3 유출 행위")
        y -= 35
        c.drawString(70, y, "2.4 증거 인멸 행위")
        y -= 40
        
        try:
            c.setFont('MalgunBold', 19)
        except:
            c.setFont(self.font, 19)
        c.drawString(50, y, "3. 분석 결과")
        y -= 35
        
        c.setFont(self.font, 16)
        c.drawString(70, y, "3.1 확인된 사실")
        y -= 35
        c.drawString(70, y, "3.2 종합 의견 및 재구성")
        
        c.showPage()
    
    # ===================================================================
    # 섹션별 메서드
    # ===================================================================
    
    def section1_overview(self, data):
        """섹션 1: 개요"""
        # 본문 max_width 계산 (L2 기준, 오른쪽 여백 30)
        max_w = self.width - self.L2 - 30
        
        # 1. 개요
        self.check_space(30)
        try:
            self.canvas.setFont('MalgunBold', 19)
        except:
            self.canvas.setFont(self.font, 19)
        self.canvas.setFillColor(self.black)
        self.canvas.drawString(self.L0, self.current_y, "1. 개요")
        self.current_y -= 35
        
        # 1.1 분석 목적
        self.check_space(25)
        try:
            self.canvas.setFont('MalgunBold', 16)
        except:
            self.canvas.setFont(self.font, 16)
        self.canvas.drawString(self.L1, self.current_y, "1.1 분석 목적")
        self.current_y -= 28
        
        text = "본 분석의 목적은 대상 PC로부터 사내 주요 기밀정보(고객정보, 사내 데이터 등)의 유출 정황을 파악하는 것입니다."
        self.draw_paragraph(self.L2, text, 13, max_w)
        self.current_y -= 20
        
        # 1.2 데이터 수집
        self.check_space(25)
        try:
            self.canvas.setFont('MalgunBold', 16)
        except:
            self.canvas.setFont(self.font, 16)
        self.canvas.drawString(self.L1, self.current_y, "1.2 데이터 수집")
        self.current_y -= 28
        
        text = "본 분석은 퇴사 예정자인 김민재 대리의 업무용 Windows PC에 대하여 정보를 수집하였으며, 행위에 따라 기록되는 주요 아티팩트 데이터를 확보하였습니다."
        self.draw_paragraph(self.L2, text, 13, max_w)
        self.current_y -= 15
        
        # 표
        headers = ["PC 이름", "OS", "MAC Address", "IP Address"]
        rows = [["WORK-PC-001", "WINDOWS 11 Pro", "AAA:BBB:CCC:DDD", "192.142.0.13"]]
        col_widths = [100, 130, 130, 125]
        self.draw_table(headers, rows, col_widths, self.L2)
        self.current_y -= 15
        
        text = "수집된 아티팩트는 브라우저 사용 내역, USB 연결 기록, 프로그램 실행 기록(프리패치), 파일 실행 및 삭제 흔적, 메신저 이용 내역 등으로, 이를 종합적으로 분석하여 사용자의 행동을 확인할 수 있습니다."
        self.draw_paragraph(self.L2, text, 13, max_w)
        self.current_y -= 20
        
        # 1.3 분석 일정
        self.check_space(25)
        try:
            self.canvas.setFont('MalgunBold', 16)
        except:
            self.canvas.setFont(self.font, 16)
        self.canvas.drawString(self.L1, self.current_y, "1.3 분석 일정")
        self.current_y -= 28
        
        text = "분석은 자동화 시스템을 통해 이루어졌으며, 총 30분이 소모되었습니다."
        self.draw_paragraph(self.L2, text, 13, max_w)
        
        text = "분석 일시: 2025년 9월 18일 목요일 오후 13:00 – 13:30"
        self.draw_paragraph(self.L2, text, 13, max_w)
        self.current_y -= 20
        
        # 1.4 분석 방법 및 절차
        self.check_space(25)
        try:
            self.canvas.setFont('MalgunBold', 16)
        except:
            self.canvas.setFont(self.font, 16)
        self.canvas.drawString(self.L1, self.current_y, "1.4 분석 방법 및 절차")
        self.current_y -= 28
        
        text = "본 분석은 자동화된 시스템을 통해 아래 4단계의 절차로 수행되었으며, 이를 통해 신속하고 일관된 결과를 도출하였습니다."
        self.draw_paragraph(self.L2, text, 13, max_w)
        self.current_y -= 18
        
        # 번호 리스트
        methods = [
            ("1) 데이터 수집", ["분석 시스템이 대상 PC에 접근하여 1.2 데이터 수집에 명시된 브라우저, 외부 저장 매체, 메신저 등 각 영역의 디지털 아티팩트 원본 데이터를 수집합니다."]),
            ("2) 데이터 전처리 및 필터링", ["수집된 로그, 데이터베이스, 시스템 파일 등 비정형 데이터를 분석 가능한 정형 데이터로 변환(파싱)합니다.", "이후, 분석 목적과 관련 없는 시스템의 기본 동작 기록(쓰레기 데이터)를 제거하여 사용자의 유의미한 행위 데이터만을 추출합니다."]),
            ("3) ML 기반 분류", ["정제된 데이터를 머신러닝 모델에 입력하여 '파일 다운로드', 'USB 연결', '파일 삭제', '메신저 전송' 등 사전에 정의된 사용자 행위를 추출합니다.", "이 단계는 대량의 데이터 속에서 정보 유출과 관련된 핵심 행위들 신속하게 식별하는 역할을 합니다."]),
            ("4) 포렌식 분석 AI 에이전트 분석", ["분류된 행위 데이터를 기반으로, 거대 언어 모델(LLM)이 적용된 포렌식 분석 AI 에이전트가 각 행위 간의 시간적, 논리적 인과관계를 추론합니다.", "에이전트는 취득→유출→증거인멸의 연관성을 종합하여 가장 가능성이 높은 사건의 시나리오를 제공하며, 그 결과를 본 보고서의 자연어 텍스트로 생성합니다."])
        ]
        
        # 번호 리스트 내용 max_width (L4 기준)
        max_w4 = self.width - self.L4 - 30
        
        for title, contents in methods:
            self.check_space(30)
            self.canvas.setFont(self.font, 14)
            self.canvas.drawString(self.L3, self.current_y, title)
            self.current_y -= 20
            
            self.canvas.setFont(self.font, 12)
            for content in contents:
                self.draw_paragraph(self.L4, content, 12, max_w4, line_spacing=16)
                self.current_y -= 5
            self.current_y -= 10
        
        # 1.5 분석의 한계
        self.check_space(30)
        try:
            self.canvas.setFont('MalgunBold', 16)
        except:
            self.canvas.setFont(self.font, 16)
        self.canvas.drawString(self.L1, self.current_y, "1.5 분석의 한계")
        self.current_y -= 28
        
        text = "본 분석은 정보를 유출한 사용자 PC에 남아 있는 아티팩트에 국한하여 수행되었습니다."
        self.draw_paragraph(self.L2, text, 13, max_w)
        self.current_y -= 18
        
        limits = [
            "외부 저장매체 자체, 네트워크 기록, 서버 로그 등은 분석 범위에 포함되지 않습니다.",
            "일부 결과는 정량 및 시간차 기반의 논리적 추정으로, 객관적 증거력이 부족할 수 있습니다.",
            "본 보고서의 내용은 법적 판단을 대신하지 않으며, 중요한 의사결정이나 법적 조치 전에는 추가 검증 및 전문가의 재검토를 권장합니다."
        ]
        self.draw_bullet_list(limits, self.L4)
    
    def section2_analysis_detail(self, data):
        """섹션 2: 분석 요약 및 상세"""
        max_w = self.width - self.L2 - 30
        
        self.new_page()
        
        # 2. 분석 요약 및 상세
        self.check_space(30)
        try:
            self.canvas.setFont('MalgunBold', 19)
        except:
            self.canvas.setFont(self.font, 19)
        self.canvas.setFillColor(self.black)
        self.canvas.drawString(self.L0, self.current_y, "2. 분석 요약 및 상세")
        self.current_y -= 35
        
        # 2.1 분석 요약
        self.check_space(25)
        try:
            self.canvas.setFont('MalgunBold', 16)
        except:
            self.canvas.setFont(self.font, 16)
        self.canvas.drawString(self.L1, self.current_y, "2.1 분석 요약")
        self.current_y -= 28
        
        summary = [
            "취득 행위: 2025년 9월 15일, 구글 클라우드 서비스에 접속하여 기밀로 분류된 고객 정보 파일을 로컬 PC로 다운로드하였습니다.",
            "유출 행위: 비슷한 시각, 직후, 개인 메신저 및 USB 저장 장치를 연결하여 파일을 옮겼으며, 유사한 사전이 카카오톡 메신저에 첨부 전송된 흔적을 확인하였습니다."
        ]
        self.draw_bullet_list(summary, self.L4)
        self.current_y -= 10
        
        # 표
        headers = ["구분", "일시 (KST)", "행위 내용", "관련 증거"]
        rows = [
            ["취득 행위", "2025-09-15\n14:22~23", "구글 드라이브 접속 후 기밀 파일 다운로드", "Chrome History DB, Download Logs, LNK Files"],
            ["유출 행위", "2025-09-15\n14:25", "USB 저장 장치(SanDisk Ultra Flair) 연결 후 파일 복사 가능성", "Registry (USBSTOR), setupapi.dev.log"],
            ["유출 행위", "2025-09-15\n14:30", "카카오톡 PC 버전을 통해 동일 파일 전송 정황", "KakaoTalk Cache Data"],
            ["증거 인멸", "2025-09-15\n14:40~41", "다운로드 파일 삭제 및 Chrome 관련 세션, 로그 삭제 흔적", "$Recycle.Bin Metadata, MFT Entry, Chrome Cache/Session, Prefetch Files"]
        ]
        col_widths = [55, 80, 155, 195]
        self.draw_table(headers, rows, col_widths, self.L2, row_height=45)
        self.current_y -= 35
        
        # 2.2 취득 행위
        self.check_space(25)
        try:
            self.canvas.setFont('MalgunBold', 16)
        except:
            self.canvas.setFont(self.font, 16)
        self.canvas.drawString(self.L1, self.current_y, "2.2 취득 행위")
        self.current_y -= 28
        
        text = "분석 대상자는 개인 구글 클라우드 계정을 통해 회사 내부 정보를 취득한 것으로 확인되었습니다."
        self.draw_paragraph(self.L2, text, 13, max_w)
        self.current_y -= 18
        
        # 상세 분석
        self.canvas.setFont(self.font, 13)
        self.canvas.setFillColor(self.black)
        self.canvas.drawString(self.L4, self.current_y, "상세 분석 결과:")
        self.current_y -= 20
        
        details = [
            "2025년 9월 15일 14:22, Chrome 브라우저를 통해 구글 드라이브(drive.google.com)에 접속한 기록이 확인되었습니다.",
            "브라우저 다운로드 내역 분석 결과, 같은 날 14:23에 '[대외비]_고객정보_2025_3Q.xlsx'(15.4MB) 파일이 C:\\Users\\MinJae\\Downloads\\에 저장된 사실을 확인하였습니다.",
            "바탕화면 및 최근 사용 항목의 LNK 파일 분석 결과, 해당 파일이 다운로드 직후 최소 1회 이상 실행되었음을 나타냅니다."
        ]
        
        # 상세 분석 내용 max_width (○ 다음 텍스트 위치 고려)
        detail_max_w = self.width - (self.L4 + 35) - 40
        
        for detail in details:
            lines = self._wrap_text(detail, detail_max_w, 11)
            needed = len(lines) * 16 + 5
            self.check_space(needed)
            self.canvas.drawString(self.L4 + 18, self.current_y, "○")
            # Use draw_paragraph to handle wrapping and page breaks reliably
            self.draw_paragraph(self.L4 + 35, detail, 11, detail_max_w, line_spacing=16)
            self.current_y -= 5
        
        self.current_y -= 10
        
        # 관련 증거
        evidence = [
            "Chrome History DB: drive.google.com 접속 기록",
            "Chrome Download Logs: [대외비]_고객정보_2025_3Q.xlsx 파일 다운로드 로그",
            "LNK Files: [대외비]_고객정보_2025_3Q.xlsx 파일 메타데이터"
        ]
        evidence_height = 20 + len(evidence) * 18
        self.check_space(evidence_height)
        
        self.canvas.setFont(self.font, 13)
        self.canvas.drawString(self.L4, self.current_y, "관련 증거:")
        self.current_y -= 22
        
        self.canvas.setFont(self.font, 12)
        for ev in evidence:
            self.canvas.drawString(self.L4 + 18, self.current_y, "○")
            self.canvas.drawString(self.L4 + 35, self.current_y, ev)
            self.current_y -= 18
        
        self.current_y -= 20
        
        # 2.3 유출 행위
        self.check_space(25)
        try:
            self.canvas.setFont('MalgunBold', 16)
        except:
            self.canvas.setFont(self.font, 16)
        self.canvas.drawString(self.L1, self.current_y, "2.3 유출 행위")
        self.current_y -= 28
        
        text = "자료를 가로 파일이 USB 저장 장치와 개인 메신저라는 두 가지 경로를 통해 외부로 유출된 정황이 식별되었습니다."
        self.draw_paragraph(self.L2, text, 13, max_w)
        self.current_y -= 18
        
        # 경로 1
        self.canvas.setFont(self.font, 13)
        self.canvas.drawString(self.L4, self.current_y, "경로 1: USB 저장 장치를 통한 유출")
        self.current_y -= 20
        
        usb_details = [
            "레지스트리(USBSTOR) 및 시스템 로그 분석 결과, 파일 다운로드 직후인 2025년 9월 15일 14:25에 'SanDisk Ultra Flair' 모델의 USB 장치(S/N: 4C530001356789BEED)가 PC에 연결된 기록을 확인하였습니다.",
            "해당 USB는 과거에도 여러 차례 사용된 이력이 있으며, 파일 취득 시점과 지연 매우 인접한 시점이 매우 인접하여 데이터 복사를 위한 목적으로 사용되었을 가능성이 높습니다."
        ]
        
        for detail in usb_details:
            lines = self._wrap_text(detail, detail_max_w, 11)
            needed = len(lines) * 16 + 5
            self.check_space(needed)
            self.canvas.drawString(self.L4 + 18, self.current_y, "○")
            self.draw_paragraph(self.L4 + 35, detail, 11, detail_max_w, line_spacing=16)
            self.current_y -= 5
        
        self.current_y -= 10
        
        # 경로 2
        self.canvas.setFont(self.font, 13)
        self.canvas.drawString(self.L4, self.current_y, "경로 2: 메신저를 통한 유출")
        self.current_y -= 20
        
        kakao_details = [
            "카카오톡 PC 버전의 아티팩트 분석 결과, 2025년 9월 15일 14:30 경 외부 대화 상대에게 파일이 전송된 기록을 확인하였습니다.",
            "대화 내용은 암호화되어 직접적인 확인이 불가능하나, 메신저 캐시 폴더에서 유출된 파일과 동일한 이름 및 크기(15.4MB)를 가진 파일의 조각(fragment)이 발견되었습니다. 이는 파일 전송 행위의 강력한 증거로 판단됩니다."
        ]
        
        for detail in kakao_details:
            lines = self._wrap_text(detail, detail_max_w, 11)
            needed = len(lines) * 16 + 5
            self.check_space(needed)
            self.canvas.drawString(self.L4 + 18, self.current_y, "○")
            self.draw_paragraph(self.L4 + 35, detail, 11, detail_max_w, line_spacing=16)
            self.current_y -= 5
        
        self.current_y -= 10
        
        # 관련 증거
        evidence2 = [
            "Registry (USBSTOR): SanDisk Ultra Flair USB 연결 기록",
            "setupapi.dev.log: 장치 연결 이벤트 로그",
            "KakaoTalk Cache Data: [대외비]_고객정보_2025_3Q.xlsx 파일 조각 데이터"
        ]
        evidence_height = 20 + len(evidence2) * 18
        self.check_space(evidence_height)
        
        self.canvas.setFont(self.font, 13)
        self.canvas.drawString(self.L4, self.current_y, "관련 증거:")
        self.current_y -= 22
        
        self.canvas.setFont(self.font, 12)
        for ev in evidence2:
            self.canvas.drawString(self.L4 + 18, self.current_y, "○")
            self.canvas.drawString(self.L4 + 35, self.current_y, ev)
            self.current_y -= 18
        
        self.current_y -= 20
        
        # 2.4 증거 인멸 행위
        if self.current_y < 350:
            self.new_page()
        
        self.check_space(25)
        try:
            self.canvas.setFont('MalgunBold', 16)
        except:
            self.canvas.setFont(self.font, 16)
        self.canvas.drawString(self.L1, self.current_y, "2.4 증거 인멸 행위")
        self.current_y -= 28
        
        text = "분석 대상자는 정보 유출 후 자신의 행적을 숨기기 위해 관련 디지털 증거를 삭제하려 한 것으로 보입니다."
        self.draw_paragraph(self.L2, text, 13, max_w)
        self.current_y -= 18
        
        # 상세 분석
        self.canvas.setFont(self.font, 13)
        self.canvas.drawString(self.L4, self.current_y, "상세 분석 결과:")
        self.current_y -= 20
        
        destruction_details = [
            "파일 삭제: Downloads 폴더에 있던 '[대외비]_고객정보_2025_3Q.xlsx' 파일은 현재 존재하지 않으며, 휴지통($Recycle.Bin) 분석 결과 2025년 9월 15일 14:40 ~ 14:41 사이에 해당 파일이 삭제되었음을 확인하였습니다.",
            "가능 삭제: Chrome 브라우저의 접속 기록 중, 유출 행위가 발생한 2025년 9월 15일 14:20 ~ 14:30 사이의 기록이 선택적으로 삭제되었습니다.",
            "복구 가능성: MFT(Master File Table) 분석 결과, 삭제된 파일의 메타데이터가 시스템에 그대로 남아있어 일부 파일의 복구가 가능한 상태입니다. 또한, 브라우저 캐시 및 세션 파일에도 삭제된 기록의 일부가 잔존하여 구글 드라이브 접속 사실을 확인할 수 있었습니다.",
            "Prefetch 분석 결과, 보안 삭제 프로그램인 $Delete64.exe가 14:41에 실행된 흔적이 발견되어, 단순 삭제를 넘어 영구 삭제를 시도했을 가능성도 존재합니다."
        ]
        
        for detail in destruction_details:
            lines = self._wrap_text(detail, detail_max_w, 11)
            needed = len(lines) * 16 + 5
            self.check_space(needed)
            self.canvas.drawString(self.L4 + 18, self.current_y, "○")
            self.draw_paragraph(self.L4 + 35, detail, 11, detail_max_w, line_spacing=16)
            self.current_y -= 5
        
        self.current_y -= 10
        
        # 관련 증거
        evidence3 = [
            "$Recycle.Bin Metadata: 파일 삭제 시간 및 원본 경로 정보",
            "MFT Entry: 삭제된 파일의 메타데이터",
            "Chrome Cache/Session Files: 삭제된 시간대의 웹 접속 흔적",
            "Prefetch Files: $Delete64.exe.pf 실행 기록"
        ]
        evidence_height = 20 + len(evidence3) * 18
        self.check_space(evidence_height)
        
        self.canvas.setFont(self.font, 13)
        self.canvas.drawString(self.L4, self.current_y, "관련 증거:")
        self.current_y -= 22
        
        self.canvas.setFont(self.font, 12)
        for ev in evidence3:
            self.canvas.drawString(self.L4 + 18, self.current_y, "○")
            self.canvas.drawString(self.L4 + 35, self.current_y, ev)
            self.current_y -= 18
    
    def section3_conclusion(self, data):
        """섹션 3: 최종 분석 결과 및 결론"""
        max_w = self.width - self.L2 - 30
        
        self.new_page()
        
        # 3. 최종 분석 결과 및 결론
        self.check_space(30)
        try:
            self.canvas.setFont('MalgunBold', 19)
        except:
            self.canvas.setFont(self.font, 19)
        self.canvas.setFillColor(self.black)
        self.canvas.drawString(self.L0, self.current_y, "3. 최종 분석 결과 및 결론")
        self.current_y -= 35
        
        # 3.1 확인된 사실
        self.check_space(25)
        try:
            self.canvas.setFont('MalgunBold', 16)
        except:
            self.canvas.setFont(self.font, 16)
        self.canvas.drawString(self.L1, self.current_y, "3.1 확인된 사실 (Facts)")
        self.current_y -= 28
        
        text = "본 분석을 통해 객관적인 디지털 증거로 확인된 사실은 다음과 같습니다."
        self.draw_paragraph(self.L2, text, 13, max_w)
        self.current_y -= 18
        
        facts = [
            "(사실 1) 2025년 9월 15일 14시 23분, 분석 대상 PC에서 구글 드라이브를 통해 '[대외비]_고객정보_2025_3Q.xlsx' (15.4MB) 파일이 다운로드되었습니다.",
            "(사실 2) 파일 다운로드 2분 후인 14시 25분, 외부 저장 장치 'SanDisk Ultra Flair' 모델이 PC에 연결되었습니다.",
            "(사실 3) 14시 30분경, 카카오톡 메신저를 통해 상기 파일과 동일한 크기와 이름의 파일이 전송된 흔적이 발견되었습니다.",
            "(사실 4) 14시 40분, 다운로드되었던 원본 파일이 삭제되었으며, 관련 시간대의 웹 브라우저 접속 기록 또한 삭제되었습니다.",
            "(사실 5) 14시 41분, 데이터 영구 삭제 유틸리티인 $Delete64.exe가 실행된 기록이 확인되었습니다."
        ]
        
        self.canvas.setFont(self.font, 12)
        fact_max_w = self.width - self.L4 - 30
        for fact in facts:
            lines = self._wrap_text(fact, fact_max_w, 12)
            self.check_space(len(lines) * 16 + 5)
            
            for line in lines:
                self.canvas.drawString(self.L4, self.current_y, line)
                self.current_y -= 16
            self.current_y -= 5
        
        self.current_y -= 20
        
        # 3.2 종합 의견 및 재구성
        self.check_space(25)
        try:
            self.canvas.setFont('MalgunBold', 16)
        except:
            self.canvas.setFont(self.font, 16)
        self.canvas.drawString(self.L1, self.current_y, "3.2 종합 의견 및 재구성 (Reconstruction)")
        self.current_y -= 28
        
        text = "확인된 디지털 증거를 시간순으로 재구성하면, 정보 유출을 불 수 있는 일련의 행위가 다음과 같이 식별됩니다."
        self.draw_paragraph(self.L2, text, 13, max_w)
        self.current_y -= 18
        
        para1 = "2025년 9월 15일, 먼저 특정 기밀 파일이 PC로 다운로드되었습니다(사실 1). 그 직후, 외부 저장 매체가 연결됨(사실 2)과 메신저를 통한 파일 전송 흔적(사실 3)이라는 두 가지 잠재적 데이터 유출 경로가 동시에 확인되었습니다. 자료 취득부터 외부 장치 연결, 메신저 사용까지의 짧아진 시간 경과 및 시간 순서를 고려할 때, 이는 계획적인 정보 반출로 볼 수 있는 충분한 정황을 시사합니다."
        self.draw_paragraph(self.L2, para1, 13, max_w, line_spacing=18)
        self.current_y -= 18
        
        para2 = "이후, 선택된 직업의 흔적을 제거하기 위한 행위가 이어졌습니다. 다운로드된 원본 파일과 관련 웹 접속 기록이 삭제되었고(사실 4), 일반적인 삭제가 아닌 데이터 영구 삭제 도구가 사용된 흔적이 확인되었습니다(사실 5)로 확인되었습니다. 이는 단순히 데이터를 정리하는 목적의 범위를 벗어나 디지털 증거의 흔적을 의도적으로 인멸하고자 한 시도로 해석될 수 있습니다."
        self.draw_paragraph(self.L2, para2, 13, max_w, line_spacing=18)
        self.current_y -= 18
        
        conclusion = "결론적으로, 이러한 일련의 행위는 우발적인 실수가 아닌 명확한 의도를 가진 계획적 정보 유출로 판단됩니다."
        try:
            self.canvas.setFont('MalgunBold', 13)
        except:
            self.canvas.setFont(self.font, 13)
        self.draw_paragraph(self.L2, conclusion, 13, max_w, line_spacing=18)
    
    # ===================================================================
    # 메인 생성 메서드
    # ===================================================================
    
    def generate_report(self, output, data=None):
        """보고서 생성"""
        if data is None:
            data = ReportData()
        
        print("=" * 60)
        print("📄 보안 진단 보고서 생성 (들여쓰기 최적화)")
        print("=" * 60)
        print(f"출력: {output}\n")
        
        self.canvas = canvas.Canvas(output, pagesize=A4, pageCompression=0)
        
        self.page1(self.canvas, data)
        self.page2(self.canvas)
        
        # 페이지 3부터 본문을 약간 오른쪽으로 이동시킵니다 (왼쪽 여백 확보)
        # 필요하면 dx 값을 조절하세요 (양수 = 오른쪽 이동)
        def _shift_body_right(dx: int = 12):
            self.L0 += dx
            self.L1 += dx
            self.L2 += dx
            self.L3 += dx
            self.L4 += dx

        _shift_body_right(12)

        self._bg(self.canvas, 3)
        self._pgn(self.canvas, 3)
        self.current_page = 3
        self.current_y = self.top
        
        self.section1_overview(data)
        self.section2_analysis_detail(data)
        self.section3_conclusion(data)
        
        self.canvas.save()
        
        print("\n✅ 완료! (들여쓰기 최적화)")
        print(f"✅ 총 {self.current_page}페이지 생성됨")