import os
from enum import Enum, unique
from typing import Final, TypedDict, final

import requests
from dotenv import load_dotenv

# TODO: Move to client's parameters.
load_dotenv()
_AUTH_URL = os.getenv("AUTH_URL")


@unique
class UserRole(Enum):
    admin = "admin"
    manager = "manager"
    employee = "employee"


@final
class _UserData(TypedDict, total=True):
    public_id: str
    role: UserRole


class AuthClient:
    def __init__(self, token: str) -> None:
        self._session: Final = requests.Session()
        self.__token: str = token

    def verify(self) -> _UserData:
        headers = {"Authorization": f"Bearer {self.__token}"}

        response = self._session.post(
            f"{_AUTH_URL}/api/v1/auth/verify",
            headers=headers,
            timeout=(3, 10),
        )

        d = response.json()

        return {
            "public_id": d["user_id"],
            "role": UserRole(d["role"]),
        }
