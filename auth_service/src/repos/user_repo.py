from abc import ABC, abstractmethod
from typing import Final, final

from psycopg.rows import class_row
from typing_extensions import override

from lib.db import DBSession
from src._types import User


class UserRepo(ABC):
    """Repository for users data."""

    @final
    def get_by_public_id(self, public_id: str) -> User | None:
        return self.get_by_public_ids([public_id]).get(public_id)

    @abstractmethod
    def get_by_public_ids(self, public_ids: list[str]) -> dict[str, User]:
        """Returns user by public id."""

    @abstractmethod
    def get_by_beak_form(self, beak_form: str) -> User | None:
        """Returns user by beak form."""

    @abstractmethod
    def add_user(self, user: User) -> bool:
        pass

    @abstractmethod
    def modify_user(self, modified_user: User) -> bool:
        pass


@final
class DBUserRepo(UserRepo):
    def __init__(self, db_session: DBSession) -> None:
        self._db_session: Final = db_session

    @override
    def get_by_public_ids(self, public_ids: list[str]) -> dict[str, User]:
        if not public_ids:
            return {}

        with self._db_session.connection() as conn:
            with conn.cursor(row_factory=class_row(User)) as cursor:
                cursor.execute(
                    """
                    select public_id,
                           name,
                           role,
                           beak_form
                    from auth.user
                    where public_id = any(%s)
                    """,
                    (public_ids,),
                )

                if cursor.rowcount == 0:
                    return {}

                users = cursor.fetchall()

        return {user.public_id: user for user in users}

    @override
    def get_by_beak_form(self, beak_form: str) -> User | None:
        with self._db_session.connection() as conn:
            with conn.cursor(row_factory=class_row(User)) as cursor:
                cursor.execute(
                    """
                    select public_id,
                           name,
                           role,
                           beak_form
                    from auth.user
                    where beak_form = %s
                    """,
                    (beak_form,),
                )

                user = cursor.fetchone()

        return user

    @override
    def add_user(self, user: User) -> bool:
        with self._db_session.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    insert into auth.user
                        (public_id, beak_form, name, email, role)
                    values
                        (%s, %s, %s, %s, %s)
                    returning id
                    """,
                    (user.public_id, user.beak_form, user.name, user.email, user.role.value),
                )

                row_id = cursor.fetchone()

        return row_id is not None

    @override
    def modify_user(self, modified_user: User) -> bool:
        raise NotImplementedError
