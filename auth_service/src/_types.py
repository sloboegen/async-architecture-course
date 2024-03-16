import dataclasses
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
    beak_form: str
