from typing import final

from psycopg.rows import dict_row

from lib.db import DBSession


@final
class PaymentRepo:
    def __init__(self, db_session: DBSession) -> None:
        self._db_session: DBSession = db_session

    def credit_money(
        self,
        user_public_id: str,
        money: int,
    ) -> None:
        with self._db_session.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    select id
                    from billing.user
                    where public_id = %s
                    """,
                    (user_public_id,),
                )

                user_id = cursor.fetchone()["id"]

                cursor.execute(
                    """
                    update billing.balance
                    set money = money + %s
                    where user_id = %s
                    """,
                    (money, user_id),
                )

                cursor.execute(
                    """
                    insert into billing.payment_journal
                        (user_id, amount, op)
                    values
                        (%s, %s, %s)
                    """,
                    (user_id, money, "credit"),
                )

    def debit_money(
        self,
        user_public_id: str,
        money: int,
    ) -> None:
        with self._db_session.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    select id
                    from billing.user
                    where public_id = %s
                    """,
                    (user_public_id,),
                )

                user_id = cursor.fetchone()["id"]

                cursor.execute(
                    """
                    update billing.balance
                    set money = money - %s
                    where user_id = %s
                    """,
                    (money, user_id),
                )

                cursor.execute(
                    """
                    insert into billing.payment_journal
                        (user_id, amount, op)
                    values
                        (%s, %s, %s)
                    """,
                    (user_id, money, "debit"),
                )
