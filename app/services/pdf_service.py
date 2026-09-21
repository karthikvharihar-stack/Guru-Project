"""
PDF Service — Generate Digital Lekhana Seva Acknowledgement.

IMPORTANT DISCLAIMER:
  This generates a "Digital Lekhana Seva Acknowledgement" — a personal devotional record.
  It is NOT an official certificate of Uttaradi Math Peetham.
  This disclaimer is printed prominently on the generated PDF.
"""

import io
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm, mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
        Table, TableStyle
    )
    from reportlab.pdfgen import canvas as rl_canvas
    REPORTLAB_AVAILABLE = True

    # Spiritual color palette (RGB 0-1 scale) — only defined when reportlab is available
    COLOR_MAROON = colors.HexColor('#8B1A1A')
    COLOR_DARK_BROWN = colors.HexColor('#4A2C17')
    COLOR_GOLD = colors.HexColor('#C9922A')
    COLOR_SAFFRON = colors.HexColor('#D4823A')
    COLOR_IVORY = colors.HexColor('#FDF6E3')
    COLOR_CARD = colors.HexColor('#FFF8EE')
    COLOR_BORDER = colors.HexColor('#D4C5A0')
    COLOR_TEXT = colors.HexColor('#2C1810')
    COLOR_TEXT_LIGHT = colors.HexColor('#6B4A32')

except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_acknowledgement(session) -> bytes:
    """
    Generate a PDF acknowledgement for a completed Lekhana Seva session.

    Args:
        session: LekhanaSession model instance

    Returns:
        bytes: PDF content
    """
    if not REPORTLAB_AVAILABLE:
        return _generate_simple_text_fallback(session)

    buffer = io.BytesIO()

    # Page setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Digital Lekhana Seva Acknowledgement",
        author="Guru Lekhana Seva Platform"
    )

    # Styles
    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontName='Times-Bold',
        fontSize=22,
        textColor=COLOR_MAROON,
        alignment=TA_CENTER,
        spaceAfter=4 * mm,
    )

    style_subtitle = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=13,
        textColor=COLOR_GOLD,
        alignment=TA_CENTER,
        spaceAfter=6 * mm,
    )

    style_section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=11,
        textColor=COLOR_DARK_BROWN,
        spaceAfter=2 * mm,
        spaceBefore=4 * mm,
    )

    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=11,
        textColor=COLOR_TEXT,
        spaceAfter=3 * mm,
        leading=16,
    )

    style_lekhana = ParagraphStyle(
        'Lekhana',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=13,
        textColor=COLOR_MAROON,
        alignment=TA_CENTER,
        spaceAfter=4 * mm,
        spaceBefore=4 * mm,
        borderPad=6 * mm,
        borderColor=COLOR_GOLD,
        borderWidth=1,
        backColor=COLOR_CARD,
    )

    style_disclaimer = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=8,
        textColor=COLOR_TEXT_LIGHT,
        alignment=TA_CENTER,
        spaceAfter=2 * mm,
        leading=12,
    )

    style_footer = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=9,
        textColor=COLOR_TEXT_LIGHT,
        alignment=TA_CENTER,
    )

    # Gather data
    guru = session.guru
    user = session.user
    guru_name = guru.name if guru else 'Unknown Guru'
    bhakta_name = user.name if user else 'Guest Devotee'
    completed_count = session.completed_count
    target_count = session.target_count
    completion_date = session.completed_at or session.created_at or datetime.utcnow()
    date_str = completion_date.strftime('%d %B %Y')

    lekhana_text = ''
    if guru and guru.lekhana_text and '[PLACEHOLDER' not in guru.lekhana_text:
        lekhana_text = guru.lekhana_text

    # Build story (document elements)
    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("🪷", style_title))
    story.append(Paragraph("Digital Lekhana Seva Acknowledgement", style_title))
    story.append(Paragraph("Guru Smarana · Guru Lekhana · Guru Parampara", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_GOLD, spaceAfter=5 * mm))

    # ── Main statement ───────────────────────────────────────────────────────
    statement = (
        f"This is to acknowledge that <b>{bhakta_name}</b> has devotionally completed "
        f"<b>{completed_count} Lekhana(s)</b> of the Guru Namaskara associated with "
        f"<b>{guru_name}</b> on the Guru Lekhana Seva digital platform."
    )
    story.append(Paragraph(statement, style_body))
    story.append(Spacer(1, 4 * mm))

    # ── Details table ────────────────────────────────────────────────────────
    details_data = [
        ['Guru', guru_name],
        ['Devotee (Bhakta)', bhakta_name],
        ['Lekhana Count Completed', str(completed_count)],
        ['Target Count', str(target_count)],
        ['Mode', session.mode.title()],
        ['Date of Completion', date_str],
    ]

    detail_table = Table(
        details_data,
        colWidths=[5 * cm, 11 * cm],
        style=TableStyle([
            ('FONT', (0, 0), (0, -1), 'Times-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Times-Roman', 10),
            ('TEXTCOLOR', (0, 0), (0, -1), COLOR_DARK_BROWN),
            ('TEXTCOLOR', (1, 0), (1, -1), COLOR_TEXT),
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_CARD),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [COLOR_IVORY, COLOR_CARD]),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ])
    )
    story.append(detail_table)
    story.append(Spacer(1, 6 * mm))

    # ── Lekhana display ──────────────────────────────────────────────────────
    if lekhana_text:
        story.append(Paragraph("Guru Lekhana", style_section_header))
        story.append(Paragraph(lekhana_text, style_lekhana))

    # ── Divider ──────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="80%", thickness=1, color=COLOR_GOLD, spaceAfter=5 * mm, spaceBefore=5 * mm))

    # ── Blessing text ────────────────────────────────────────────────────────
    story.append(Paragraph(
        "May the grace of the Guru Parampara bless this devotional effort.",
        ParagraphStyle('Blessing', parent=style_body, alignment=TA_CENTER,
                       fontName='Times-Italic', textColor=COLOR_SAFFRON)
    ))

    story.append(Spacer(1, 8 * mm))

    # ── Disclaimer ───────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER, spaceAfter=3 * mm))

    disclaimer_text = (
        "<b>IMPORTANT DISCLAIMER:</b> This Digital Lekhana Seva Acknowledgement is a personal "
        "devotional record generated by the Guru Lekhana Seva digital platform. "
        "It is NOT an official certificate, authorization, or recognition from Uttaradi Math Peetham "
        "or any religious authority. This platform is an independent devotional initiative and "
        "is not officially affiliated with or endorsed by Uttaradi Math Peetham. "
        "For official religious communications, please contact Uttaradi Math Peetham directly."
    )
    story.append(Paragraph(disclaimer_text, style_disclaimer))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        f"Generated on {datetime.utcnow().strftime('%d %B %Y at %H:%M UTC')} · Guru Lekhana Seva Platform",
        style_footer
    ))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def _generate_simple_text_fallback(session) -> bytes:
    """
    Fallback: generate a plain text acknowledgement if ReportLab is not available.
    Returns bytes (UTF-8 encoded text, not a real PDF).
    """
    guru = session.guru
    user = session.user
    guru_name = guru.name if guru else 'Unknown Guru'
    bhakta_name = user.name if user else 'Guest Devotee'
    completion_date = (session.completed_at or datetime.utcnow()).strftime('%d %B %Y')

    text = f"""
========================================
DIGITAL LEKHANA SEVA ACKNOWLEDGEMENT
Guru Smarana · Guru Lekhana · Guru Parampara
========================================

This acknowledges that {bhakta_name} has completed
{session.completed_count} Lekhana(s) of the Guru Namaskara
associated with {guru_name}.

Details:
  Guru              : {guru_name}
  Devotee (Bhakta)  : {bhakta_name}
  Completed Count   : {session.completed_count}
  Target Count      : {session.target_count}
  Mode              : {session.mode.title()}
  Date              : {completion_date}

May the grace of the Guru Parampara bless this devotional effort.

----------------------------------------
DISCLAIMER: This is a personal devotional record. It is NOT an
official certificate from Uttaradi Math Peetham. This platform
is an independent devotional initiative.
========================================
"""
    return text.encode('utf-8')
