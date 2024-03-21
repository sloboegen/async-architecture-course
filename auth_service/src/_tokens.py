import os
from typing import Any, TypeAlias

import jwt
from dotenv import load_dotenv

from src._types import User

# TODO: Configure path to .env-file.
load_dotenv(".env.local")
_AUTHSECRET = os.getenv("AUTHSECRET")


AuthToken: TypeAlias = str


def generate_auth_token(user: User) -> AuthToken:
    return jwt.encode(
        payload={
            "user_id": user.public_id,
            "role": user.role.value,
        },
        key=_AUTHSECRET,
        algorithm="HS256",
    )


def decode_auth_token(token: str) -> dict[str, Any] | None:
    decoded = jwt.decode(
        token,
        _AUTHSECRET,
        algorithms=["HS256"],
    )

    return decoded  # type: ignore[no-any-return]
