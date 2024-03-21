from typing import final

from psycopg.rows import dict_row

from lib.db import DBSession
from src._types import Task


@final
class TaskRepo:
    def __init__(self, db_session: DBSession) -> None:
        self._db_session: DBSession = db_session

    def fetch_task_by_public_id(self, public_id: str) -> Task | None:
        with self._db_session.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    select public_id,
                           assignee_price,
                           complete_price
                    from billing.task
                    where public_id = %s
                    """,
                    (public_id,),
                )

                row = cursor.fetchone()
                if row is None:
                    return None

        return Task(
            public_id=row["public_id"],
            assignee_price=row["assignee_price"],
            complete_price=row["complete_price"],
        )

    def add_task(self, task: Task) -> None:
        with self._db_session.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    insert into billing.task
                        (public_id, assignee_price, complete_price)
                    values
                        (%s, %s, %s)
                    """,
                    (task.public_id, task.assignee_price, task.complete_price),
                )
