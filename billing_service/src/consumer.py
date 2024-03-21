import json
import logging
import os
from typing import final

from dotenv import load_dotenv
from kafka import KafkaConsumer  # type: ignore[import-untyped]
from schema_registry.models.account.created.v1 import (  # type: ignore[import-untyped]
    AccountCreatedData,
)
from schema_registry.models.account.role_changed.v1 import (  # type: ignore[import-untyped]
    AccountRoleChangedData,
)
from schema_registry.models.task.assigned.v1 import TaskAssignedData
from schema_registry.models.task.closed.v1 import TaskClosedData
from schema_registry.models.task.created.v1 import TaskCreatedData

from lib.db import DBSession
from src._types import UnpricedTask, User
from src.repos.payment_repo import PaymentRepo
from src.repos.task_repo import TaskRepo
from src.repos.user_repo import UserRepo
from src.utils import generate_price_task

logger = logging.getLogger(__name__)


load_dotenv()

_DB_URI: str = os.getenv("BILLING_DB_URI")  # type: ignore[assignment]


@final
class KafkaTopic:
    ACCOUNT_STREAM = "account_stream"
    ROLE_CHANGED = "role_changed"

    TASK_CREATED = "task_created"
    TASK_ASSIGNED = "task_assigneed"
    TASK_CLOSED = "task_closed"


def run_kafka_consumer(consumer: KafkaConsumer) -> None:
    _db_session = DBSession(_DB_URI, max_size=10)

    user_repo = UserRepo(_db_session)
    task_repo = TaskRepo(_db_session)
    payment_repo = PaymentRepo(_db_session)

    consumer.subscribe(
        topics=[
            KafkaTopic.ACCOUNT_STREAM,
            KafkaTopic.ROLE_CHANGED,
            KafkaTopic.TASK_CREATED,
            KafkaTopic.TASK_ASSIGNED,
            KafkaTopic.TASK_CLOSED,
        ]
    )

    for msg in consumer:
        logger.info("Consume event", extra={"event": msg})

        json_data = msg.value.decode("utf-8")

        event = json.loads(json_data)
        event = json.loads(event)

        match event["event_name"]:
            case "AccountCreated":
                data = AccountCreatedData.model_validate(event["data"])
                user = User(
                    public_id=data.public_id,
                    name=data.name,
                    email=data.email,
                    role=data.role,
                )

                user_repo.add_user(user)

            case "AccountRoleChanged":
                data = AccountRoleChangedData.model_validate(event["data"])
                user_repo.modify_user_role(
                    user_id=data.user_public_id,
                    new_role=data.new_role.value,
                )

            case "TaskCreated":
                data = TaskCreatedData.model_validate(event["data"])
                task = generate_price_task(UnpricedTask(public_id=data.public_id))

                # TODO: Better do it in one transaction.
                task_repo.add_task(task)
                payment_repo.debit_money(data.assignee_public_id, task.assignee_price)

            case "TaskAssigneed":
                data = TaskAssignedData.model_validate(event["data"])
                task = task_repo.fetch_task_by_public_id(data.task_public_id)
                payment_repo.debit_money(data.assignee_public_id, task.assignee_price)

            case "TaskClosed":
                data = TaskClosedData.model_validate(event["data"])
                task = task_repo.fetch_task_by_public_id(data.task_public_id)
                payment_repo.credit_money(data.assignee_public_id, task.complete_price)

            case _:
                logger.warning(
                    "Unknown event: %s",
                    event["event_name"],
                    extra={"event_id": event["event_id"]},
                )
