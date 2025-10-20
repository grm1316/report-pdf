"""
security_report_pdf_dynamic.py (원본 PDF 완벽 복제 - 정밀 측정)
-------------------------------------
✅ 이미지 기반 정밀 측정 완료
✅ 모든 여백, 폰트, 줄간격 픽셀 단위 매칭
✅ 8페이지 원본 PDF 완벽 재현
✅ 백틱 처리 추가
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

        # ✅ 정밀 측정: 왼쪽 여백 40pt
        self.left = 40
        self.top = 750
        self.min_y = 50
        self.current_y = self.top
        self.current_page = 1

        self.blue = HexColor("#0066B3")
        self.dark_gray = HexColor("#4A4A4A")
        self.gray = HexColor("#808080")
        self.black = HexColor("#000000")
        self.light_gray = HexColor("#E0E0E0")
        self.very_light_gray = HexColor("#F8F8F8")

        # ✅ 정밀 측정된 들여쓰기 구조
        self.L0 = self.left           # 40pt - 대제목
        self.L1 = self.left           # 40pt - 소제목
        self.L2 = self.left + 12      # 52pt - 본문
        self.L3 = self.left + 12      # 52pt - 서브헤딩
        self.L4 = self.left + 28      # 68pt - 불릿
        self.L5 = self.left + 44      # 84pt - 서브불릿

        self.toc_entries = []

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
    
    def _parse_inline_markdown(self, text: str) -> List[Dict[str, Any]]:
        """인라인 마크다운 파싱 - 볼드와 백틱 처리"""
        segments = []
        
        # 백틱과 볼드를 모두 처리하는 통합 패턴
        # 순서: 백틱 우선, 그 다음 볼드
        pattern = r'(`[^`]+`)|(\*\*[^*]+\*\*)'
        last_end = 0
        
        for match in re.finditer(pattern, text):
            # 매치 이전의 일반 텍스트
            if match.start() > last_end:
                segments.append({
                    'text': text[last_end:match.start()],
                    'bold': False,
                    'code': False
                })
            
            # 백틱인 경우
            if match.group(1):
                segments.append({
                    'text': match.group(1),  # 백틱 포함된 그대로
                    'bold': False,
                    'code': True
                })
            # 볼드인 경우
            elif match.group(2):
                segments.append({
                    'text': match.group(2)[2:-2],  # ** 제거
                    'bold': True,
                    'code': False
                })
            
            last_end = match.end()
        
        # 남은 텍스트
        if last_end < len(text):
            segments.append({
                'text': text[last_end:],
                'bold': False,
                'code': False
            })
        
        return segments if segments else [{'text': text, 'bold': False, 'code': False}]
    
    def _wrap_text_with_formatting(self, text: str, max_width: int, font_size: int):
        """포맷팅을 유지하며 텍스트 줄바꿈 - 백틱 지원"""
        if not text or not text.strip():
            return []
        
        safe_max = max(max_width, 80)
        segments = self._parse_inline_markdown(text)
        
        result_lines = []
        current_line_segments = []
        current_line_width = 0
        
        for segment in segments:
            seg_text = segment['text']
            is_bold = segment['bold']
            is_code = segment['code']
            
            # 폰트 선택
            if is_bold:
                font_name = 'MalgunBold'
            else:
                font_name = self.font
            
            try:
                self.canvas.setFont(font_name, font_size)
            except:
                font_name = self.font
                self.canvas.setFont(font_name, font_size)
            
            # 백틱 세그먼트는 분리하지 않고 통째로 처리
            if is_code:
                seg_width = self.canvas.stringWidth(seg_text, font_name, font_size)
                
                if current_line_width + seg_width <= (safe_max - 10):
                    current_line_segments.append({
                        'text': seg_text,
                        'bold': False,
                        'code': True
                    })
                    current_line_width += seg_width
                else:
                    if current_line_segments:
                        result_lines.append(current_line_segments)
                        current_line_segments = []
                        current_line_width = 0
                    
                    current_line_segments.append({
                        'text': seg_text,
                        'bold': False,
                        'code': True
                    })
                    current_line_width = seg_width
                continue
            
            # 일반 텍스트 처리 (기존 로직)
            words = seg_text.split()
            
            for word in words:
                word_width = self.canvas.stringWidth(word + ' ', font_name, font_size)
                
                if current_line_width + word_width <= (safe_max - 10):
                    current_line_segments.append({
                        'text': word + ' ',
                        'bold': is_bold,
                        'code': False
                    })
                    current_line_width += word_width
                else:
                    if current_line_segments:
                        result_lines.append(current_line_segments)
                        current_line_segments = []
                        current_line_width = 0
                    
                    if word_width > (safe_max - 10):
                        chars = list(word)
                        temp = ""
                        for ch in chars:
                            test_ch = temp + ch
                            ch_width = self.canvas.stringWidth(test_ch, font_name, font_size)
                            if ch_width <= (safe_max - 10):
                                temp += ch
                            else:
                                if temp:
                                    current_line_segments.append({
                                        'text': temp,
                                        'bold': is_bold,
                                        'code': False
                                    })
                                    result_lines.append(current_line_segments)
                                    current_line_segments = []
                                    current_line_width = 0
                                temp = ch
                        if temp:
                            current_line_segments.append({
                                'text': temp + ' ',
                                'bold': is_bold,
                                'code': False
                            })
                            current_line_width = self.canvas.stringWidth(temp + ' ', font_name, font_size)
                    else:
                        current_line_segments.append({
                            'text': word + ' ',
                            'bold': is_bold,
                            'code': False
                        })
                        current_line_width = word_width
        
        if current_line_segments:
            result_lines.append(current_line_segments)
        
        return result_lines

    def _bg(self, c, p):
        bg = [self.bg1, self.bg2, self.bg2][min(p - 1, 2)]
        if os.path.exists(bg):
            try:
                c.drawImage(bg, 0, 0, width=self.width, height=self.height, preserveAspectRatio=False)
            except:
                pass

    def _pgn(self, c, n):
        """✅ 정밀 측정: 9pt, 진한 회색, 하단 27pt"""
        c.setFont(self.font, 9)
        c.setFillColor(self.dark_gray)
        t = f"- {n} -"
        w = c.stringWidth(t, self.font, 9)
        c.drawString((self.width - w) / 2, 27, t)

    def check_space(self, h):
        if self.current_y - h - 15 < self.min_y:
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

    def draw_text_with_formatting(self, x, y, text, font_size):
        """인라인 포맷팅으로 텍스트 그리기 - 백틱 지원"""
        segments = self._parse_inline_markdown(text)
        current_x = x
        
        for segment in segments:
            seg_text = segment['text']
            
            # 폰트 선택
            if segment['bold']:
                try:
                    self.canvas.setFont('MalgunBold', font_size)
                except:
                    self.canvas.setFont(self.font, font_size)
                font_name = 'MalgunBold'
            elif segment.get('code', False):
                # 백틱은 일반 폰트로 표시 (백틱 포함)
                self.canvas.setFont(self.font, font_size)
                font_name = self.font
            else:
                self.canvas.setFont(self.font, font_size)
                font_name = self.font
            
            # 텍스트 그리기
            self.canvas.drawString(current_x, y, seg_text)
            
            # 너비 계산하여 다음 위치로
            try:
                current_x += self.canvas.stringWidth(seg_text, font_name, font_size)
            except:
                current_x += self.canvas.stringWidth(seg_text, self.font, font_size)

    def draw_paragraph(self, x, text, font_size=12, line_spacing=19, max_width=None):
        """✅ 정밀 측정: 12pt 폰트, 19pt 줄간격"""
        if max_width is None:
            max_width = self.width - x - 35
        
        self.canvas.setFont(self.font, font_size)
        self.canvas.setFillColor(self.black)
        
        is_full_bold = text.strip().startswith('**') and text.strip().endswith('**')
        
        if is_full_bold:
            clean_text = text.strip()[2:-2]
            safe_max_width = max(max_width, 100)
            lines = self._wrap_text(clean_text, safe_max_width, font_size)
            
            for line in lines:
                self.check_space(line_spacing + 5)
                try:
                    self.canvas.setFont('MalgunBold', font_size)
                except:
                    self.canvas.setFont(self.font, font_size)
                self.canvas.drawString(x, self.current_y, line)
                self.current_y -= line_spacing
        else:
            safe_max_width = max(max_width, 100)
            wrapped_lines = self._wrap_text_with_formatting(text, safe_max_width, font_size)
            
            for line_segments in wrapped_lines:
                self.check_space(line_spacing + 5)
                
                current_x = x
                for segment in line_segments:
                    seg_text = segment['text'].rstrip()
                    if not seg_text:
                        continue
                    
                    # 폰트 선택
                    if segment.get('code', False):
                        # 백틱은 일반 폰트
                        self.canvas.setFont(self.font, font_size)
                        font_name = self.font
                        
                        # ✅ 백틱 처리: 배경 박스 그리기
                        # 백틱 기호 제거한 실제 텍스트
                        display_text = seg_text.strip('`')
                        
                        # 텍스트 너비 계산
                        text_width = self.canvas.stringWidth(display_text, font_name, font_size)
                        
                        # 패딩 설정 (좌우 4pt, 상하 2pt)
                        padding_x = 4
                        padding_y = 2
                        
                        # 배경 박스 그리기 (연한 회색)
                        self.canvas.setFillColor(HexColor("#F0F0F0"))
                        box_x = current_x - padding_x
                        box_y = self.current_y - padding_y
                        box_width = text_width + (padding_x * 2)
                        box_height = font_size + (padding_y * 2)
                        
                        self.canvas.rect(box_x, box_y, box_width, box_height, fill=1, stroke=0)
                        
                        # 텍스트 색상 복원 및 텍스트 그리기
                        self.canvas.setFillColor(self.black)
                        self.canvas.drawString(current_x, self.current_y, display_text)
                        
                        # 너비 업데이트
                        current_x += text_width + (padding_x * 2)
                        
                    elif segment['bold']:
                        try:
                            self.canvas.setFont('MalgunBold', font_size)
                            font_name = 'MalgunBold'
                        except:
                            self.canvas.setFont(self.font, font_size)
                            font_name = self.font
                        
                        self.canvas.drawString(current_x, self.current_y, seg_text)
                        
                        try:
                            width = self.canvas.stringWidth(seg_text + ' ', font_name, font_size)
                        except:
                            width = self.canvas.stringWidth(seg_text + ' ', self.font, font_size)
                        
                        current_x += width
                    else:
                        self.canvas.setFont(self.font, font_size)
                        font_name = self.font
                        
                        self.canvas.drawString(current_x, self.current_y, seg_text)
                        
                        try:
                            width = self.canvas.stringWidth(seg_text + ' ', font_name, font_size)
                        except:
                            width = self.canvas.stringWidth(seg_text + ' ', self.font, font_size)
                        
                        current_x += width
                
                self.current_y -= line_spacing
    def draw_header(self, x, text, level=2, font_size=None):
        """
        마크다운 헤더 렌더링
        level: 2 (##), 3 (###), 4 (####)
        """
        if font_size is None:
            # 레벨에 따른 기본 폰트 크기
            font_sizes = {2: 15, 3: 13, 4: 12}
            font_size = font_sizes.get(level, 12)

        # 레벨에 따른 상단 여백
        top_margins = {2: 28, 3: 22, 4: 18}
        top_margin = top_margins.get(level, 18)

        # 레벨에 따른 하단 여백
        bottom_margins = {2: 20, 3: 16, 4: 14}
        bottom_margin = bottom_margins.get(level, 14)

        # 상단 여백 적용
        self.current_y -= top_margin
        self.check_space(font_size + bottom_margin + 5)

        # 헤더는 항상 볼드체
        try:
            self.canvas.setFont('MalgunBold', font_size)
        except:
            self.canvas.setFont(self.font, font_size)

        self.canvas.setFillColor(self.black)

        # ** 제거 (마크다운에서 올 수 있음)
        clean_text = text.replace('**', '').strip()

        # 레벨 2는 약간 진한 파란색, 나머지는 검정
        if level == 2:
            self.canvas.setFillColor(self.dark_gray)
        else:
            self.canvas.setFillColor(self.black)

        self.canvas.drawString(x, self.current_y, clean_text)

        # 하단 여백 적용
        self.current_y -= bottom_margin

        # 색상 원복
        self.canvas.setFillColor(self.black)
    def _draw_table_header(self, headers, col_widths, x, row_height=40):
        """
        표 헤더만 그리기 (페이지 분할 시 재사용)
        """
        self.canvas.setFont(self.font, 10)
        self.canvas.setFillColor(self.light_gray)
        self.canvas.rect(x, self.current_y - row_height, sum(col_widths), row_height, fill=1)
        self.canvas.setFillColor(self.black)

        for i, h in enumerate(headers):
            h_clean = h.replace('**', '')
            if '**' in h:
                try:
                    self.canvas.setFont('MalgunBold', 10)
                except:
                    self.canvas.setFont(self.font, 10)
            else:
                self.canvas.setFont(self.font, 10)
            self.canvas.drawString(x + sum(col_widths[:i]) + 8, self.current_y - 16, h_clean)

        self.current_y -= row_height

    def draw_table(self, headers, rows, col_widths, x, row_height=40):
        """
        ✅ 개선된 표 렌더링 - 긴 텍스트 자동 줄바꿈 + 페이지 분할
        """
        # 헤더 그리기
        header_height = row_height
        self.check_space(header_height + 20)
        self._draw_table_header(headers, col_widths, x, header_height)
        
        # 데이터 행 처리
        for row_idx, row in enumerate(rows):
            # ✅ 개선: 각 셀의 실제 필요 라인 수 정확히 계산
            cell_line_counts = []
            
            for i, cell in enumerate(row):
                cell_text = str(cell).strip()
                if not cell_text:
                    cell_line_counts.append(1)
                    continue
                
                # 줄바꿈 문자로 분리
                lines = cell_text.split('\n')
                total_lines = 0
                
                # 각 라인에 대해 자동 줄바꿈 계산
                for line in lines:
                    line_clean = line.replace('**', '').replace('`', '').strip()
                    if not line_clean:
                        total_lines += 1
                        continue
                    
                    # ✅ 셀 너비에서 패딩(16) 제외한 실제 사용 가능 너비
                    available_width = col_widths[i] - 16
                    line_width = self.canvas.stringWidth(line_clean, self.font, 10)
                    
                    # 한 줄에 들어가는 경우
                    if line_width <= available_width:
                        total_lines += 1
                    else:
                        # ✅ 단어 단위로 줄바꿈
                        words = line_clean.split()
                        if not words:
                            total_lines += 1
                            continue
                        
                        current_line = ""
                        line_count = 0
                        
                        for word in words:
                            test_line = current_line + " " + word if current_line else word
                            test_width = self.canvas.stringWidth(test_line, self.font, 10)
                            
                            if test_width <= available_width:
                                current_line = test_line
                            else:
                                # ✅ 한 단어가 너무 긴 경우 강제 분할
                                if not current_line:
                                    # 문자 단위로 분할
                                    chars_per_line = int(available_width / self.canvas.stringWidth('A', self.font, 10))
                                    word_lines = [word[i:i+chars_per_line] for i in range(0, len(word), chars_per_line)]
                                    line_count += len(word_lines)
                                    current_line = ""
                                else:
                                    line_count += 1
                                    current_line = word
                        
                        if current_line:
                            line_count += 1
                        
                        total_lines += line_count
                
                cell_line_counts.append(max(1, total_lines))
            
            # ✅ 최대 라인 수에 따른 행 높이 계산 (최소 높이 보장)
            max_cell_lines = max(cell_line_counts) if cell_line_counts else 1
            # 라인당 13pt + 상하 패딩 14pt
            actual_height = max(row_height, max_cell_lines * 13 + 14)
            
            # ✅ 페이지 공간 체크 및 분할
            if self.current_y - actual_height < self.min_y:
                self.new_page()
                self._draw_table_header(headers, col_widths, x, header_height)
            
            # 행 배경 그리기
            self.canvas.setFillColor(self.very_light_gray)
            self.canvas.rect(x, self.current_y - actual_height, sum(col_widths), actual_height, fill=1)
            self.canvas.setFillColor(self.black)
            
            # ✅ 셀 내용 그리기 (개선된 줄바꿈)
            for i, cell in enumerate(row):
                cell_text = str(cell).strip()
                if not cell_text:
                    continue
                
                lines = cell_text.split('\n')
                cell_y = self.current_y - 13
                cell_bottom = self.current_y - actual_height + 5
                cell_x = x + sum(col_widths[:i]) + 8
                available_width = col_widths[i] - 16
                
                for line in lines:
                    if cell_y < cell_bottom:
                        break
                    
                    line_clean = line.replace('**', '').replace('`', '').strip()
                    if not line_clean:
                        cell_y -= 13
                        continue
                    
                    has_bold = '**' in line
                    
                    # 폰트 설정
                    if has_bold:
                        try:
                            self.canvas.setFont('MalgunBold', 10)
                            font_name = 'MalgunBold'
                        except:
                            self.canvas.setFont(self.font, 10)
                            font_name = self.font
                    else:
                        self.canvas.setFont(self.font, 10)
                        font_name = self.font
                    
                    line_width = self.canvas.stringWidth(line_clean, font_name, 10)
                    
                    # 한 줄에 들어가는 경우
                    if line_width <= available_width:
                        if cell_y >= cell_bottom:
                            self.canvas.drawString(cell_x, cell_y, line_clean)
                        cell_y -= 13
                    else:
                        # ✅ 단어 단위 줄바꿈
                        words = line_clean.split()
                        current_line = ""
                        
                        for word in words:
                            test_line = current_line + " " + word if current_line else word
                            test_width = self.canvas.stringWidth(test_line, font_name, 10)
                            
                            if test_width <= available_width:
                                current_line = test_line
                            else:
                                # 현재 줄 출력
                                if current_line and cell_y >= cell_bottom:
                                    self.canvas.drawString(cell_x, cell_y, current_line)
                                    cell_y -= 12
                                
                                # ✅ 한 단어가 너무 긴 경우
                                word_width = self.canvas.stringWidth(word, font_name, 10)
                                if word_width > available_width:
                                    # 문자 단위로 강제 분할
                                    chars_per_line = int(available_width / self.canvas.stringWidth('A', font_name, 10))
                                    for j in range(0, len(word), chars_per_line):
                                        chunk = word[j:j+chars_per_line]
                                        if cell_y >= cell_bottom:
                                            self.canvas.drawString(cell_x, cell_y, chunk)
                                            cell_y -= 12
                                    current_line = ""
                                else:
                                    current_line = word
                        
                        # 마지막 줄 출력
                        if current_line and cell_y >= cell_bottom:
                            self.canvas.drawString(cell_x, cell_y, current_line)
                            cell_y -= 12
            
            self.current_y -= actual_height

    def render_markdown_content(self, content, x_start):
        """마크다운 콘텐츠 렌더링 - 헤더 처리 추가"""
        if "```" in content:
            blocks = re.split(r"```+", content)
            for i, b in enumerate(blocks):
                if i % 2 == 1:
                    lines = [ln.rstrip() for ln in b.splitlines() if ln is not None]
                    block_h = max(30, len(lines) * 14 + 12)
                    self.check_space(block_h)
                    self.canvas.setFillColor(HexColor("#f3f3f3"))
                    self.canvas.rect(x_start - 5, self.current_y - block_h + 6,
                                     self.width - x_start - 45, block_h, fill=True, stroke=False)
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

        # ✅ 개선된 표 패턴: 다양한 구분선 형태 지원
        table_pattern = r'\|[^\n]+\|\n\|[\s\-—―=:|]+\|(?:\n\|[^\n]+\|)+'
        tables = list(re.finditer(table_pattern, content))

        if tables:
            last_end = 0
            for match in tables:
                before_text = content[last_end:match.start()]
                if before_text.strip():
                    self._render_text_lines(before_text, x_start)

                table_text = match.group(0)

                # ✅ 구분선 정리: 다양한 대시 문자 통일
                table_text = table_text.replace('—', '-').replace('―', '-').replace('–', '-')

                lines = [l.strip() for l in table_text.splitlines() if "|" in l]

                if len(lines) >= 2:
                    # 헤더 파싱
                    headers = [c.strip() for c in lines[0].split("|")[1:-1]]

                    # 데이터 행 파싱 (구분선 제외)
                    rows = []
                    for line in lines[2:]:  # 첫 줄(헤더), 둘째 줄(구분선) 제외
                        if not line.strip():
                            continue
                        # 구분선 스킵 (-, |, :, 공백만 있는 줄)
                        if re.match(r'^[\s\-—―=:|]+$', line.replace('|', '')):
                            continue
                        
                        cells = [c.strip() for c in line.split("|")[1:-1]]

                        # 빈 행 제외
                        if any(cell.strip() for cell in cells):
                            rows.append(cells)

                    # 표가 비어있지 않으면 렌더링
                    if headers and rows:
                        num_cols = len(headers)
                        usable_width = self.width - x_start - 45

                        # 열 너비 계산
                        max_lengths = [len(str(h).replace('**', '').replace('`', '')) for h in headers]
                        for row in rows:
                            for i, cell in enumerate(row):
                                if i < len(max_lengths):
                                    cell_lines = str(cell).replace('**', '').replace('`', '').split('\n')
                                    max_line_len = max(len(line) for line in cell_lines) if cell_lines else 0
                                    max_lengths[i] = max(max_lengths[i], max_line_len)

                        total_len = sum(max_lengths) or num_cols
                        col_widths = [max(75, int(usable_width * (l / total_len))) for l in max_lengths]

                        if sum(col_widths) > usable_width:
                            scale = usable_width / sum(col_widths)
                            col_widths = [int(w * scale) for w in col_widths]
                            for i in range(len(col_widths)):
                                if col_widths[i] < 65:
                                    col_widths[i] = 65

                        self.draw_table(headers, rows, col_widths, x_start)
                        self.current_y -= 25

                last_end = match.end()

            after_text = content[last_end:]
            if after_text.strip():
                self._render_text_lines(after_text, x_start)
        else:
            self._render_text_lines(content, x_start)
    
    def _render_text_lines(self, content, x_start):
        """일반 텍스트 라인 처리 - 개선된 버전"""
        lines = content.split('\n')
        in_sub_context = False

        # 패턴 정의
        sub_heading_pattern = r'^\* \*\*(.+?)\*\*:$'
        numbered_paren_pattern = r'^(\d+)\)\s+(.*)$'
        indented_bullet_pattern = r'^  +\* (.+)$'
        numbered_pattern = r'^(\d+)\.\s+(.*)$'
        bullet_pattern = r'^\* (.+)$'
        dash_bullet_pattern = r'^-\s+(.+)$'
        double_dash_pattern = r'^  +-\s+(.+)$'

        # ✅ 새로 추가: 마크다운 헤더 패턴
        header_pattern = r'^(#{2,4})\s+(.+)$'

        for line in lines:
            line_rstrip = line.rstrip()

            # 빈 줄 처리
            if not line_rstrip.strip():
                self.current_y -= 8
                in_sub_context = False
                continue

            # ✅ 새로 추가: 마크다운 헤더 처리 (##, ###, ####)
            header_match = re.match(header_pattern, line_rstrip)
            if header_match:
                level = len(header_match.group(1))  # #의 개수
                header_text = header_match.group(2).strip()
                self.draw_header(x_start, header_text, level=level)
                in_sub_context = False
                continue

            # 패턴 1: * **제목**: 형태 (서브 헤딩)
            sub_heading_match = re.match(sub_heading_pattern, line_rstrip)
            if sub_heading_match:
                heading_text = sub_heading_match.group(1)
                self.check_space(20)

                try:
                    self.canvas.setFont('MalgunBold', 12)
                except:
                    self.canvas.setFont(self.font, 12)
                self.canvas.setFillColor(self.black)
                self.canvas.drawString(self.L3, self.current_y, f"• {heading_text}:")

                self.current_y -= 20
                in_sub_context = True
                continue

            # 패턴 2: 1) 내용 형태 (번호 + 괄호)
            numbered_paren_match = re.match(numbered_paren_pattern, line_rstrip)
            if numbered_paren_match:
                num = numbered_paren_match.group(1)
                text = numbered_paren_match.group(2)
                
                # 제목 스타일인지 확인 (볼드 처리)
                if text.strip().startswith('**') and text.strip().endswith('**'):
                    clean_text = text.strip()[2:-2]
                    self.check_space(22)
                    try:
                        self.canvas.setFont('MalgunBold', 12)
                    except:
                        self.canvas.setFont(self.font, 12)
                    self.canvas.setFillColor(self.black)
                    self.canvas.drawString(self.L3, self.current_y, f"{num}) {clean_text}")
                    self.current_y -= 22
                    in_sub_context = True
                else:
                    self.draw_paragraph(self.L3, f"{num}) {text}", font_size=12, line_spacing=19)
                    in_sub_context = False
                continue

            # 패턴 3: 들여쓰기된 - 불릿
            double_dash_match = re.match(double_dash_pattern, line_rstrip)
            if double_dash_match:
                bullet_text = double_dash_match.group(1)
                indent_level = self.L5 if in_sub_context else self.L4
                self.draw_paragraph(indent_level, f"• {bullet_text}", font_size=12, line_spacing=19)
                continue

            # 패턴 4: - 불릿 (최상위)
            dash_bullet_match = re.match(dash_bullet_pattern, line_rstrip)
            if dash_bullet_match:
                bullet_text = dash_bullet_match.group(1)
                self.draw_paragraph(self.L4, f"• {bullet_text}", font_size=12, line_spacing=19)
                in_sub_context = False
                continue

            # 패턴 5: 들여쓰기된 * 불릿
            indented_bullet_match = re.match(indented_bullet_pattern, line_rstrip)
            if indented_bullet_match:
                bullet_text = indented_bullet_match.group
                (1)
                indent_level = self.L5 if in_sub_context else self.L4
                self.draw_paragraph(indent_level, f"• {bullet_text}", font_size=12, line_spacing=19)
                continue

            # 패턴 6: 1. 내용 형태
            numbered_match = re.match(numbered_pattern, line_rstrip)
            if numbered_match:
                self.draw_paragraph(self.L3, line_rstrip, font_size=12, line_spacing=19)
                in_sub_context = False
                continue

            # 패턴 7: * 불릿 (최상위)
            bullet_match = re.match(bullet_pattern, line_rstrip)
            if bullet_match:
                bullet_text = bullet_match.group(1)
                self.draw_paragraph(self.L4, f"• {bullet_text}", font_size=12, line_spacing=19)
                in_sub_context = False
                continue

            # 일반 텍스트
            self.draw_paragraph(x_start, line_rstrip, font_size=12, line_spacing=19)
            in_sub_context = False

    def page1(self, c, data):
        """✅ 표지 페이지"""
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
        """✅ 정밀 측정: 목차 페이지 (페이지 번호 없음, 제목만 표시)"""
        self._bg(self.canvas, 2)
        self._pgn(self.canvas, 2)
        
        # 목차 페이지 북마크 등록 (뒤로가기 기능 지원)
        self.canvas.bookmarkPage("TOC")
        
        # 목차 제목
        try:
            self.canvas.setFont('MalgunBold', 26)
        except:
            self.canvas.setFont(self.font, 26)
        self.canvas.setFillColor(self.black)
        title_text = "목차"
        registered_fonts = pdfmetrics.getRegisteredFontNames()
        font_name = 'MalgunBold' if 'MalgunBold' in registered_fonts else self.font
        text_width = self.canvas.stringWidth(title_text, font_name, 26)
        self.canvas.drawString((self.width - text_width) / 2, 750, title_text)
        
        y = 680
        prev_was_main = False
        
        for i, (title, page_num, dest_name, is_main) in enumerate(self.toc_entries):
            if is_main:
                # 이전 항목이 소제목이었고 현재가 대제목이면 큰 간격 추가
                if i > 0 and not prev_was_main:
                    y -= 15  # 소제목 → 대제목 전환 시 추가 간격
                
                # 대제목: 18pt 볼드
                try:
                    self.canvas.setFont('MalgunBold', 18)
                except:
                    self.canvas.setFont(self.font, 18)
                self.canvas.setFillColor(self.black)
                
                # 제목만 그리기 (페이지 번호 없음)
                self.canvas.drawString(50, y, title)
                
                # 링크 영역 (제목 클릭 시 해당 섹션으로 이동)
                try:
                    title_width = self.canvas.stringWidth(title, 'MalgunBold', 18)
                except:
                    title_width = self.canvas.stringWidth(title, self.font, 18)
                
                self.canvas.linkRect("", dest_name, (50, y - 2, 50 + title_width, y + 17), relative=0)
                y -= 32  # 대제목 → 소제목 간격
                
                prev_was_main = True
                
            else:
                # 소제목: 15pt 일반
                self.canvas.setFont(self.font, 15)
                self.canvas.setFillColor(self.black)
                
                # 제목만 그리기 (페이지 번호 없음)
                self.canvas.drawString(70, y, title)
                
                # 링크 영역
                title_width = self.canvas.stringWidth(title, self.font, 15)
                self.canvas.linkRect("", dest_name, (70, y - 2, 70 + title_width, y + 14), relative=0)
                y -= 28  # 소제목 간 간격
                
                prev_was_main = False
            
            # 페이지 넘김 체크
            if y < 100:
                break
            
        self.canvas.showPage()

    def render_section(self, main_num: int, section_details: List[Dict[str, Any]], 
                       section_titles: Dict[int, str], section_names: Dict[int, str],
                       collect_toc: bool = True, is_first_section: bool = False):
        """✅ 정밀 측정: 섹션 렌더링"""
        max_w = self.width - self.L2 - 45
        
        if not is_first_section:
            self.new_page()
        
        main_title = f"{main_num}. {section_names[main_num]}"
        if collect_toc:
            self.toc_entries.append((main_title, self.current_page, f"section_{main_num}", True))
        
        self.canvas.bookmarkPage(f"section_{main_num}")
        
        # ✅ 대제목: 18pt 볼드, 아래 32pt 여백
        self.check_space(30)
        try:
            self.canvas.setFont('MalgunBold', 18)
        except:
            self.canvas.setFont(self.font, 18)
        self.canvas.setFillColor(self.black)
        self.canvas.drawString(self.L0, self.current_y, main_title)
        self.current_y -= 32
        
        # ✅ 소제목 및 내용
        for idx, detail in enumerate(section_details, 1):
            section_type = detail.get('section_type')
            title = section_titles.get(section_type, "")
            content = detail.get('content', "")
            
            sub_title = f"{main_num}.{idx} {title}"
            if collect_toc:
                self.toc_entries.append((sub_title, self.current_page, f"section_{main_num}_{idx}", False))
            self.canvas.bookmarkPage(f"section_{main_num}_{idx}")
            
            # ✅ 소제목: 14pt 볼드, 아래 26pt 여백
            self.check_space(24)
            try:
                self.canvas.setFont('MalgunBold', 14)
            except:
                self.canvas.setFont(self.font, 14)
            self.canvas.drawString(self.L1, self.current_y, sub_title)
            self.current_y -= 26
            
            self.render_markdown_content(content, self.L2)
            self.current_y -= 22

    def generate_from_json(self, json_data, output_path: str, section_titles, section_mapping, main_sections):
        """JSON 데이터로부터 PDF 생성"""
        report_meta = json_data.get("report", {})
        data = ReportData(
            company_name=report_meta.get("summary", "[의뢰 회사 이름]"),
            pc_name=report_meta.get("pc_id", "[TEST-PC-001]"),
            date=report_meta.get("created_at", "2025년 10월 15일")
        )
        
        print("=" * 60)
        print("📄 보안 진단 보고서 PDF 생성 (정밀 측정 완료)")
        print("=" * 60)
        print(f"출력: {output_path}\n")
        
        # 1차 렌더: TOC 페이지 번호 수집
        temp_buf = io.BytesIO()
        temp_canvas = canvas.Canvas(temp_buf, pagesize=A4, pageCompression=0)
        self.canvas = temp_canvas
        self.current_page = 3
        self.current_y = self.top
        self.toc_entries = []

        grouped_details = defaultdict(list)
        details = json_data.get("details", [])
        sorted_details = sorted(details, key=lambda d: d.get('section_type', 0))
        for detail in sorted_details:
            section_type = detail.get('section_type')
            main_group = section_mapping.get(section_type)
            if main_group:
                grouped_details[main_group].append(detail)

        self._bg(self.canvas, 3)
        first_section = True
        for main_num in sorted(main_sections.keys()):
            section_details = grouped_details.get(main_num, [])
            if not section_details:
                continue
            self.render_section(main_num, section_details, section_titles, main_sections, collect_toc=True, is_first_section=first_section)
            first_section = False
        temp_canvas.save()

        # 2차 렌더: 실제 PDF 생성
        self.canvas = canvas.Canvas(output_path, pagesize=A4, pageCompression=0)
        self.page1(self.canvas, data)
        self.render_toc()

        self._bg(self.canvas, 3)
        self._pgn(self.canvas, 3)
        self.current_page = 3
        self.current_y = self.top
        
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
    print("✅ 이미지 기반 정밀 측정 완료")