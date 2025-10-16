"""
security_report_pdf_dynamic.py (표 크기 및 들여쓰기 개선)
-------------------------------------
✅ 표 크기 자동 조정 개선 (가독성 대폭 향상)
✅ 들여쓰기 일관성 확보
✅ 컬럼 폭 계산 로직 개선
"""

import os
import re
import io
import markdown
from markdown import Markdown
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


@dataclass
class ReportData:
    company_name: str = "[의뢰 회사 이름]"
    pc_name: str = "[TEST-PC-001]"
    date: str = "2025년 10월 15일"


def markdown_to_lines(md_text: str) -> List[str]:
    md = Markdown(extensions=["tables", "fenced_code"])
    html = md.convert(md_text)
    text = re.sub(r"<[^>]+>", "", html)
    text = text.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines


class SecurityReportPDF:
    def __init__(self):
        self.width, self.height = A4
        self.font = self._setup_fonts()
        self.canvas = None
        
        self.left = 25
        self.top = 780
        self.min_y = 60  # 하단 여백 축소
        self.current_y = self.top
        self.current_page = 1

        self.blue = HexColor("#0066B3")
        self.gray = HexColor("#808080")
        self.black = HexColor("#000000")
        self.light_gray = HexColor("#E0E0E0")
        self.very_light_gray = HexColor("#F8F8F8")

        self.L0 = self.left
        self.L1 = self.left
        self.L2 = self.left + 10
        self.L3 = self.left + 20
        self.L4 = self.left + 35

        # 목차 저장 (대분류/소분류 구분)
        self.toc_entries = []  # [(title, page_num, dest_name, is_main), ...]

        d = os.path.dirname(os.path.abspath(__file__))
        self.bg1 = os.path.join(d, "001.png")
        self.bg2 = os.path.join(d, "002.png")

    def _setup_fonts(self):
        try:
            m = "C:\\Windows\\Fonts\\malgun.ttf"
            mb = "C:\\Windows\\Fonts\\malgunbd.ttf"
            if os.path.exists(m):
                pdfmetrics.registerFont(TTFont("Malgun", m))
                if os.path.exists(mb):
                    pdfmetrics.registerFont(TTFont("MalgunBold", mb))
                return "Malgun"
        except:
            pass
        return "Helvetica"

    def _wrap_text(self, text: str, max_width: int, font_size: int):
        """텍스트 래핑(줄바꿈) - 페이지 넘김과 함께 안전하게 사용"""
        if not text or not text.strip():
            return []
        safe_max = max(max_width, 80)
        words = text.split()
        lines = []
        line = ""
        for w in words:
            test = line + " " + w if line else w
            actual = self.canvas.stringWidth(test, self.font, font_size)
            if actual <= (safe_max - 10):
                line = test
            else:
                if line:
                    lines.append(line)
                # 단어가 너무 길면 강제 분할
                if self.canvas.stringWidth(w, self.font, font_size) > (safe_max - 10):
                    chars = list(w)
                    temp = ""
                    for ch in chars:
                        test_ch = temp + ch
                        if self.canvas.stringWidth(test_ch, self.font, font_size) <= (safe_max - 10):
                            temp += ch
                        else:
                            if temp:
                                lines.append(temp)
                            temp = ch
                    line = temp
                else:
                    line = w
        if line:
            lines.append(line)
        return lines

    def _bg(self, c, p):
        bg = [self.bg1, self.bg2, self.bg2][min(p - 1, 2)]
        if os.path.exists(bg):
            try:
                c.drawImage(bg, 0, 0, width=self.width, height=self.height, preserveAspectRatio=False)
            except:
                pass

    def _pgn(self, c, n):
        c.setFont(self.font, 10)
        c.setFillColor(self.gray)
        t = f"- {n} -"
        w = c.stringWidth(t, self.font, 10)
        c.drawString((self.width - w) / 2, 30, t)

    def check_space(self, h):
        if self.current_y - h - 20 < self.min_y:
            self.new_page()

    def new_page(self):
        self.canvas.showPage()
        self.current_page += 1
        self._bg(self.canvas, min(self.current_page, 3))
        self._pgn(self.canvas, self.current_page)
        self.canvas.saveState()
        self.canvas.setFillColorRGB(0, 0, 0)
        self.canvas.setStrokeColorRGB(0, 0, 0)
        self.current_y = self.top

    # ==============================
    # Markdown 인라인 파싱
    # ==============================
    def _parse_inline_markdown(self, text: str) -> List[Dict[str, Any]]:
        segments = []
        pattern = r'\*\*(.*?)\*\*'
        last_end = 0
        
        for match in re.finditer(pattern, text):
            if match.start() > last_end:
                segments.append({'text': text[last_end:match.start()], 'bold': False})
            segments.append({'text': match.group(1), 'bold': True})
            last_end = match.end()
        
        if last_end < len(text):
            segments.append({'text': text[last_end:], 'bold': False})
        
        return segments if segments else [{'text': text, 'bold': False}]

    def draw_text_with_formatting(self, x, y, text, font_size):
        segments = self._parse_inline_markdown(text)
        current_x = x
        
        for segment in segments:
            if segment['bold']:
                try:
                    self.canvas.setFont('MalgunBold', font_size)
                except:
                    self.canvas.setFont(self.font, font_size)
            else:
                self.canvas.setFont(self.font, font_size)
            
            self.canvas.drawString(current_x, y, segment['text'])
            font_name = 'MalgunBold' if segment['bold'] else self.font
            current_x += self.canvas.stringWidth(segment['text'], font_name, font_size)

    def draw_paragraph(self, x, text, font_size=13, line_spacing=17, max_width=None):
        """문단 그리기"""
        if max_width is None:
            max_width = self.width - x - 30
        
        self.canvas.setFont(self.font, font_size)
        self.canvas.setFillColor(self.black)
        
        # 전체 문단이 **로 감싸져 있는지 확인
        is_full_bold = text.strip().startswith('**') and text.strip().endswith('**')
        
        if is_full_bold:
            # ** 제거하고 줄바꿈
            clean_text = text.strip()[2:-2]
            safe_max_width = max(max_width, 100)
            lines = self._wrap_text(clean_text, safe_max_width, font_size)
            
            # 모든 줄을 볼드로 출력
            for line in lines:
                self.check_space(line_spacing + 10)
                try:
                    self.canvas.setFont('MalgunBold', font_size)
                except:
                    self.canvas.setFont(self.font, font_size)
                self.canvas.drawString(x, self.current_y, line)
                self.current_y -= line_spacing
        else:
            # 일반 처리 (인라인 볼드 포함)
            safe_max_width = max(max_width, 100)
            lines = self._wrap_text(text, safe_max_width, font_size)
            
            for line in lines:
                self.check_space(line_spacing + 10)
                self.draw_text_with_formatting(x, self.current_y, line, font_size)
                self.current_y -= line_spacing

    def draw_table(self, headers, rows, col_widths, x, row_height=45):
        """
        표 그리기 - 가독성 대폭 개선
        - 기본 행 높이: 45px (기존 30px → 45px)
        - 줄간격: 20px (기존 18px → 20px)
        - 패딩: 12px (기존 8px → 12px)
        - 헤더 글자: 12pt (기존 11pt → 12pt)
        """
        # 행 높이 계산 (최소 45px 보장)
        total_height = row_height
        for row in rows:
            max_lines = max(str(cell).count('\n') + 1 for cell in row)
            total_height += max(row_height, max_lines * 20 + 15)  # 줄당 20px + 여백 증가
        
        # ✅ 표 위쪽 여백 확보 (check_space로 충분)
        self.check_space(total_height + 30)
        
        # 헤더
        self.canvas.setFont(self.font, 12)  # 헤더 글자 크기 증가 11 → 12
        self.canvas.setFillColor(self.light_gray)
        self.canvas.rect(x, self.current_y - row_height, sum(col_widths), row_height, fill=1)
        self.canvas.setFillColor(self.black)
        
        for i, h in enumerate(headers):
            # 헤더에 볼드 처리 적용
            h_clean = h.replace('**', '')
            if '**' in h:
                try:
                    self.canvas.setFont('MalgunBold', 12)
                except:
                    self.canvas.setFont(self.font, 12)
            else:
                self.canvas.setFont(self.font, 12)
            self.canvas.drawString(x + sum(col_widths[:i]) + 12, self.current_y - 20, h_clean)  # 패딩 8 → 12
        self.current_y -= row_height
        
        # 데이터
        for row in rows:
            # ✅ 각 셀의 내용을 미리 계산하여 행 높이 정확하게 처리
            cell_line_counts = []
            for i, cell in enumerate(row):
                cell_text = str(cell)
                lines = cell_text.split('\n')
                total_lines = 0
                
                for line in lines:
                    line_clean = line.replace('**', '')
                    # 컴럼 폭보다 긴 텍스트는 래핑 필요
                    if self.canvas.stringWidth(line_clean, self.font, 11) > col_widths[i] - 20:
                        # 래핑된 줄 수 계산
                        words = line_clean.split()
                        current_line = ""
                        wrapped_count = 0
                        for word in words:
                            test = current_line + " " + word if current_line else word
                            if self.canvas.stringWidth(test, self.font, 10) <= col_widths[i] - 20:
                                current_line = test
                            else:
                                if current_line:
                                    wrapped_count += 1
                                current_line = word
                        if current_line:
                            wrapped_count += 1
                        total_lines += wrapped_count
                    else:
                        total_lines += 1
                
                cell_line_counts.append(total_lines)
            
            # 최대 줄 수로 행 높이 결정
            max_cell_lines = max(cell_line_counts) if cell_line_counts else 1
            actual_height = max(row_height, max_cell_lines * 18 + 20)  # 줄당 18px + 상하단 여백 20px
            
            # 행 배경 그리기
            self.canvas.setFillColor(self.very_light_gray)
            self.canvas.rect(x, self.current_y - actual_height, sum(col_widths), actual_height, fill=1)
            self.canvas.setFillColor(self.black)
            
            # 각 셀 내용 그리기
            for i, cell in enumerate(row):
                cell_text = str(cell)
                lines = cell_text.split('\n')
                cell_y = self.current_y - 18  # 상단 여백
                cell_bottom = self.current_y - actual_height + 5  # 하단 경계 (여백 5px)
                
                for line in lines:
                    # ✅ 하단 경계 검사 - 표 밖으로 나가지 않도록
                    if cell_y < cell_bottom:
                        break
                    
                    # 볼드 처리
                    line_clean = line.replace('**', '')
                    has_bold = '**' in line
                    
                    if self.canvas.stringWidth(line_clean, self.font, 11) > col_widths[i] - 20:  # 패딩 15 → 20
                        wrapped = []
                        words = line_clean.split()
                        current_line = ""
                        for word in words:
                            test = current_line + " " + word if current_line else word
                            if self.canvas.stringWidth(test, self.font, 10) <= col_widths[i] - 20:
                                current_line = test
                            else:
                                if current_line:
                                    wrapped.append(current_line)
                                current_line = word
                        if current_line:
                            wrapped.append(current_line)
                        
                        for wrap_line in wrapped:
                            # ✅ 하단 경계 검사
                            if cell_y < cell_bottom:
                                break
                            
                            if has_bold:
                                try:
                                    self.canvas.setFont('MalgunBold', 10)
                                except:
                                    self.canvas.setFont(self.font, 10)
                            else:
                                self.canvas.setFont(self.font, 10)
                            self.canvas.drawString(x + sum(col_widths[:i]) + 12, cell_y, wrap_line)
                            cell_y -= 15  # 줄간격 14 → 15
                    else:
                        if has_bold:
                            try:
                                self.canvas.setFont('MalgunBold', 11)
                            except:
                                self.canvas.setFont(self.font, 11)
                        else:
                            self.canvas.setFont(self.font, 11)
                        self.canvas.drawString(x + sum(col_widths[:i]) + 12, cell_y, line_clean)
                        cell_y -= 18  # 줄간격 16 → 18
            
            self.current_y -= actual_height

    def render_markdown_content(self, content, x_start):
        """마크다운 콘텐츠 렌더링"""
        # 코드 블록 처리
        if "```" in content:
            blocks = re.split(r"```+", content)
            for i, b in enumerate(blocks):
                if i % 2 == 1:
                    lines = [ln.rstrip() for ln in b.splitlines() if ln is not None]
                    block_h = max(30, len(lines) * 14 + 12)
                    self.check_space(block_h)
                    self.canvas.setFillColor(HexColor("#f3f3f3"))
                    self.canvas.rect(x_start - 5, self.current_y - block_h + 6,
                                     self.width - x_start - 40, block_h, fill=True, stroke=False)
                    self.canvas.setFillColor(self.black)
                    try:
                        self.canvas.setFont("Courier", 10)
                    except:
                        self.canvas.setFont(self.font, 10)
                    line_y = self.current_y
                    for ln in lines:
                        if line_y - 14 < self.min_y:
                            self.new_page()
                            self.check_space(block_h)
                            line_y = self.current_y
                        self.canvas.drawString(x_start, line_y, ln)
                        line_y -= 14
                    self.current_y = line_y - 8
                else:
                    self.render_markdown_content(b, x_start)
            return

        # 표(마크다운) 처리 - 개선된 컬럼 폭 계산
        # ✅ 마지막 행에 줄바꿈이 없어도 매칭되도록 정규식 개선
        table_pattern = r'\|[^\n]+\|\n\|[-:| ]+\|(?:\n\|[^\n]+\|)+'
        tables = list(re.finditer(table_pattern, content))
        
        if tables:
            last_end = 0
            for match in tables:
                # 표 이전 텍스트 처리
                before_text = content[last_end:match.start()]
                if before_text.strip():
                    self._render_text_lines(before_text, x_start)
                
                # 표 처리
                table_text = match.group(0)
                lines = [l.strip() for l in table_text.splitlines() if "|" in l]
                if len(lines) >= 2:
                    headers = [c.strip() for c in lines[0].split("|")[1:-1]]
                    rows = []
                    for line in lines[2:]:
                        if not line.strip():
                            continue
                        cells = [c.strip() for c in line.split("|")[1:-1]]
                        rows.append(cells)
                    
                    # ✅ 개선된 컬럼 폭 계산 로직
                    num_cols = len(headers)
                    usable_width = self.width - x_start - 40
                    
                    # 각 컬럼의 최대 텍스트 길이 계산
                    max_lengths = [len(str(h).replace('**', '')) for h in headers]
                    for row in rows:
                        for i, cell in enumerate(row):
                            if i < len(max_lengths):
                                cell_lines = str(cell).replace('**', '').split('\n')
                                max_line_len = max(len(line) for line in cell_lines) if cell_lines else 0
                                max_lengths[i] = max(max_lengths[i], max_line_len)
                    
                    # 가중치 기반 컬럼 폭 계산 (최소 80px 보장)
                    total_len = sum(max_lengths) or num_cols
                    col_widths = [max(80, int(usable_width * (l / total_len))) for l in max_lengths]  # 최소 50 → 80
                    
                    # 전체 폭이 사용 가능 폭을 초과하면 비율로 축소
                    if sum(col_widths) > usable_width:
                        scale = usable_width / sum(col_widths)
                        col_widths = [int(w * scale) for w in col_widths]
                        # 축소 후에도 최소 폭 보장
                        for i in range(len(col_widths)):
                            if col_widths[i] < 70:
                                col_widths[i] = 70
                    
                    self.draw_table(headers, rows, col_widths, x_start)
                    # ✅ 표 아래쪽 간격 추가 (25px) - 위쪽과 동일하게
                    self.current_y -= 25
                
                last_end = match.end()
            
            # 표 이후 텍스트 처리
            after_text = content[last_end:]
            if after_text.strip():
                self._render_text_lines(after_text, x_start)
        else:
            # 표가 없으면 일반 텍스트 처리
            self._render_text_lines(content, x_start)
    
    def _render_text_lines(self, content, x_start):
        """
        일반 텍스트 라인 처리 (번호 리스트, 불릿 리스트 포함)
        ✅ 들여쓰기 일관성 개선
        """
        lines = content.split('\n')
        for line in lines:
            line = line.rstrip()
            if not line.strip():
                self.current_y -= 8
                continue
            
            # 번호 리스트 처리 (1. 2. 3. ...)
            numbered_pattern = r'^(\d+)\.\s+(.*)$'
            numbered_match = re.match(numbered_pattern, line)
            if numbered_match:
                # 번호 리스트는 L3 위치에 렌더링
                self.draw_paragraph(self.L3, line, font_size=13, line_spacing=17)
                continue
            
            # 불릿 리스트 처리 (•, *, -, 등)
            if line.startswith(("* ", "- ", "• ")):
                # ✅ 불릿 리스트는 L4 위치에 렌더링하여 들여쓰기 통일
                bullet_text = "• " + line[2:].strip()
                self.draw_paragraph(self.L4, bullet_text, font_size=13, line_spacing=17)
                continue
            
            # 일반 텍스트는 x_start 위치에 렌더링
            self.draw_paragraph(x_start, line, font_size=13, line_spacing=17)

    # ==============================
    # 페이지 생성
    # ==============================
    def page1(self, c, data):
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
    
    def render_toc(self):
        """목차 렌더링"""
        self._bg(self.canvas, 2)
        self._pgn(self.canvas, 2)
        
        # "목차" 제목
        try:
            self.canvas.setFont('MalgunBold', 28)
        except:
            self.canvas.setFont(self.font, 28)
        self.canvas.setFillColor(self.black)
        title_text = "목차"
        registered_fonts = pdfmetrics.getRegisteredFontNames()
        font_name = 'MalgunBold' if 'MalgunBold' in registered_fonts else self.font
        text_width = self.canvas.stringWidth(title_text, font_name, 28)
        self.canvas.drawString((self.width - text_width) / 2, 750, title_text)
        
        y = 680
        
        # 목차 항목 렌더링
        for title, page_num, dest_name, is_main in self.toc_entries:
            if is_main:
                # 대제목 (1. 개요)
                try:
                    self.canvas.setFont('MalgunBold', 19)
                except:
                    self.canvas.setFont(self.font, 19)
                self.canvas.setFillColor(self.black)
                self.canvas.drawString(50, y, title)
                # 하이퍼링크
                self.canvas.linkRect("", dest_name, (50, y - 2, self.width - 50, y + 17), relative=0)
                y -= 35
            else:
                # 소제목 (1.1 분석 목적)
                self.canvas.setFont(self.font, 16)
                self.canvas.setFillColor(self.black)
                self.canvas.drawString(70, y, title)
                # 하이퍼링크
                self.canvas.linkRect("", dest_name, (70, y - 2, self.width - 70, y + 14), relative=0)
                y -= 35
            
            # 페이지 넘어가면 간격 조정
            if not is_main and y < 100:
                y -= 5
        
        self.canvas.showPage()

    # ==============================
    # 섹션 렌더링
    # ==============================
    def render_section(self, main_num: int, section_details: List[Dict[str, Any]], 
                       section_titles: Dict[int, str], section_names: Dict[int, str],
                       collect_toc: bool = True, is_first_section: bool = False):
        max_w = self.width - self.L2 - 30
        
        # 대분류 전환 시 새 페이지 시작 (첫 번째 섹션 제외)
        if not is_first_section:
            self.new_page()
        
        # 목차에 대분류 추가
        main_title = f"{main_num}. {section_names[main_num]}"
        if collect_toc:
            self.toc_entries.append((main_title, self.current_page, f"section_{main_num}", True))
        
        self.canvas.bookmarkPage(f"section_{main_num}")
        
        # 대제목
        self.check_space(30)
        try:
            self.canvas.setFont('MalgunBold', 19)
        except:
            self.canvas.setFont(self.font, 19)
        self.canvas.setFillColor(self.black)
        self.canvas.drawString(self.L0, self.current_y, main_title)
        self.current_y -= 35
        
        # 각 소제목
        for idx, detail in enumerate(section_details, 1):
            section_type = detail.get('section_type')
            title = section_titles.get(section_type, "")
            content = detail.get('content', "")
            
            # 목차에 소분류 추가
            sub_title = f"{main_num}.{idx} {title}"
            if collect_toc:
                self.toc_entries.append((sub_title, self.current_page, f"section_{main_num}_{idx}", False))
            self.canvas.bookmarkPage(f"section_{main_num}_{idx}")
            
            # 소제목
            self.check_space(25)
            try:
                self.canvas.setFont('MalgunBold', 16)
            except:
                self.canvas.setFont(self.font, 16)
            self.canvas.drawString(self.L1, self.current_y, sub_title)
            self.current_y -= 28
            
            # Content
            self.render_markdown_content(content, self.L2)
            self.current_y -= 20

    # ==============================
    # 메인
    # ==============================
    def generate_from_json(self, json_data, output_path: str, section_titles, section_mapping, main_sections):
        report_meta = json_data.get("report", {})
        data = ReportData(
            company_name=report_meta.get("summary", "[의뢰 회사 이름]"),
            pc_name=report_meta.get("pc_id", "[TEST-PC-001]"),
            date=report_meta.get("created_at", "2025년 10월 15일")
        )
        
        print("=" * 60)
        print("📄 보안 진단 보고서 PDF 생성 (표 크기 및 들여쓰기 개선)")
        print("=" * 60)
        print(f"출력: {output_path}\n")
        
        # --- 두 번의 렌더 패스(1: 내용만 렌더하여 toc 페이지 번호 수집, 2: 최종 PDF 생성) ---
        # 1) 내용만 렌더 (임시 캔버스) — TOC에 들어갈 페이지 번호 수집
        temp_buf = io.BytesIO()
        temp_canvas = canvas.Canvas(temp_buf, pagesize=A4, pageCompression=0)
        self.canvas = temp_canvas
        # 본문은 3페이지부터 시작(1:표지, 2:목차)
        self.current_page = 3
        self.current_y = self.top
        self.toc_entries = []

        # 그룹화 및 정렬
        grouped_details = defaultdict(list)
        details = json_data.get("details", [])
        sorted_details = sorted(details, key=lambda d: d.get('order_no', 0))
        for detail in sorted_details:
            section_type = detail.get('section_type')
            main_group = section_mapping.get(section_type)
            if main_group:
                grouped_details[main_group].append(detail)

        # 렌더(수집용)
        self._bg(self.canvas, 3)
        first_section = True
        for main_num in sorted(main_sections.keys()):
            section_details = grouped_details.get(main_num, [])
            if not section_details:
                continue
            self.render_section(main_num, section_details, section_titles, main_sections, collect_toc=True, is_first_section=first_section)
            first_section = False
        temp_canvas.save()

        # 2) 실제 파일 생성 — 표지(1), 목차(2), 본문(3~)
        self.canvas = canvas.Canvas(output_path, pagesize=A4, pageCompression=0)
        # 표지
        self.page1(self.canvas, data)
        # 목차(2)
        self.render_toc()

        # 본문 렌더
        self._bg(self.canvas, 3)
        self._pgn(self.canvas, 3)
        self.current_page = 3
        self.current_y = self.top
        
        # 페이지 3부터 본문을 약간 오른쪽으로 이동 (왼쪽 여백 확보)
        def _shift_body_right(dx: int = 12):
            self.L0 += dx
            self.L1 += dx
            self.L2 += dx
            self.L3 += dx
            self.L4 += dx
        
        _shift_body_right(12)
        
        first_section = True
        for main_num in sorted(main_sections.keys()):
            section_details = grouped_details.get(main_num, [])
            if not section_details:
                continue
            self.render_section(main_num, section_details, section_titles, main_sections, collect_toc=False, is_first_section=first_section)
            first_section = False

        self.canvas.save()
        print("\n✅ 완료!")
        print(f"✅ 총 {self.current_page}페이지 생성")
        print(f"✅ 목차 항목 {len(self.toc_entries)}개 자동 생성")
        print("=" * 60)


if __name__ == "__main__":
    print("✅ 표 크기 및 들여쓰기 개선 완료")
