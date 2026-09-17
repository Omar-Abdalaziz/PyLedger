"""
PyLedger PDF Module - Styles
Colors, fonts, and styling constants for PDF generation
"""

from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.pagesizes import A4

# Page setup
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 20 * mm
MARGIN_RIGHT = 20 * mm
MARGIN_TOP = 20 * mm
MARGIN_BOTTOM = 20 * mm
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

# Colors
COLOR_PRIMARY = colors.HexColor('#1a237e')
COLOR_SECONDARY = colors.HexColor('#3949ab')
COLOR_ACCENT = colors.HexColor('#0d47a1')
COLOR_BACKGROUND = colors.HexColor('#f5f5f5')

COLOR_ASSET = colors.HexColor('#1565c0')
COLOR_LIABILITY = colors.HexColor('#c62828')
COLOR_EQUITY = colors.HexColor('#2e7d32')
COLOR_INCOME = colors.HexColor('#00838f')
COLOR_EXPENSE = colors.HexColor('#e65100')

COLOR_HEADING = colors.HexColor('#1a237e')
COLOR_SUBHEADING = colors.HexColor('#283593')
COLOR_SECTION_HEADER = COLOR_HEADING
COLOR_TEXT = colors.HexColor('#212121')
COLOR_MUTED = colors.HexColor('#757575')
COLOR_BORDER = colors.HexColor('#bdbdbd')
COLOR_TOTAL_LINE = colors.HexColor('#424242')

# Font sizes (will use built-in Helvetica since Arabic reshapes handle it)
SIZE_TITLE = 16
SIZE_SUBTITLE = 11
SIZE_SECTION_HEADER = 10
SIZE_ACCOUNT_NAME = 9
SIZE_AMOUNT = 9
SIZE_TOTAL = 10
SIZE_FOOTER = 8
SIZE_NOTE = 8

# Spacing
LINE_HEIGHT = 14
SECTION_SPACE = 8
PARAGRAPH_SPACE = 4
