"""
PyLedger Utilities Module - Formatting
Text formatting utilities
"""

from decimal import Decimal


class Formatter:
    """Format data for display"""
    
    @staticmethod
    def format_amount(amount, currency_symbol: str = '', decimals: int = 2) -> str:
        """Format amount with currency symbol"""
        decimal_amount = Decimal(str(amount))
        formatted = f"{decimal_amount:.{decimals}f}"
        if currency_symbol:
            return f"{currency_symbol}{formatted}"
        return formatted
    
    @staticmethod
    def format_date(date_obj, format_str: str = '%Y-%m-%d') -> str:
        """Format date"""
        if isinstance(date_obj, str):
            return date_obj
        return date_obj.strftime(format_str)
    
    @staticmethod
    def format_table(data: list, headers: list = None) -> str:
        """Format data as table"""
        if not data:
            return "No data"
        
        if headers is None:
            headers = list(data[0].keys()) if isinstance(data[0], dict) else []
        
        # Calculate column widths
        widths = {h: len(str(h)) for h in headers}
        
        for row in data:
            for header in headers:
                value = row.get(header) if isinstance(row, dict) else getattr(row, header, '')
                widths[header] = max(widths[header], len(str(value)))
        
        # Build table
        lines = []
        
        # Header
        header_line = " | ".join(f"{h:<{widths[h]}}" for h in headers)
        lines.append(header_line)
        lines.append("-" * len(header_line))
        
        # Rows
        for row in data:
            row_values = []
            for header in headers:
                value = row.get(header) if isinstance(row, dict) else getattr(row, header, '')
                row_values.append(f"{str(value):<{widths[header]}}")
            lines.append(" | ".join(row_values))
        
        return "\n".join(lines)
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        """Format value as percentage"""
        return f"{float(value):.{decimals}f}%"
