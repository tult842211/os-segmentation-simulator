"""Build the printable Vietnamese report (optional dependency: reportlab).

Run from any directory: python scripts/build_report.py
The source remains report/report.md; explicit page breaks are respected.
"""
from __future__ import annotations

import csv
import html
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether, Preformatted,
)

ROOT = Path(__file__).resolve().parents[1]
INK = colors.HexColor('#19344c')
TEAL = colors.HexColor('#087f83')
GRAY = colors.HexColor('#526679')


def register_fonts() -> None:
    candidates = [
        (Path('C:/Windows/Fonts/segoeui.ttf'), Path('C:/Windows/Fonts/segoeuib.ttf')),
        (Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
         Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')),
    ]
    for regular, bold in candidates:
        if regular.is_file() and bold.is_file():
            pdfmetrics.registerFont(TTFont('Body', str(regular)))
            pdfmetrics.registerFont(TTFont('BodyBold', str(bold)))
            pdfmetrics.registerFontFamily('Body', normal='Body', bold='BodyBold',
                                          italic='Body', boldItalic='BodyBold')
            return
    raise SystemExit('Install Segoe UI or DejaVu Sans for Vietnamese PDF text.')


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                  lambda m: '<link href="' + m[2] + '" color="#087f83">' + m[1] + '</link>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'<i>\1</i>', text)
    text = re.sub(r'`([^`]+)`', r'<font color="#087f83">\1</font>', text)
    return text


def measured_results() -> str:
    benchmark = ROOT / 'output/benchmark.csv'
    verification = ROOT / 'output/verification.csv'
    if not benchmark.exists() or not verification.exists():
        return ('Chưa có dữ liệu đo. Chạy scripts/verify.py và scripts/benchmark.py '
                'rồi tạo lại báo cáo trước khi nộp.')
    # Reuse the concise measured summary authored by the measurement script.
    snippet = ROOT / 'output/report-metrics.md'
    if snippet.exists():
        measured = snippet.read_text(encoding='utf-8-sig')
        measured = measured.replace('## ', '### ')
        measured = measured.replace('# Số liệu thực nghiệm dùng trong báo cáo',
                                    '## 8.4. Kết quả thực nghiệm')
        return '[PAGEBREAK]\n' + measured
    return ('Số liệu thực tế và môi trường đo được lưu trong output/benchmark.csv, '
            'output/benchmark-summary.md và output/system-info.json. Bảng '
            'output/verification.csv ghi từng giá trị kỳ vọng và thực tế.')


def build() -> Path:
    register_fonts()
    styles = {
        'body': ParagraphStyle('Body', fontName='Body', fontSize=10.2, leading=15,
                               textColor=INK, spaceAfter=7),
        'h1': ParagraphStyle('Heading1', fontName='BodyBold', fontSize=19, leading=25,
                             textColor=INK, spaceAfter=15, keepWithNext=True),
        'h2': ParagraphStyle('Heading2', fontName='BodyBold', fontSize=14, leading=19,
                             textColor=INK, spaceBefore=10, spaceAfter=9, keepWithNext=True),
        'h3': ParagraphStyle('Heading3', fontName='BodyBold', fontSize=11, leading=16,
                             textColor=TEAL, spaceBefore=8, spaceAfter=6, keepWithNext=True),
        'cell': ParagraphStyle('Cell', fontName='Body', fontSize=9, leading=13,
                               textColor=INK),
        'code': ParagraphStyle('Code', fontName='Body', fontSize=8.5, leading=12,
                               textColor=INK, backColor=colors.HexColor('#eef4f6'),
                               borderPadding=8, spaceBefore=5, spaceAfter=9),
    }
    styles['list'] = ParagraphStyle('ListItem', parent=styles['body'], spaceAfter=2)
    source = (ROOT / 'report/report.md').read_text(encoding='utf-8-sig')
    source = source.replace('<!-- MEASURED_RESULTS -->', measured_results())
    source = source.replace('<div class="page-break"></div>', '\n[PAGEBREAK]\n')
    source = source.replace('<div style="page-break-after: always;"></div>', '\n[PAGEBREAK]\n')
    lines = source.splitlines()
    story = []
    index = 0
    width = A4[0] - 92

    def add_paragraph(text: str, style: str = 'body') -> None:
        story.append(Paragraph(inline(text), styles[style]))

    while index < len(lines):
        line = lines[index].strip()
        index += 1
        if not line:
            continue
        if line == '[PAGEBREAK]':
            story.append(PageBreak())
            continue
        if line.startswith('<!--'):
            continue
        if line.startswith('```'):
            block = []
            while index < len(lines) and not lines[index].strip().startswith('```'):
                block.append(lines[index])
                index += 1
            index += 1
            story.append(Preformatted('\n'.join(block), styles['code'], maxLineLength=87))
            continue
        if line.startswith('|'):
            rows = [line]
            while index < len(lines) and lines[index].strip().startswith('|'):
                rows.append(lines[index].strip())
                index += 1
            cells = [[c.strip() for c in row.strip('|').split('|')] for row in rows
                     if not re.fullmatch(r'[| :\-]+', row)]
            count = len(cells[0])
            weights = [max(8, min(50, max(len(row[col]) if col < len(row) else 0 for row in cells)))
                       for col in range(count)]
            widths = [width * w / sum(weights) for w in weights]
            table_data = [[Paragraph(inline(value), styles['cell']) for value in row] for row in cells]
            table = Table(table_data, colWidths=widths, repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dceef0')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f3f6f8')]),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 7),
                ('RIGHTPADDING', (0,0), (-1,-1), 7),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LINEBELOW', (0,0), (-1,0), 0.6, TEAL),
            ]))
            story.extend([table, Spacer(1,9)])
            continue
        heading = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading:
            add_paragraph(heading[2], 'h' + str(min(len(heading[1]),3)))
            continue
        if line in ('---', '***'):
            story.append(Spacer(1,10))
            continue
        bullet = re.match(r'^[-*]\s+(.*)', line)
        if bullet:
            add_paragraph('• ' + bullet[1])
            continue
        if re.match(r'^\d+\.\s+', line):
            add_paragraph(line, 'list')
            continue
        paragraph = [line]
        while index < len(lines):
            nxt = lines[index].strip()
            if not nxt or nxt.startswith(('#','|','```','<!--','[PAGEBREAK]','- ','* ')) or re.match(r'^\d+\.\s+', nxt):
                break
            paragraph.append(nxt)
            index += 1
        add_paragraph(' '.join(paragraph))

    output = ROOT / 'report/OS_MEM_12_Report.pdf'
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Body', 8)
        canvas.setFillColor(GRAY)
        canvas.drawString(46, 27, 'OS_MEM_12  |  Segmentation và địa chỉ logic')
        canvas.drawRightString(A4[0] - 46, 27, str(doc.page))
        canvas.restoreState()
    document = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=46, rightMargin=46,
                                  topMargin=42, bottomMargin=45, title='OS_MEM_12 Segmentation và địa chỉ logic',
                                  author='OS_MEM_12 project')
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return output


if __name__ == '__main__':
    print(build())
