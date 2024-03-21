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

from lib.db import DBSession
from src._types import User
from src.repos.user_repo import DBUserRepo

load_dotenv()

_DB_URI: str = os.getenv("TRACKER_DB_URI")  # type: ignore[assignment]


@final
class KafkaTopic:
    ACCOUNT_STREAM = "account_stream"
    ROLE_CHANGED = "role_changed"


logger = logging.getLogger(__name__)


def run_kafka_consumer(consumer: KafkaConsumer) -> None:
    _db_session = DBSession(_DB_URI, max_size=10)

    user_repo = DBUserRepo(_db_session)

    consumer.subscribe(topics=[KafkaTopic.ACCOUNT_STREAM, KafkaTopic.ROLE_CHANGED])

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
                data = AccountRoleChangedData.model_validate_json(event["data"])
                user_repo.modify_user_role(
                    user_id=data.user_public_id,
                    new_role=data.new_role.value,
                )

            case _:
                logger.warning(
                    "Unknown event: %s",
                    event["event_name"],
                    extra={"event_id": event["event_id"]},
                )
