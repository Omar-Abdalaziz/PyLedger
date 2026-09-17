"""
PyLedger PDF Module - Reusable PDF Elements
"""

from decimal import Decimal
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from pyledger.pdf.styles import *


def make_statement_table(headers: list, rows: list,
                         col_widths: list = None,
                         title: str = None) -> Table:
    """Create a styled table for financial statements"""
    data = [headers] + rows if headers else rows
    if col_widths is None:
        col_widths = [CONTENT_WIDTH * 0.6, CONTENT_WIDTH * 0.2, CONTENT_WIDTH * 0.2]

    style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), SIZE_ACCOUNT_NAME),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_TEXT),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ])

    if headers:
        style.add('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY)
        style.add('TEXTCOLOR', (0, 0), (-1, 0), colors.white)
        style.add('FONTSIZE', (0, 0), (-1, 0), SIZE_SECTION_HEADER)
        style.add('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(style)
    return table


def make_section_table(accounts: list, total: str,
                       label_col: str = 'name',
                       amount_col: str = 'amount',
                       section_color=COLOR_PRIMARY) -> Table:
    """Create a styled accounts section (name + amount columns)"""
    rows = []
    for acc in accounts:
        amount = acc.get(amount_col, '0')
        rows.append([f"  {acc.get(label_col, '')}", '', amount])

    total_row = [f"Total", '', total]
    data = rows + [total_row]

    col_widths = [CONTENT_WIDTH * 0.7, CONTENT_WIDTH * 0.05, CONTENT_WIDTH * 0.25]

    style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), SIZE_ACCOUNT_NAME),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_TEXT),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LINEABOVE', (0, -1), (-1, -1), 1, COLOR_TOTAL_LINE),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), SIZE_TOTAL),
    ])

    table = Table(data, colWidths=col_widths)
    table.setStyle(style)
    return table


def make_section_header(text: str, color=COLOR_SECTION_HEADER) -> Table:
    """Create a styled section header"""
    data = [[text]]
    col_widths = [CONTENT_WIDTH]

    style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), SIZE_SECTION_HEADER),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('BACKGROUND', (0, 0), (-1, -1), color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ])

    table = Table(data, colWidths=col_widths)
    table.setStyle(style)
    return table


def make_total_line(label: str, amount: str, double: bool = False) -> Table:
    """Create a styled total line"""
    data = [[label, '', amount]]
    col_widths = [CONTENT_WIDTH * 0.7, CONTENT_WIDTH * 0.05, CONTENT_WIDTH * 0.25]

    style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), SIZE_TOTAL),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLOR_TOTAL_LINE),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (0, 0), (-1, 0), 1, COLOR_TOTAL_LINE),
    ])

    if double:
        style.add('LINEBELOW', (0, -1), (-1, -1), 2, COLOR_TOTAL_LINE)
        style.add('LINEABOVE', (0, -1), (-1, -1), 2, COLOR_TOTAL_LINE)

    table = Table(data, colWidths=col_widths)
    table.setStyle(style)
    return table
