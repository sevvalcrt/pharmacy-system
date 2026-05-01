from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BaseEntity:
    id: int


@dataclass
class TimestampMixin:
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def touch(self) -> None:
        self.updated_at = datetime.now()


@dataclass
class Person(BaseEntity):
    full_name: str

    def __post_init__(self) -> None:
        self.full_name = self.full_name.strip()
        if len(self.full_name) < 3:
            raise ValueError("Full name is too short.")
