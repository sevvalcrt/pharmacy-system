from __future__ import annotations

from dataclasses import dataclass

from pharmacy_detailed.base import Person, TimestampMixin


@dataclass
class User(Person, TimestampMixin):
    username: str
    password: str
    role: str

    def __post_init__(self) -> None:
        Person.__post_init__(self)
        self.username = self.username.strip()
        self.password = self.password.strip()
        self.role = self.role.strip().lower()
        if len(self.username) < 3:
            raise ValueError("Username is too short.")
        if len(self.password) < 6:
            raise ValueError("Password is too short.")

    def check_password(self, raw_password: str) -> bool:
        return self.password == raw_password


@dataclass
class Admin(User):
    can_manage_users: bool = True


@dataclass
class Pharmacist(User):
    can_validate_prescriptions: bool = True


@dataclass
class Cashier(User):
    can_process_sales: bool = True


@dataclass
class Technician(User):
    can_manage_inventory: bool = True
