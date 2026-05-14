#!/usr/bin/env python3
"""
Toys For Trucks® PDF Generator
Generates branded PDFs compatible with desktop and mobile devices.
"""

import argparse
import json
import os
import sys
import tempfile
import urllib.request
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
        Table, TableStyle, KeepTogether, Image
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
except ImportError:
    print("ERROR: reportlab not installed. Run: python3 -m pip install reportlab --break-system-packages")
    sys.exit(1)

# PLACEHOLDER logo URL — single source of truth until the official production-quality
# TFT® logo file is formally provided and approved by James. Do NOT swap this for a
# local path or hardcoded binary. When the official file is approved, replace this URL.
LOGO_PLACEHOLDER_URL = 'https://www.toysfortrucksofficial.com/sites/default/files/logoplain.png'


def fetch_logo(width=1.0 * inch, height=0.6 * inch):
    """Fetch logo from placeholder URL. Returns Image flowable or None on failure."""
    try:
        with urllib.request.urlopen(LOGO_PLACEHOLDER_URL, timeout=5) as resp:
            data = resp.read()
        tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        tmp.write(data)
        tmp.close()
        return Image(tmp.name, width=width, height=height, kind='proportional')
    except Exception:
        return None

# ── Brand Colors ──────────────────────────────────────────────────────────────
TFT_BLACK      = colors.HexColor('#1A1A1A')
TFT_ORANGE     = colors.HexColor('#E85D00')
TFT_WHITE      = colors.white
TFT_LIGHT_GRAY = colors.HexColor('#F5F5F5')
TFT_MID_GRAY   = colors.HexColor('#888888')
TFT_DARK_GRAY  = colors.HexColor('#333333')


def build_styles():
    base = getSampleStyleSheet()

    styles = {
        'doc_title': ParagraphStyle(
            'DocTitle',
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=TFT_BLACK,
            spaceAfter=6,
            leading=26,
            alignment=TA_LEFT,
        ),
        'doc_subtitle': ParagraphStyle(
            'DocSubtitle',
            fontName='Helvetica',
            fontSize=12,
            textColor=TFT_MID_GRAY,
            spaceAfter=4,
            alignment=TA_LEFT,
        ),
        'section_heading': ParagraphStyle(
            'SectionHeading',
            fontName='Helvetica-Bold',
            fontSize=13,
            textColor=TFT_ORANGE,
            spaceBefore=14,
            spaceAfter=6,
            leading=16,
        ),
        'body': ParagraphStyle(
            'Body',
            fontName='Helvetica',
            fontSize=10,
            textColor=TFT_DARK_GRAY,
            spaceAfter=4,
            leading=14,
        ),
        'bullet': ParagraphStyle(
            'Bullet',
            fontName='Helvetica',
            fontSize=10,
            textColor=TFT_DARK_GRAY,
            spaceAfter=4,
            leading=14,
            leftIndent=16,
            bulletIndent=0,
        ),
        'tagline': ParagraphStyle(
            'Tagline',
            fontName='Helvetica-BoldOblique',
            fontSize=10,
            textColor=TFT_ORANGE,
            alignment=TA_CENTER,
            spaceBefore=4,
        ),
        'footer_text': ParagraphStyle(
            'FooterText',
            fontName='Helvetica',
            fontSize=8,
            textColor=TFT_MID_GRAY,
            alignment=TA_CENTER,
        ),
        'meta': ParagraphStyle(
            'Meta',
            fontName='Helvetica',
            fontSize=9,
            textColor=TFT_MID_GRAY,
            spaceAfter=2,
        ),
    }
    return styles


def build_header_table(title, subtitle, styles):
    """Logo (fetched from placeholder URL) + title block side by side."""
    logo_img = fetch_logo(width=1.0 * inch, height=0.6 * inch)

    if logo_img:
        logo_cell = logo_img
    else:
        # Text fallback when logo URL is unreachable
        fallback_data = [[Paragraph('<b>TFT®</b>', ParagraphStyle(
            'LogoText',
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=TFT_WHITE,
            alignment=TA_CENTER,
        ))]]
        logo_cell = Table(fallback_data, colWidths=[1.1 * inch], rowHeights=[0.55 * inch])
        logo_cell.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), TFT_BLACK),
            ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

    title_para = Paragraph(title, styles['doc_title'])
    title_cell = [title_para]
    if subtitle:
        title_cell.append(Paragraph(subtitle, styles['doc_subtitle']))

    header_data = [[logo_cell, title_cell]]
    header_table = Table(header_data, colWidths=[1.3 * inch, 5.7 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (1, 0), (1, 0),   12),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return header_table


def build_pdf(title, sections, output_path, subtitle=None, meta=None):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.85 * inch,
        title=title,
        author='Toys For Trucks®',
        subject=subtitle or title,
        creator='TFT® PDF Generator',
    )

    styles = build_styles()
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(build_header_table(title, subtitle, styles))
    story.append(Spacer(1, 0.08 * inch))
    story.append(HRFlowable(width='100%', thickness=2, color=TFT_ORANGE, spaceAfter=6))

    # Meta line (date + optional label)
    date_str = datetime.now().strftime('%B %d, %Y')
    meta_line = meta if meta else f'Toys For Trucks®  |  {date_str}'
    story.append(Paragraph(meta_line, styles['meta']))
    story.append(Spacer(1, 0.1 * inch))

    # ── Sections ──────────────────────────────────────────────────────────────
    for section in sections:
        heading = section.get('heading', '')
        items   = section.get('items', [])
        text    = section.get('text', '')

        block = []
        if heading:
            block.append(Paragraph(heading, styles['section_heading']))

        if text:
            for line in text.split('\n'):
                line = line.strip()
                if line:
                    block.append(Paragraph(line, styles['body']))

        for item in items:
            item = item.strip()
            if item:
                block.append(Paragraph(f'• {item}', styles['bullet']))

        if block:
            story.append(KeepTogether(block))
            story.append(Spacer(1, 0.05 * inch))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.2 * inch))
    story.append(HRFlowable(width='100%', thickness=1, color=TFT_MID_GRAY, spaceAfter=8))
    story.append(Paragraph('We Are LifeStyle Driven', styles['tagline']))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        'Toys For Trucks®  |  www.toysfortrucksofficial.com  |  @toysfortrucksofficial  |  855-TFT-LIFT',
        styles['footer_text']
    ))

    doc.build(story)
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Toys For Trucks® PDF Generator')
    parser.add_argument('--title',    required=True,  help='Document title')
    parser.add_argument('--subtitle', default='',     help='Optional subtitle')
    parser.add_argument('--output',   required=True,  help='Output PDF file path')
    parser.add_argument('--meta',     default='',     help='Optional meta line (date, label, etc.)')
    parser.add_argument('--sections', default='[]',   help='JSON array of sections')
    parser.add_argument('--text',     default='',     help='Simple plain text content (no sections)')
    args = parser.parse_args()

    try:
        sections = json.loads(args.sections)
    except json.JSONDecodeError as e:
        print(f'ERROR: Invalid JSON in --sections: {e}')
        sys.exit(1)

    if not sections and args.text:
        sections = [{'heading': '', 'text': args.text}]

    if not sections:
        print('ERROR: Provide --sections or --text')
        sys.exit(1)

    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    build_pdf(
        title=args.title,
        sections=sections,
        output_path=args.output,
        subtitle=args.subtitle or None,
        meta=args.meta or None,
    )
    print(f'PDF saved: {args.output}')


if __name__ == '__main__':
    main()
