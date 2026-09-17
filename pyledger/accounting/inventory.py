"""
PyLedger Accounting - Inventory System
FIFO and Weighted Average Cost valuation
"""

from decimal import Decimal
from datetime import datetime
from collections import deque
from typing import Optional, List, Dict
from pyledger.utils.validators import format_amount


class InventoryItem:
    """Represents a single inventory item with stock tracking"""

    def __init__(self, sku: str, name: str, category: str = 'general',
                 selling_price: Decimal = Decimal('0'),
                 valuation_method: str = 'fifo'):
        self.sku = sku
        self.name = name
        self.category = category
        self.selling_price = Decimal(str(selling_price))
        self.valuation_method = valuation_method
        self.current_qty = Decimal('0')
        self.reserved_qty = Decimal('0')
        self._fifo_layers = deque()
        self._total_cost = Decimal('0')
        self.movements = []

    @property
    def available_qty(self) -> Decimal:
        return self.current_qty - self.reserved_qty

    def receive(self, qty, unit_cost, reference: str = '',
                date: datetime = None) -> dict:
        qty = Decimal(str(qty))
        cost = Decimal(str(unit_cost))
        self.current_qty += qty
        if self.valuation_method == 'fifo':
            self._fifo_layers.append((qty, cost))
        self._total_cost += qty * cost

        movement = {
            'type': 'in',
            'qty': qty,
            'unit_cost': cost,
            'reference': reference,
            'date': date or datetime.now(),
            'balance_qty': self.current_qty,
        }
        self.movements.append(movement)
        return movement

    def issue(self, qty, reference: str = '',
              date: datetime = None) -> dict:
        qty = Decimal(str(qty))
        if qty > self.current_qty:
            raise ValueError(f"Insufficient stock. Available: {self.current_qty}, Requested: {qty}")

        cost = Decimal('0')
        remaining = qty

        if self.valuation_method == 'fifo':
            while remaining > 0 and self._fifo_layers:
                layer_qty, layer_cost = self._fifo_layers[0]
                if layer_qty <= remaining:
                    cost += layer_qty * layer_cost
                    remaining -= layer_qty
                    self._fifo_layers.popleft()
                else:
                    cost += remaining * layer_cost
                    self._fifo_layers[0] = (layer_qty - remaining, layer_cost)
                    remaining = Decimal('0')

        elif self.valuation_method == 'weighted_average':
            avg_cost = self.weighted_average_cost()
            cost = qty * avg_cost

        self.current_qty -= qty

        if self.valuation_method == 'weighted_average':
            self._total_cost -= cost

        unit_cost = (cost / qty).quantize(Decimal('0.01')) if qty > 0 else Decimal('0')

        movement = {
            'type': 'out',
            'qty': qty,
            'unit_cost': unit_cost,
            'total_cost': cost,
            'reference': reference,
            'date': date or datetime.now(),
            'balance_qty': self.current_qty,
        }
        self.movements.append(movement)
        return movement

    def weighted_average_cost(self) -> Decimal:
        """Weighted average unit cost (method API required by test suite)."""
        if self.current_qty == 0:
            return Decimal('0')
        return (self._total_cost / self.current_qty).quantize(Decimal('0.01'))

    @property
    def inventory_value(self) -> Decimal:
        if self.valuation_method == 'fifo':
            return sum(q * c for q, c in self._fifo_layers)
        return self._total_cost

    def to_dict(self) -> dict:
        try:
            wac = self.weighted_average_cost()
        except TypeError:
            wac = self.weighted_average_cost
        return {
            'sku': self.sku,
            'name': self.name,
            'category': self.category,
            'current_qty': str(self.current_qty),
            'available_qty': str(self.available_qty),
            'inventory_value': str(self.inventory_value),
            'valuation_method': self.valuation_method,
            'weighted_average_cost': str(wac),
        }


class InventoryManager:
    """Manage inventory items and valuations"""

    def __init__(self):
        self.items = {}

    def add_item(self, item: InventoryItem):
        self.items[item.sku] = item

    def get_item(self, sku: str) -> InventoryItem:
        if sku not in self.items:
            raise ValueError(f"Item '{sku}' not found")
        return self.items[sku]

    def receive(self, sku: str, qty, unit_cost, reference='', date=None) -> dict:
        return self.get_item(sku).receive(qty, unit_cost, reference, date)

    def issue(self, sku: str, qty, reference='', date=None) -> dict:
        return self.get_item(sku).issue(qty, reference, date)

    def get_inventory_value(self) -> Decimal:
        return sum(item.inventory_value for item in self.items.values())

    def get_valuation_report(self) -> dict:
        items = []
        for sku, item in self.items.items():
            items.append(item.to_dict())
        return {
            'items': items,
            'total_value': str(self.get_inventory_value()),
            'total_items': len(self.items),
        }

    def get_movements(self, sku: str = None, limit: int = 50) -> list:
        if sku:
            return self.get_item(sku).movements[-limit:]
        all_movements = []
        for item in self.items.values():
            all_movements.extend(item.movements)
        all_movements.sort(key=lambda m: m.get('date', datetime.min), reverse=True)
        return all_movements[:limit]
