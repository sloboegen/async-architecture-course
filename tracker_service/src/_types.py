import dataclasses
import datetime
import enum


@enum.unique
class UserRole(enum.Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
    MANAGER = "manager"


@dataclasses.dataclass(frozen=True, kw_only=True)
class User:
    public_id: str
    name: str
    email: str
    role: UserRole


@dataclasses.dataclass(frozen=True, kw_only=True)
class Task:
    public_id: str
    title: str
    assignee_public_id: str
    is_closed: bool
    created_at: datetime.datetime
