"""
PyLedger CLI - Command line interface for PyLedger
"""

import click
import json
from decimal import Decimal

from pyledger import BusinessEngine, PDFEngine
from pyledger.reports.base import FinancialPeriod


@click.group()
def cli():
    """PyLedger - Professional Accounting Library"""


@cli.command()
@click.option('--company', default='My Company', help='Company name')
@click.option('--currency', default='USD', help='Currency')
@click.option('--country', default='US', help='Country')
@click.option('--output', '-o', default='ledger_state.json', help='Output file')
def init(company, currency, country, output):
    """Initialize a new company ledger"""
    app = BusinessEngine(
        company_name=company,
        currency=currency,
        country=country,
    )
    data = app.ledger.to_dict()
    with open(output, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    click.echo(f"Initialized ledger for '{company}' with {len(app.ledger.accounts)} accounts")
    click.echo(f"Saved to {output}")


@cli.command()
@click.option('--entry-file', '-f', required=True, help='JSON file with entries')
@click.option('--ledger-file', '-l', default='ledger_state.json', help='Ledger state file')
@click.option('--output', '-o', default='ledger_state.json', help='Output file')
def run(entry_file, ledger_file, output):
    """Process business operations from a JSON file"""
    from pyledger import Ledger, Account

    ledger = Ledger('Temp', 'USD')
    try:
        with open(ledger_file) as f:
            data = json.load(f)
        ledger.name = data.get('name', 'Temp')
        ledger.currency = data.get('currency', 'USD')
        for code, acc_data in data.get('accounts', {}).items():
            acc = Account(
                name=acc_data['name'],
                account_type=acc_data['type'],
                code=code,
                currency=acc_data.get('currency', 'USD'),
            )
            ledger.add_account(acc)
    except FileNotFoundError:
        click.echo("No existing ledger found, creating new one")

    app = BusinessEngine(ledger=ledger)

    with open(entry_file) as f:
        entries = json.load(f)

    for entry in entries:
        op = entry.get('operation')
        click.echo(f"Processing: {op} - {entry.get('description', '')}")
        if op == 'sell':
            app.sell(
                items=entry['items'],
                customer=entry['customer'],
                payment_method=entry.get('payment_method', 'credit'),
                tax_rate=entry.get('tax_rate', 0),
            )
        elif op == 'buy':
            app.buy(
                items=entry['items'],
                supplier=entry['supplier'],
                payment_method=entry.get('payment_method', 'credit'),
                tax_rate=entry.get('tax_rate', 0),
            )
        elif op == 'expense':
            app.pay_expense(
                description=entry['description'],
                amount=entry['amount'],
                category=entry.get('category', 'general'),
            )
        elif op == 'salary':
            app.pay_salary(
                employee=entry['employee'],
                gross_salary=entry['gross_salary'],
                deductions=entry.get('deductions', {}),
            )
        elif op == 'investment':
            app.add_investment(
                investor=entry['investor'],
                amount=entry['amount'],
            )
        elif op == 'asset':
            app.buy_fixed_asset(
                name=entry['name'],
                cost=entry['cost'],
                useful_life=entry.get('useful_life'),
            )

    with open(output, 'w') as f:
        json.dump(ledger.to_dict(), f, indent=2, default=str)
    click.echo(f"Ledger saved to {output}")


@cli.command()
@click.option('--type', '-t', 'report_type', default='all',
              help='Report type: income, balance, cashflow, equity, all')
@click.option('--period', '-p', default=None, help='Period label (e.g. "2024-Q1")')
@click.option('--ledger-file', '-l', default='ledger_state.json', help='Ledger state file')
@click.option('--format', '-f', 'output_format', default='text',
              type=click.Choice(['text', 'pdf']), help='Output format')
@click.option('--output', '-o', default=None, help='Output file')
def report(report_type, period, ledger_file, output_format, output):
    """Generate financial reports"""
    from pyledger import Ledger, Account

    ledger = Ledger('Temp', 'USD')
    try:
        with open(ledger_file) as f:
            data = json.load(f)
        ledger.name = data.get('name', 'Temp')
        ledger.currency = data.get('currency', 'USD')
        for code, acc_data in data.get('accounts', {}).items():
            acc = Account(
                name=acc_data['name'],
                account_type=acc_data['type'],
                code=code,
                currency=acc_data.get('currency', 'USD'),
            )
            ledger.add_account(acc)
            if 'balance' in acc_data:
                acc.balance = Decimal(str(acc_data['balance']))
    except FileNotFoundError:
        click.echo("Ledger file not found. Run 'pyledger init' first.", err=True)
        return

    from pyledger.reports import IncomeStatement, BalanceSheet, CashFlowStatement, EquityStatement

    reports = []
    if report_type in ('all', 'income'):
        reports.append(IncomeStatement(ledger))
    if report_type in ('all', 'balance'):
        reports.append(BalanceSheet(ledger))
    if report_type in ('all', 'cashflow'):
        reports.append(CashFlowStatement(ledger))
    if report_type in ('all', 'equity'):
        reports.append(EquityStatement(ledger))

    if output_format == 'text':
        for r in reports:
            click.echo(str(r))
            click.echo()
    elif output_format == 'pdf':
        from pyledger.security.sanitizer import sanitize_filepath
        pdf = PDFEngine(ledger)
        pdf.set_company(name=ledger.name)
        for r in reports:
            pdf.add_report(r)
        out = sanitize_filepath(output or 'report.pdf')
        pdf.save(out)
        click.echo(f"PDF saved to {out}")


@cli.command()
@click.option('--ledger-file', '-l', default='ledger_state.json')
@click.option('--period', '-p', required=True, help='Period label (e.g. "2026-07" or "2026-Q1" or "2026")')
@click.option('--output', '-o', default=None)
def ratios(ledger_file, period, output):
    """Generate financial ratios"""
    from pyledger.reports.ratios import FinancialRatios
    ledger = _load_ledger(ledger_file)
    fp = _parse_period(period)
    r = FinancialRatios(ledger, period=fp)
    click.echo(str(r))
    if output:
        with open(output, 'w') as f:
            f.write(str(r))


@cli.command()
@click.option('--ledger-file', '-l', default='ledger_state.json')
@click.option('--period', '-p', required=True)
@click.option('--vat-rate', default=15.0)
def vat(ledger_file, period, vat_rate):
    """Generate VAT return"""
    from pyledger.accounting.tax_reports import VATReturn
    ledger = _load_ledger(ledger_file)
    fp = _parse_period(period)
    r = VATReturn(ledger, fp, vat_rate=Decimal(str(vat_rate)))
    click.echo(str(r))


@cli.command()
@click.option('--ledger-file', '-l', default='ledger_state.json')
@click.option('--period', '-p', required=True)
@click.option('--country', default='US')
def tax(ledger_file, period, country):
    """Generate corporate tax report"""
    from pyledger.accounting.tax_reports import CorporateTaxReport
    ledger = _load_ledger(ledger_file)
    fp = _parse_period(period)
    r = CorporateTaxReport(ledger, fp, country=country)
    click.echo(str(r))


@cli.command()
@click.option('--ledger-file', '-l', default='ledger_state.json')
@click.option('--cash-account', default='1100')
def reconcile(ledger_file, cash_account):
    """Bank reconciliation report"""
    from pyledger.accounting.bank_reconciliation import BankReconciliation
    ledger = _load_ledger(ledger_file)
    br = BankReconciliation(ledger, cash_account)
    click.echo(br.generate_report())


@cli.command()
@click.option('--ledger-file', '-l', default='ledger_state.json')
@click.option('--type', '-t', 'aging_type', default='receivable',
              type=click.Choice(['receivable', 'payable']))
def aging(ledger_file, aging_type):
    """Generate aging report"""
    from pyledger.accounting.aging import ReceivableAging, PayableAging
    ledger = _load_ledger(ledger_file)
    if aging_type == 'receivable':
        r = ReceivableAging(ledger, [])
    else:
        r = PayableAging(ledger, [])
    click.echo(str(r))


@cli.command()
@click.option('--ledger-file', '-l', default='ledger_state.json')
@click.option('--output', '-o', default=None)
@click.option('--format', '-f', 'output_format', default='text',
              type=click.Choice(['text', 'csv']))
def ratios_export(ledger_file, output, output_format):
    """Export financial ratios"""
    from pyledger.reports.ratios import FinancialRatios
    from pyledger.reports.export import ReportExporter
    ledger = _load_ledger(ledger_file)
    r = FinancialRatios(ledger)
    if output_format == 'csv':
        csv_data = ReportExporter.export_ratios(r.generate())
        if output:
            with open(output, 'w') as f:
                f.write(csv_data)
            click.echo(f"CSV saved to {output}")
        else:
            click.echo(csv_data)
    else:
        click.echo(str(r))


def _load_ledger(filepath: str):
    """Load ledger from JSON file (fails closed with a clean message)"""
    import json
    from pyledger import Ledger, Account
    from pyledger.security.sanitizer import sanitize_filepath
    filepath = sanitize_filepath(filepath)
    ledger = Ledger('Temp', 'USD')
    try:
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)
        ledger.name = data.get('name', 'Temp')
        ledger.currency = data.get('currency', 'USD')
        for code, acc_data in data.get('accounts', {}).items():
            acc = Account(
                name=acc_data['name'],
                account_type=acc_data['type'],
                code=code,
                currency=acc_data.get('currency', 'USD'),
            )
            ledger.add_account(acc)
            if 'balance' in acc_data:
                acc.balance = Decimal(str(acc_data['balance']))
    except FileNotFoundError:
        click.echo(f"Ledger file {filepath} not found.", err=True)
        raise
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
        raise click.ClickException(f"Invalid ledger file {filepath}: {e}")
    return ledger


def _parse_period(label: str) -> FinancialPeriod:
    """Parse period label like '2026-07', '2026-Q1', '2026'"""
    try:
        if label.startswith('YTD'):
            parts = label.replace('YTD ', '').split('-')
            return FinancialPeriod.year_to_date(int(parts[0]), int(parts[1]))
        if 'Q' in label:
            parts = label.split('Q')
            return FinancialPeriod.quarterly(int(parts[0]), int(parts[1]))
        if '-' in label:
            parts = label.split('-')
            return FinancialPeriod.monthly(int(parts[0]), int(parts[1]))
        return FinancialPeriod.annual(int(label))
    except (ValueError, IndexError, AttributeError):
        raise click.BadParameter(
            f"Invalid period '{label}'. Use '2026-07', '2026-Q1', '2026' or 'YTD 2026-07'")


if __name__ == '__main__':
    cli()
