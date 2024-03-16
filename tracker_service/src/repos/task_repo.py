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

    @override
    def get_open_tasks(self) -> list[Task]:
        """Returns all tasks that are not closed at the current moment."""

    @abstractmethod
    def add_task(self, task: Task) -> None:
        """Adds new task."""

    @abstractmethod
    def modify_task(
        self,
        task_public_id: str,
        title: str | None = None,
        assignee_public_id: str | None = None,
        is_closed: bool | None = None,
    ) -> None:
        """Modifies info about task."""


@final
class DBTaskRepo(TaskRepo):
    def __init__(self, db_session: DBSession) -> None:
        self._db_session: Final = db_session

    @override
    def get_opened_tasks(self) -> list[Task]:
        with self._db_session.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    select 
                    from tracker.task
                    where is_closed = False
                    """
                )

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
        title: str | None = None,
        assignee_public_id: str | None = None,
        is_closed: bool | None = None,
    ) -> None:
        with self._db_session.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                sql_objs = []
                args = []

                if title is not None:
                    sql_objs.append(sql.SQL("title = %s"))
                    args.append(title)

                if assignee_public_id is not None:
                    cursor.execute(
                        """
                        select id
                        from tracker.user
                        where public_id = %s
                        """,
                        (assignee_public_id,),
                    )

                    assignee_id = cursor.fetchone()["id"]

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
