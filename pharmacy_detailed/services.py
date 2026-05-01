from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from pharmacy_detailed.catalog import Medicine
from pharmacy_detailed.prescriptions import Prescription, PrescriptionValidator
from pharmacy_detailed.sales import Payment, Sale
from pharmacy_detailed.users import User
from pharmacy_detailed.value_objects import Money


@dataclass
class AuthService:
    def login(self, users: Iterable[User], username: str, password: str) -> User:
        for user in users:
            if user.username == username and user.check_password(password):
                return user
        raise ValueError("Invalid credentials.")


@dataclass
class PricingService:
    def calculate_subtotal(self, unit_price: Money, quantity: int) -> Money:
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        return Money(unit_price.amount * quantity)


@dataclass
class SalesService:
    def complete_sale(self, sale: Sale) -> Money:
        return sale.total_amount


@dataclass
class InventoryService:
    def has_enough_stock(self, medicine: Medicine, requested_quantity: int) -> bool:
        return requested_quantity > 0 and medicine.stock >= requested_quantity


@dataclass
class ReportingService:
    def revenue_total(self, sales: List[Sale]) -> Money:
        return Money(sum(sale.total_amount.amount for sale in sales))


@dataclass
class NotificationService:
    def build_low_stock_message(self, medicine: Medicine, threshold: int) -> str:
        return f"{medicine.name} stock is below threshold {threshold}."


@dataclass
class PrescriptionService:
    validator: PrescriptionValidator

    def can_sell_medicine(self, prescription: Prescription, medicine_id: int) -> bool:
        return self.validator.validate_medicine(prescription, medicine_id)


@dataclass
class BillingService:
    def calculate_change(self, payment: Payment, total: Money) -> Money:
        if payment.amount.amount < total.amount:
            raise ValueError("Insufficient payment.")
        return Money(payment.amount.amount - total.amount)
