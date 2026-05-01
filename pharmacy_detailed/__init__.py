from __future__ import annotations

import inspect

from pharmacy_detailed.base import BaseEntity, Person, TimestampMixin
from pharmacy_detailed.catalog import Batch, Category, Manufacturer, Medicine, MedicineAlternative
from pharmacy_detailed.inventory import InventoryMovement, ReorderRule, StockAlert, StockAudit
from pharmacy_detailed.parties import Customer, Doctor, InsuranceProvider, Supplier
from pharmacy_detailed.prescriptions import Prescription, PrescriptionItem, PrescriptionValidator
from pharmacy_detailed.sales import Invoice, Payment, Refund, Sale, SaleItem
from pharmacy_detailed.services import (
    AuthService,
    BillingService,
    InventoryService,
    NotificationService,
    PrescriptionService,
    PricingService,
    ReportingService,
    SalesService,
)
from pharmacy_detailed.users import Admin, Cashier, Pharmacist, Technician, User
from pharmacy_detailed.value_objects import Address, DateRange, EmailAddress, Money, PhoneNumber


def count_project_classes() -> int:
    current_module = __import__(__name__)
    members = inspect.getmembers(current_module, inspect.isclass)
    return len([cls for _, cls in members if cls.__module__.startswith("pharmacy_detailed")])
