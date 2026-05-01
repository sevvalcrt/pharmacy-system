from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: Optional[int]
    full_name: str
    username: str
    password: str
    role_id: int

    def __post_init__(self) -> None:
        self.full_name = self.full_name.strip()
        self.username = self.username.strip()
        self.password = self.password.strip()
        self._validate()

    def _validate(self) -> None:
        if not self.full_name:
            raise ValueError("Kullanici adi-soyadi bos olamaz.")
        if len(self.username) < 3:
            raise ValueError("Kullanici adi en az 3 karakter olmali.")
        if len(self.password) < 6:
            raise ValueError("Parola en az 6 karakter olmali.")
        if self.role_id not in (1, 2, 3):
            raise ValueError("Gecersiz rol ID. (1=Admin, 2=Pharmacist, 3=Cashier)")

    def check_password(self, raw_password: str) -> bool:
        return self.password == raw_password

    def has_role(self, role_id: int) -> bool:
        return self.role_id == role_id

    def to_safe_dict(self) -> dict:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "username": self.username,
            "role_id": self.role_id,
        }


@dataclass
class Admin(User):
    can_manage_users: bool = True


@dataclass
class Pharmacist(User):
    can_validate_prescriptions: bool = True


@dataclass
class Cashier(User):
    can_process_payments: bool = True


@dataclass
class Customer:
    id: int
    full_name: str
    phone: str


@dataclass
class Supplier:
    id: int
    name: str
    phone: str
    address: str


@dataclass
class Category:
    id: int
    name: str


@dataclass
class Medicine:
    id: int
    name: str
    category_id: Optional[int]
    unit_price: float
    stock: int
    expiry_date: Optional[str]


@dataclass
class Batch:
    id: int
    medicine_id: int
    supplier_id: int
    lot_number: str
    expiry_date: str


@dataclass
class Inventory:
    id: int
    medicine_id: int
    quantity_change: int
    action_type: str
    action_date: datetime


@dataclass
class Prescription:
    id: int
    customer_id: int
    doctor_name: str
    created_at: datetime


@dataclass
class PrescriptionItem:
    id: int
    prescription_id: int
    medicine_id: int
    quantity: int


@dataclass
class Sale:
    id: int
    customer_id: Optional[int]
    total_amount: float
    sale_date: str


@dataclass
class SaleItem:
    id: int
    sale_id: int
    medicine_id: int
    quantity: int
    unit_price: float
    subtotal: float


@dataclass
class Payment:
    id: int
    sale_id: int
    amount: float
    method: str


@dataclass
class Invoice:
    id: int
    sale_id: int
    invoice_number: str


@dataclass
class ReportService:
    name: str = "Report Service"


@dataclass
class DatabaseManagerEntity:
    name: str = "Database Manager Entity"
