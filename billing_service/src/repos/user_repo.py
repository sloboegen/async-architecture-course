from typing import Final, final

from psycopg.rows import dict_row

from lib.db import DBSession
from src._types import User, UserRole


@final
class UserRepo:
    """Repository for users data."""

    def __init__(self, db_session: DBSession) -> None:
        self._db_session: Final = db_session

    def fetch_by_public_id(self, public_id: str) -> User | None:
        return self.fetch_by_public_ids([public_id]).get(public_id)

    def fetch_by_public_ids(self, public_ids: list[str]) -> dict[str, User]:
        if not public_ids:
            return {}

        with self._db_session.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    select public_id,
                           name,
                           email,
                           role,
                           beak_form
                    from tracker.user
                    where public_id = any(%s)
                    """,
                    (public_ids,),
                )

                if cursor.rowcount == 0:
                    return {}

                rows = cursor.fetchall()

        return {
            row["public_id"]: User(
                public_id=row["public_id"],
                name=row["name"],
                email=row["email"],
                role=UserRole(row["role"]),
            )
            for row in rows
        }

    def add_user(self, user: User) -> None:
        with self._db_session.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    insert into tracker.user
                        (public_id, name, email, role)
                    values
                        (%s, %s, %s, %s)
                    """,
                    (user.public_id, user.name, user.email, user.role.value),
                )

    def modify_user_role(self, user_id: str, new_role: UserRole) -> bool:
        with self._db_session.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    update tracker.user
                    set role = %s
                    where public_id = %s
                    """,
                    (user_id, new_role.value),
                )

                return bool(cursor.rowcount == 1)
