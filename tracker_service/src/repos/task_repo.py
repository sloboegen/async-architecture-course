import datetime
from abc import ABC, abstractmethod
from typing import Final, final

from psycopg import sql
from psycopg.rows import dict_row
from typing_extensions import override

from lib.db import DBSession
from src._types import Task


class TaskRepo(ABC):
    """Repository for storing task information."""

    @abstractmethod
    def fetch_task_by_public_id(self, public_id: str) -> Task | None:
        """Returns task by its public id."""

    @abstractmethod
    def fetch_opened_tasks(self) -> list[Task]:
        """Returns all tasks that are not closed at the current moment."""

    @abstractmethod
    def fetch_assigned_tasks(self, assignee_public_id: str) -> list[Task]:
        """Returns all tasks that assigned for the given users."""

    @abstractmethod
    def add_task(self, task: Task) -> None:
        """Adds new task."""

    @abstractmethod
    def modify_task(
        self,
        task_public_id: str,
        assignee_public_id: str | None = None,
        is_closed: bool | None = None,
    ) -> None:
        """Modifies info about task."""


@final
class DBTaskRepo(TaskRepo):
    def __init__(self, db_session: DBSession) -> None:
        self._db_session: Final = db_session

    @override
    def fetch_task_by_public_id(self, public_id: str) -> Task | None:
        with self._db_session.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    select t.public_id as task_public_id,
                           u.public_id as user_public_id,
                           title,
                           is_closed,
                           created_at
                    from tracker.task t
                        join tracker.user u on t.assignee_id = u.id
                    where t.public_id = %s
                    """,
                    (public_id,),
                )

                row = cursor.fetchone()
                if row is None:
                    return None

        return Task(
            public_id=row["task_public_id"],
            title=row["title"],
            assignee_public_id=row["assignee_public_id"],
            is_closed=row["is_closed"],
            created_at=row["created_at"],
        )

    @override
    def fetch_opened_tasks(self) -> list[Task]:
        with self._db_session.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    select t.public_id as task_public_id,
                           u.public_id as user_public_id,
                           title,
                           is_closed,
                           created_at
                    from tracker.task t
                        join tracker.user u on t.assignee_id = u.id
                    where is_closed = %s
                    """,
                    (False,),
                )

                if cursor.rowcount == 0:
                    return []

                rows = cursor.fetchall()

        return [
            Task(
                public_id=row["public_id"],
                title=row["title"],
                is_closed=row["is_closed"],
                assignee_public_id=row["user_public_id"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    @override
    def fetch_assigned_tasks(self, assignee_public_id: str) -> list[Task]:
        with self._db_session.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    select t.public_id as task_public_id,
                           t.title,
                           t.is_closed,
                           u.public_id as user_public_id,
                           t.created_at
                    from tracker.task t
                        join tracker.user u on t.assignee_id = u.id
                    where u.public_id = %s
                    """,
                    (assignee_public_id,),
                )

                if cursor.rowcount == 0:
                    return []

                rows = cursor.fetchall()

        return [
            Task(
                public_id=row["task_public_id"],
                title=row["title"],
                assignee_public_id=row["user_public_id"],
                is_closed=row["is_closed"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    @override
    def add_task(self, task: Task) -> None:
        with self._db_session.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                nowtime = datetime.datetime.now(tz=datetime.UTC)

                cursor.execute(
                    """
                    select id
                    from tracker.user
                    where public_id = %s
                    """,
                    (task.assignee_public_id,),
                )

                assignee_id = cursor.fetchone()["id"]  # type: ignore[index]

                cursor.execute(
                    """
                    insert into tracker.task
                        (
                            public_id,
                            title,
                            is_closed,
                            assignee_id,
                            created_at,
                            updated_at
                        )
                    values
                        (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        task.public_id,
                        task.title,
                        task.is_closed,
                        assignee_id,
                        nowtime,
                        nowtime,
                    ),
                )

    @override
    def modify_task(
        self,
        task_public_id: str,
        assignee_public_id: str | None = None,
        is_closed: bool | None = None,
    ) -> None:
        with self._db_session.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                sql_objs: list[sql.SQL] = []
                args: list[object] = []

                if assignee_public_id is not None:
                    cursor.execute(
                        """
                        select id
                        from tracker.user
                        where public_id = %s
                        """,
                        (assignee_public_id,),
                    )

                    assignee_id = cursor.fetchone()["id"]  # type: ignore[index]

                    sql_objs.append(sql.SQL("assignee_id = %s"))
                    args.append(assignee_id)

                if is_closed is not None:
                    sql_objs.append(sql.SQL("is_closed = %s"))
                    args.append(is_closed)

                sql_objs.append(sql.SQL("updated_at = %s"))
                args.append(datetime.datetime.now(tz=datetime.UTC))

                cursor.execute(
                    sql.SQL("update tracker.task set")
                    .join(sql_objs)
                    .join("where public_id = %s"),
                    (
                        *args,
                        task_public_id,
                    ),
                )
