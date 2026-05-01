from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from pharmacy_detailed.base import BaseEntity


@dataclass
class PrescriptionItem(BaseEntity):
    prescription_id: int
    medicine_id: int
    quantity: int
    dosage_note: str


@dataclass
class Prescription(BaseEntity):
    customer_id: int
    doctor_id: int
    created_at: datetime = field(default_factory=datetime.now)
    items: List[PrescriptionItem] = field(default_factory=list)

    def add_item(self, item: PrescriptionItem) -> None:
        if item.prescription_id != self.id:
            raise ValueError("Prescription item ownership mismatch.")
        self.items.append(item)


@dataclass
class PrescriptionValidator:
    def validate_medicine(self, prescription: Prescription, medicine_id: int) -> bool:
        return any(item.medicine_id == medicine_id for item in prescription.items)
