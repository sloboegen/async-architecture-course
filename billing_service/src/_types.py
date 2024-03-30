import dataclasses
from enum import Enum, unique


@unique
class UserRole(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


@dataclasses.dataclass(frozen=True, kw_only=True)
class User:
    public_id: str
    name: str
    email: str
    role: UserRole


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnpricedTask:
    public_id: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class Task(UnpricedTask):
    assignee_price: int
    complete_price: int
