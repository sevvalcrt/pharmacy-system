from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from pharmacy_detailed.base import BaseEntity


@dataclass
class InventoryMovement(BaseEntity):
    medicine_id: int
    quantity_change: int
    action_type: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StockAlert(BaseEntity):
    medicine_id: int
    threshold: int
    active: bool = True


@dataclass
class ReorderRule(BaseEntity):
    medicine_id: int
    minimum_stock: int
    reorder_quantity: int


@dataclass
class StockAudit(BaseEntity):
    medicine_id: int
    counted_stock: int
    system_stock: int

    @property
    def difference(self) -> int:
        return self.counted_stock - self.system_stock
