"""
PyLedger PDF Module - Main PDF Engine
"""

from typing import Optional, List, Type
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

from pyledger.pdf.styles import *
from pyledger.pdf.branding import CompanyInfo
from pyledger.pdf.arabic import prepare_text, contains_arabic
from pyledger.pdf.elements import (
    make_section_table, make_section_header, make_total_line
)
from pyledger.reports.base import BaseReport
from pyledger.core.ledger import Ledger


class PDFEngine:
    """Generate professional PDF financial reports"""

    def __init__(self, ledger: Ledger, company: Optional[CompanyInfo] = None):
        self.ledger = ledger
        self.company = company or CompanyInfo(name="Company Name")
        self.elements = []

    def set_company(self, name: str = '', logo: str = '',
                    cr: str = '', vat: str = '',
                    address: str = '', phone: str = '',
                    email: str = ''):
        """Configure company info"""
        self.company = CompanyInfo(
            name=name, logo_path=logo or None,
            cr_number=cr, vat_number=vat,
            address=address, phone=phone, email=email
        )

    def add_report(self, report: BaseReport):
        """Add a report to the document"""
        data = report.generate()
        report_type = report.__class__.__name__

        if report_type == 'IncomeStatement':
            self._build_income_statement(data, report)
        elif report_type == 'BalanceSheet':
            self._build_balance_sheet(data, report)
        elif report_type == 'CashFlowStatement':
            self._build_cash_flow(data, report)
        elif report_type == 'EquityStatement':
            self._build_equity_statement(data, report)
        elif report_type == 'FinancialRatios':
            self._build_ratios(data)
        elif report_type == 'ReceivableAging':
            self._build_aging(data, 'Receivable Aging')
        elif report_type == 'PayableAging':
            self._build_aging(data, 'Payable Aging')
        elif report_type == 'VATReturn':
            self._build_vat_return(data)
        elif report_type == 'CorporateTaxReport':
            self._build_tax_report(data)
        elif report_type == 'BudgetVsActual':
            self._build_budget_vs_actual(data)
        elif report_type == 'ComparativeIncomeStatement':
            self._build_comparative(data)
        elif report_type == 'ProjectProfitability':
            self._build_project_report(data)
        elif report_type == 'ConsolidatedReport':
            self._build_consolidated(data)

    def save(self, filepath: str):
        """Generate and save PDF to file"""
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            leftMargin=MARGIN_LEFT,
            rightMargin=MARGIN_RIGHT,
            topMargin=MARGIN_TOP,
            bottomMargin=MARGIN_BOTTOM,
        )
        doc.build(self.elements)

    def to_bytes(self) -> bytes:
        """Generate PDF and return as bytes"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=MARGIN_LEFT,
            rightMargin=MARGIN_RIGHT,
            topMargin=MARGIN_TOP,
            bottomMargin=MARGIN_BOTTOM,
        )
        doc.build(self.elements)
        return buffer.getvalue()

    def _add_header(self, title: str, subtitle: str = ''):
        """Add document header with company info"""
        styles = getSampleStyleSheet()

        if self.company.logo_path:
            try:
                logo = Image(self.company.logo_path, width=40 * mm, height=20 * mm)
                logo_data = [[logo, '']]
                logo_table = Table(logo_data, colWidths=[40 * mm, CONTENT_WIDTH - 40 * mm])
                logo_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ]))
                self.elements.append(logo_table)
            except Exception:
                pass

        company_style = ParagraphStyle(
            'CompanyName',
            parent=styles['Normal'],
            fontSize=SIZE_TITLE,
            textColor=COLOR_PRIMARY,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=2,
        )
        self.elements.append(Paragraph(prepare_text(self.company.name), company_style))

        if self.company.address:
            addr_style = ParagraphStyle(
                'Address', parent=styles['Normal'],
                fontSize=SIZE_FOOTER, textColor=COLOR_MUTED, alignment=TA_LEFT
            )
            self.elements.append(Paragraph(prepare_text(self.company.address), addr_style))

        info_parts = []
        if self.company.cr_number:
            info_parts.append(f"CR: {self.company.cr_number}")
        if self.company.vat_number:
            info_parts.append(f"VAT: {self.company.vat_number}")
        if info_parts:
            info_style = ParagraphStyle(
                'Info', parent=styles['Normal'],
                fontSize=SIZE_FOOTER, textColor=COLOR_MUTED, alignment=TA_LEFT
            )
            self.elements.append(Paragraph(' | '.join(info_parts), info_style))

        self.elements.append(Spacer(1, 6 * mm))

        title_style = ParagraphStyle(
            'ReportTitle', parent=styles['Normal'],
            fontSize=SIZE_TITLE + 2, textColor=COLOR_PRIMARY,
            fontName='Helvetica-Bold', alignment=TA_CENTER,
            spaceBefore=4, spaceAfter=2,
        )
        self.elements.append(Paragraph(prepare_text(title), title_style))

        if subtitle:
            sub_style = ParagraphStyle(
                'Subtitle', parent=styles['Normal'],
                fontSize=SIZE_SUBTITLE, textColor=COLOR_SECONDARY,
                alignment=TA_CENTER, spaceAfter=6,
            )
            self.elements.append(Paragraph(prepare_text(subtitle), sub_style))

        sep_style = ParagraphStyle(
            'Sep', parent=styles['Normal'],
            fontSize=2, textColor=COLOR_BORDER,
            spaceAfter=4, spaceBefore=2,
        )
        self.elements.append(Paragraph('<hr/>', sep_style))
        self.elements.append(Spacer(1, 2 * mm))

    def _add_footer(self):
        """Add footer"""
        styles = getSampleStyleSheet()
        self.elements.append(Spacer(1, 4 * mm))
        sep_style = ParagraphStyle('Sep2', parent=styles['Normal'],
                                    fontSize=2, textColor=COLOR_BORDER,
                                    spaceBefore=4)
        self.elements.append(Paragraph('<hr/>', sep_style))

        footer_text = ' | '.join(self.company.footer_lines())
        footer_style = ParagraphStyle(
            'Footer', parent=styles['Normal'],
            fontSize=SIZE_FOOTER, textColor=COLOR_MUTED,
            alignment=TA_CENTER,
        )
        self.elements.append(Paragraph(prepare_text(footer_text), footer_style))

    def _add_section_title(self, text: str, color=COLOR_SECTION_HEADER):
        """Add a section title"""
        styles = getSampleStyleSheet()
        section_style = ParagraphStyle(
            'SectionTitle', parent=styles['Normal'],
            fontSize=SIZE_SECTION_HEADER, textColor=colors.white,
            fontName='Helvetica-Bold', alignment=TA_LEFT,
            spaceBefore=6, spaceAfter=2,
            backColor=color,
            leftIndent=4, rightIndent=4,
            borderPadding=4,
        )
        self.elements.append(Paragraph(prepare_text(text.upper()), section_style))

    def _add_accounts_section(self, accounts: list, total: str):
        """Add a list of accounts with amounts"""
        if not accounts:
            return
        rows = []
        for acc in accounts:
            rows.append([
                Paragraph(prepare_text(f"  {acc['name']}"),
                          ParagraphStyle('acc', fontSize=SIZE_ACCOUNT_NAME)),
                '',
                Paragraph(acc['amount'],
                          ParagraphStyle('amt', fontSize=SIZE_ACCOUNT_NAME, alignment=TA_RIGHT))
            ])
        rows.append([
            Paragraph(prepare_text("Total"),
                      ParagraphStyle('tot', fontSize=SIZE_TOTAL, fontName='Helvetica-Bold')),
            '',
            Paragraph(total,
                      ParagraphStyle('tot_amt', fontSize=SIZE_TOTAL, fontName='Helvetica-Bold',
                                     alignment=TA_RIGHT))
        ])

        col_widths = [CONTENT_WIDTH * 0.7, CONTENT_WIDTH * 0.05, CONTENT_WIDTH * 0.25]
        table = Table(rows, colWidths=col_widths)
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
        table.setStyle(style)
        self.elements.append(table)

    def _build_income_statement(self, data: dict, report):
        period_label = report.period.label if report.period else \
            f"As of {report.as_of_date.strftime('%Y-%m-%d')}"
        self._add_header("Income Statement", period_label)

        self._add_section_title("Revenue", COLOR_INCOME)
        self._add_accounts_section(data.get('income', {}).get('accounts', []),
                                    data.get('income', {}).get('total', '0'))

        self._add_section_title("Expenses", COLOR_EXPENSE)
        self._add_accounts_section(data.get('expenses', {}).get('accounts', []),
                                    data.get('expenses', {}).get('total', '0'))

        self._add_footer()

    def _build_balance_sheet(self, data: dict, report):
        as_of = report.as_of_date.strftime('%Y-%m-%d')
        self._add_header("Balance Sheet", f"As of {as_of}")

        self._add_section_title("Assets", COLOR_ASSET)
        if data.get('assets', {}).get('current'):
            subtitle_style = ParagraphStyle('sub', fontSize=SIZE_ACCOUNT_NAME,
                                             textColor=COLOR_MUTED, leftIndent=8)
            self.elements.append(Paragraph("Current Assets", subtitle_style))
            self._add_accounts_section(data['assets']['current'],
                                        data['assets']['total_current'])
        if data.get('assets', {}).get('noncurrent'):
            subtitle_style = ParagraphStyle('sub', fontSize=SIZE_ACCOUNT_NAME,
                                             textColor=COLOR_MUTED, leftIndent=8)
            self.elements.append(Paragraph("Non-Current Assets", subtitle_style))
            self._add_accounts_section(data['assets']['noncurrent'],
                                        data['assets']['total_noncurrent'])

        self._add_section_title("Liabilities", COLOR_LIABILITY)
        if data.get('liabilities', {}).get('current'):
            subtitle_style = ParagraphStyle('sub', fontSize=SIZE_ACCOUNT_NAME,
                                             textColor=COLOR_MUTED, leftIndent=8)
            self.elements.append(Paragraph("Current Liabilities", subtitle_style))
            self._add_accounts_section(data['liabilities']['current'],
                                        data['liabilities']['total_current'])
        if data.get('liabilities', {}).get('noncurrent'):
            subtitle_style = ParagraphStyle('sub', fontSize=SIZE_ACCOUNT_NAME,
                                             textColor=COLOR_MUTED, leftIndent=8)
            self.elements.append(Paragraph("Non-Current Liabilities", subtitle_style))
            self._add_accounts_section(data['liabilities']['noncurrent'],
                                        data['liabilities']['total_noncurrent'])

        self._add_section_title("Equity", COLOR_EQUITY)
        equity_data = data.get('equity', {})
        accounts = list(equity_data.get('accounts', []))
        net_income = equity_data.get('net_income')
        if net_income:
            accounts.append({'name': 'Net Income', 'amount': net_income})
        self._add_accounts_section(accounts, equity_data.get('total', '0'))

        self._add_footer()

    def _build_cash_flow(self, data: dict, report):
        period_label = report.period.label if report.period else "Period"
        self._add_header("Cash Flow Statement", period_label)

        sections = [
            ('operating', 'Operating Activities', COLOR_INCOME),
            ('investing', 'Investing Activities', COLOR_ASSET),
            ('financing', 'Financing Activities', COLOR_LIABILITY),
        ]

        for key, title, color in sections:
            section = data.get(key, {})
            items_data = []
            labels = section.get('labels', [])
            amounts = section.get('items', [])
            for i in range(len(labels)):
                items_data.append({'name': labels[i], 'amount': amounts[i]})

            self._add_section_title(title, color)
            self._add_accounts_section(items_data, section.get('total', '0'))

        self._add_footer()

    def _build_equity_statement(self, data: dict, report):
        period_label = report.period.label if report.period else "Period"
        self._add_header("Statement of Changes in Equity", period_label)

        if data.get('opening_balances'):
            self._add_section_title("Opening Balances", COLOR_EQUITY)
            self._add_accounts_section(data['opening_balances'],
                                        data.get('opening_total', '0'))

        if data.get('net_income', '0') != '0':
            self.elements.append(Spacer(1, 2 * mm))
            ni_style = ParagraphStyle('ni', fontSize=SIZE_ACCOUNT_NAME, textColor=COLOR_TEXT)
            self.elements.append(Paragraph(f"Net Income: {data['net_income']}", ni_style))

        if data.get('closing_balances'):
            self._add_section_title("Closing Balances", COLOR_EQUITY)
            self._add_accounts_section(data['closing_balances'],
                                        data.get('closing_total', '0'))

        self._add_footer()

    def _build_ratios(self, data: dict):
        self._add_header("Financial Ratios", data.get('period', ''))
        categories = [
            ('liquidity', 'LIQUIDITY RATIOS', COLOR_ASSET),
            ('profitability', 'PROFITABILITY RATIOS', COLOR_INCOME),
            ('leverage', 'LEVERAGE RATIOS', COLOR_LIABILITY),
            ('efficiency', 'EFFICIENCY RATIOS', COLOR_EQUITY),
        ]
        for key, title, color in categories:
            section = data.get(key, {})
            if not section:
                continue
            self._add_section_title(title, color)
            items = []
            for k, v in section.items():
                items.append({'name': k.replace('_', ' ').title(), 'amount': str(v)})
            self._add_accounts_section(items, '')
        self._add_footer()

    def _build_aging(self, data: dict, title: str):
        self._add_header(title, f"As of {data.get('as_of_date', '')[:10]}")
        entity_key = 'customers' if 'customers' in data else 'suppliers'
        for ent in data.get(entity_key, []):
            items = [{'name': 'Total', 'amount': ent['total']}]
            for k, v in ent.get('brackets', {}).items():
                items.append({'name': k, 'amount': v})
            self._add_accounts_section(items, ent['total'])
        self._add_footer()

    def _build_vat_return(self, data: dict):
        self._add_header("VAT Return", data.get('period', ''))
        items = [
            {'name': 'VAT Rate', 'amount': f"{data.get('vat_rate', '0')}%"},
            {'name': 'Output VAT (Sales)', 'amount': data.get('vat_payable', '0')},
            {'name': 'Input VAT (Purchases)', 'amount': data.get('vat_receivable', '0')},
            {'name': 'Net VAT Due', 'amount': data.get('net_vat_due', '0')},
        ]
        self._add_accounts_section(items, data.get('net_vat_due', '0'))
        self._add_footer()

    def _build_tax_report(self, data: dict):
        self._add_header("Corporate Tax Report", data.get('period', ''))
        items = [
            {'name': 'Tax Rate', 'amount': f"{data.get('tax_rate', '0')}%"},
            {'name': 'Net Profit Before Tax', 'amount': data.get('net_profit_before_tax', '0')},
            {'name': 'Estimated Tax', 'amount': data.get('estimated_tax', '0')},
            {'name': 'Net Profit After Tax', 'amount': data.get('net_profit_after_tax', '0')},
        ]
        self._add_accounts_section(items, data.get('net_profit_after_tax', '0'))
        self._add_footer()

    def _build_budget_vs_actual(self, data: dict):
        self._add_header("Budget vs Actual", data.get('period', ''))
        for line in data.get('lines', []):
            items = [
                {'name': 'Account', 'amount': line.get('account_code', '')},
                {'name': 'Budgeted', 'amount': line.get('budgeted', '0')},
                {'name': 'Actual', 'amount': line.get('actual', '0')},
                {'name': 'Variance', 'amount': line.get('variance', '0')},
            ]
            self._add_accounts_section(items, line.get('variance', '0'))
        self._add_footer()

    def _build_comparative(self, data: dict):
        self._add_header("Comparative Report", " | ".join(data.get('periods', [])))
        for row in data.get('rows', []):
            items = [{'name': 'Account', 'amount': row.get('account', '')}]
            for i, p in enumerate(data.get('periods', [])):
                amounts = row.get('amounts', [])
                items.append({'name': p, 'amount': amounts[i] if i < len(amounts) else '0'})
            self._add_accounts_section(items, '')
        self._add_footer()

    def _build_project_report(self, data: dict):
        self._add_header("Project Profitability", '')
        for p in data.get('projects', []):
            items = [
                {'name': p.get('name', ''), 'amount': ''},
                {'name': 'Revenue', 'amount': p.get('revenue', '0')},
                {'name': 'Cost', 'amount': p.get('cost', '0')},
                {'name': 'Profit', 'amount': p.get('profit', '0')},
                {'name': 'Margin', 'amount': f"{p.get('margin_pct', '0')}%"},
            ]
            self._add_accounts_section(items, p.get('profit', '0'))
        self._add_footer()

    def _build_consolidated(self, data: dict):
        self._add_header("Consolidated Report", f"{data.get('entities', 0)} entities")
        income = data.get('income', {})
        balance = data.get('balance', {})
        items = [
            {'name': 'Income Statement', 'amount': income.get('title', '')},
            {'name': 'Balance Sheet', 'amount': balance.get('title', '')},
        ]
        self._add_accounts_section(items, '')
        self._add_footer()
