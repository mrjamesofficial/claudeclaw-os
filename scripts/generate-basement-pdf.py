#!/usr/bin/env python3
"""
ClaudeClaw AI Army — Basement PDF Generator

Renders a markdown file to a brand-neutral PDF suitable for OS-level / foundational
documents. No external brand references. No logo. ClaudeClaw AI Army identity only.

Usage:
    generate-basement-pdf.py --input FILE.md --output OUT.pdf [--version "..."]
"""

import argparse
import os
import re
import sys

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
except ImportError:
    print("ERROR: reportlab not installed. Run: python3 -m pip install reportlab --break-system-packages")
    sys.exit(1)


# Brand-neutral ClaudeClaw AI Army palette — sober, constitutional, no commerce signals
INK        = colors.HexColor('#1A1A1A')
ACCENT     = colors.HexColor('#1A365D')   # Dark blue — gravitas
GRAY_DARK  = colors.HexColor('#333333')
GRAY_MID   = colors.HexColor('#666666')
GRAY_LIGHT = colors.HexColor('#999999')


def build_styles():
    return {
        'title': ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=20,
                                textColor=INK, leading=24, spaceAfter=4, alignment=TA_LEFT),
        'version': ParagraphStyle('Version', fontName='Helvetica-Bold', fontSize=10,
                                  textColor=ACCENT, leading=13, spaceAfter=12, alignment=TA_LEFT),
        'h2': ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=14,
                             textColor=ACCENT, leading=18, spaceBefore=14, spaceAfter=6),
        'h3': ParagraphStyle('H3', fontName='Helvetica-Bold', fontSize=12,
                             textColor=GRAY_DARK, leading=15, spaceBefore=10, spaceAfter=4),
        'body': ParagraphStyle('Body', fontName='Helvetica', fontSize=10.5,
                               textColor=INK, leading=15, spaceAfter=6),
        'quote': ParagraphStyle('Quote', fontName='Helvetica-Oblique', fontSize=10,
                                textColor=GRAY_DARK, leading=14, leftIndent=18,
                                rightIndent=8, spaceAfter=8),
        'bullet': ParagraphStyle('Bullet', fontName='Helvetica', fontSize=10.5,
                                 textColor=INK, leading=14, leftIndent=18,
                                 bulletIndent=0, spaceAfter=4),
        'footer': ParagraphStyle('Footer', fontName='Helvetica', fontSize=8,
                                 textColor=GRAY_LIGHT, alignment=TA_CENTER),
    }


def inline_md_to_html(text):
    """Convert markdown inline syntax to reportlab-compatible HTML."""
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'`([^`]+)`', r'<font face="Courier">\1</font>', text)
    return text


def parse_markdown(md_text):
    """Parse markdown into a list of (type, content) blocks."""
    lines = md_text.split('\n')
    blocks = []
    quote_buffer = []
    paragraph_buffer = []

    def flush_paragraph():
        if paragraph_buffer:
            blocks.append(('p', ' '.join(paragraph_buffer)))
            paragraph_buffer.clear()

    def flush_quote():
        if not quote_buffer:
            return
        current = []
        for ln in quote_buffer:
            if ln.strip():
                current.append(ln)
            elif current:
                blocks.append(('quote', ' '.join(current)))
                current = []
        if current:
            blocks.append(('quote', ' '.join(current)))
        quote_buffer.clear()

    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            flush_paragraph()
            flush_quote()
            continue

        if stripped.startswith('# '):
            flush_paragraph(); flush_quote()
            blocks.append(('h1', stripped[2:].strip()))
        elif stripped.startswith('## '):
            flush_paragraph(); flush_quote()
            blocks.append(('h2', stripped[3:].strip()))
        elif stripped.startswith('### '):
            flush_paragraph(); flush_quote()
            blocks.append(('h3', stripped[4:].strip()))
        elif stripped.startswith('> '):
            flush_paragraph()
            quote_buffer.append(stripped[2:].strip())
        elif stripped == '>':
            flush_paragraph()
            quote_buffer.append('')
        elif stripped.startswith('- ') or stripped.startswith('* '):
            flush_paragraph(); flush_quote()
            blocks.append(('bullet', stripped[2:].strip()))
        elif stripped == '---':
            flush_paragraph(); flush_quote()
            blocks.append(('hr', None))
        else:
            flush_quote()
            paragraph_buffer.append(stripped)

    flush_paragraph()
    flush_quote()
    return blocks


def build_pdf(input_path, output_path, version=None):
    with open(input_path, 'r') as f:
        md = f.read()

    blocks = parse_markdown(md)
    styles = build_styles()

    title = 'Untitled Document'
    for typ, content in blocks:
        if typ == 'h1':
            title = content
            break

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.95 * inch,
        rightMargin=0.95 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.95 * inch,
        title=title,
        author='James (Commanding Authority)',
        subject='ClaudeClaw AI Army — Foundational Doctrine',
        creator='ClaudeClaw AI Army',
    )

    story = []
    h1_seen = False

    for typ, content in blocks:
        if typ == 'h1':
            if h1_seen:
                continue
            h1_seen = True
            story.append(Paragraph(inline_md_to_html(content), styles['title']))
            if version:
                story.append(Paragraph(version, styles['version']))
            story.append(HRFlowable(width='100%', thickness=1.5, color=ACCENT, spaceAfter=10))
        elif typ == 'h2':
            story.append(Paragraph(inline_md_to_html(content), styles['h2']))
        elif typ == 'h3':
            story.append(Paragraph(inline_md_to_html(content), styles['h3']))
        elif typ == 'p':
            story.append(Paragraph(inline_md_to_html(content), styles['body']))
        elif typ == 'quote':
            story.append(Paragraph(inline_md_to_html(content), styles['quote']))
        elif typ == 'bullet':
            story.append(Paragraph('• ' + inline_md_to_html(content), styles['bullet']))
        elif typ == 'hr':
            story.append(Spacer(1, 0.05 * inch))
            story.append(HRFlowable(width='100%', thickness=0.5, color=GRAY_LIGHT, spaceAfter=10))

    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width='100%', thickness=0.5, color=GRAY_LIGHT, spaceAfter=4))
    story.append(Paragraph('ClaudeClaw AI Army  |  Foundational Doctrine', styles['footer']))

    doc.build(story)
    return output_path


def main():
    parser = argparse.ArgumentParser(description='ClaudeClaw AI Army — Basement PDF Generator')
    parser.add_argument('--input', required=True, help='Input markdown file')
    parser.add_argument('--output', required=True, help='Output PDF path')
    parser.add_argument('--version', default='', help='Optional version line below title')
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f'ERROR: input file not found: {args.input}')
        sys.exit(1)

    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    path = build_pdf(args.input, args.output, version=args.version or None)
    print(f'PDF written: {path}')


if __name__ == '__main__':
    main()
