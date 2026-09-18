"""
PyLedger Reports - CSV / Excel Export for Financial Reports
"""

import csv
import io
from decimal import Decimal
from typing import Optional
from pyledger.reports.base import BaseReport, FinancialPeriod
from pyledger.core.ledger import Ledger
from pyledger.security.sanitizer import sanitize_csv_field


def _cell(value) -> str:
    """CSV-injection-safe cell: neutralizes =,+,-,@-leading payloads."""
    return sanitize_csv_field('' if value is None else str(value))


class ReportExporter:
    """Export reports to CSV format"""

    @staticmethod
    def to_csv(report: BaseReport) -> str:
        data = report.generate()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([_cell(data.get('title', 'Report')), _cell(data.get('period', ''))])
        writer.writerow([])

        if 'items' in data:
            writer.writerow(['Account', 'Amount'])
            for item in data['items']:
                writer.writerow([_cell(item.get('account', '')), _cell(item.get('amount', '0'))])
        elif 'lines' in data:
            if data['lines']:
                first = data['lines'][0]
                writer.writerow([_cell(k) for k in first.keys()])
                for line in data['lines']:
                    writer.writerow([_cell(line.get(k, '')) for k in first.keys()])
        elif 'assets' in data:
            writer.writerow(['Category', 'Account', 'Amount'])
            for item in data.get('assets', []):
                writer.writerow(['Assets', _cell(item.get('account', '')), _cell(item.get('amount', '0'))])
            for item in data.get('liabilities', []):
                writer.writerow(['Liabilities', _cell(item.get('account', '')), _cell(item.get('amount', '0'))])
            for item in data.get('equity', []):
                writer.writerow(['Equity', _cell(item.get('account', '')), _cell(item.get('amount', '0'))])
        elif 'operating' in data:
            for section in ('operating', 'investing', 'financing'):
                s = data.get(section, {})
                writer.writerow([section.upper()])
                for i in range(len(s.get('labels', []))):
                    writer.writerow([_cell(s['labels'][i]), _cell(s['items'][i])])
                writer.writerow(['Net Cash', _cell(s.get('total', '0'))])
                writer.writerow([])

        return output.getvalue()

    @staticmethod
    def to_csv_file(report: BaseReport, filepath: str):
        content = ReportExporter.to_csv(report)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def export_aging(aging_data: dict) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([_cell(aging_data.get('title', 'Aging Report')),
                         _cell(f"As of {aging_data.get('as_of_date', '')}")])
        writer.writerow([])
        key = 'customers' if 'customers' in aging_data else 'suppliers'
        entity_list = aging_data.get(key, [])
        if entity_list:
            first = entity_list[0]
            brackets = [k for k in first.keys() if k not in ('name', 'total', f'{key[:-1]}_id')]
            header = ['Name', 'Total'] + [b for b in brackets]
            writer.writerow([_cell(h) for h in header])
            for ent in entity_list:
                row = [_cell(ent.get('name', '')), _cell(ent.get('total', '0'))]
                for b in brackets:
                    row.append(_cell(ent.get(brackets[0], {}).get(b, '0')) if isinstance(ent.get(brackets[0]), dict) else _cell(ent.get(b, '0')))
                writer.writerow(row)
        writer.writerow([])
        writer.writerow(['Grand Total', _cell(aging_data.get('grand_total', '0'))])
        return output.getvalue()

    @staticmethod
    def export_ratios(ratios_data: dict) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Financial Ratios', _cell(ratios_data.get('period', ''))])
        writer.writerow([])
        for category, values in ratios_data.items():
            if isinstance(values, dict) and category != 'title':
                writer.writerow([_cell(category.upper())])
                for k, v in values.items():
                    writer.writerow([_cell(k), _cell(str(v))])
                writer.writerow([])
        return output.getvalue()
