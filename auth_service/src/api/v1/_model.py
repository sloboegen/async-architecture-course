import dataclasses
from typing import Literal


@dataclasses.dataclass
class BeakFormModel:
    beak_form: str


@dataclasses.dataclass
class CreateUserData:
    beak_form: str
    name: str
    email: str
    role: str


@dataclasses.dataclass
class PatchUserRole:
    user_public_id: str
    new_role: Literal["admin", "manager", "employee"]
