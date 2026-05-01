from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from pharmacy_detailed.base import BaseEntity
from pharmacy_detailed.value_objects import Money


@dataclass
class SaleItem(BaseEntity):
    sale_id: int
    medicine_id: int
    quantity: int
    unit_price: Money

    @property
    def subtotal(self) -> Money:
        return Money(self.quantity * self.unit_price.amount)


@dataclass
class Sale(BaseEntity):
    customer_id: Optional[int]
    items: List[SaleItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_item(self, item: SaleItem) -> None:
        if item.sale_id != self.id:
            raise ValueError("Sale item ownership mismatch.")
        self.items.append(item)

    @property
    def total_amount(self) -> Money:
        return Money(sum(item.subtotal.amount for item in self.items))


@dataclass
class Payment(BaseEntity):
    sale_id: int
    amount: Money
    method: str


@dataclass
class Invoice(BaseEntity):
    sale_id: int
    invoice_number: str
    issued_at: datetime = field(default_factory=datetime.now)


@dataclass
class Refund(BaseEntity):
    sale_id: int
    amount: Money
    reason: str
