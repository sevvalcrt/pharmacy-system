from __future__ import annotations

from dataclasses import dataclass
from datetime import date


class ValidationError(Exception):
    pass


@dataclass(frozen=True)
class Money:
    amount: float

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative.")


@dataclass(frozen=True)
class PhoneNumber:
    value: str

    def __post_init__(self) -> None:
        digits = self.value.strip()
        if not digits.isdigit() or len(digits) < 10:
            raise ValidationError("Phone number is invalid.")


@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        text = self.value.strip()
        if "@" not in text or "." not in text:
            raise ValidationError("Email format is invalid.")


@dataclass(frozen=True)
class Address:
    value: str

    def __post_init__(self) -> None:
        if len(self.value.strip()) < 5:
            raise ValidationError("Address is too short.")


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValidationError("Date range is invalid.")
