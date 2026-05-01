from __future__ import annotations

from dataclasses import dataclass

from pharmacy_detailed.base import BaseEntity, Person
from pharmacy_detailed.value_objects import Address, EmailAddress, PhoneNumber


@dataclass
class Customer(Person):
    phone: PhoneNumber


@dataclass
class Supplier(BaseEntity):
    name: str
    phone: PhoneNumber
    email: EmailAddress
    address: Address


@dataclass
class Doctor(Person):
    license_number: str


@dataclass
class InsuranceProvider(BaseEntity):
    name: str
    policy_prefix: str
