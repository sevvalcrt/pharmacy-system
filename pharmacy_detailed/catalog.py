from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from pharmacy_detailed.base import BaseEntity
from pharmacy_detailed.value_objects import Money


@dataclass
class Category(BaseEntity):
    name: str


@dataclass
class Manufacturer(BaseEntity):
    name: str
    country: str


@dataclass
class Medicine(BaseEntity):
    name: str
    category_id: int
    manufacturer_id: int
    unit_price: Money
    stock: int
    expiry_date: Optional[date] = None

    def is_expired(self) -> bool:
        return self.expiry_date is not None and self.expiry_date < date.today()


@dataclass
class MedicineAlternative(BaseEntity):
    medicine_id: int
    alternative_medicine_id: int
    reason: str


@dataclass
class Batch(BaseEntity):
    medicine_id: int
    lot_number: str
    quantity: int
    expiry_date: date
