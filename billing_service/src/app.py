import json
import os
import threading

from blacksheep import Application
from dotenv import load_dotenv
from kafka import KafkaConsumer, KafkaProducer  # type: ignore[import-untyped]

from lib.db import DBSession, apply_db_migrations
from src.api.v1 import BankController
from src.consumer import run_kafka_consumer
from src.repos.task_repo import TaskRepo
from src.repos.user_repo import UserRepo

load_dotenv()


# TODO: transfer to app configuration.
__DB_URI: str = os.getenv("BILLING_DB_URI")  # type: ignore[assignment]
__DB_SESSION = DBSession(__DB_URI, max_size=10)
__KAFKA_ADDRESS = os.getenv("KAFKA_ADDRESS")


def _user_repo_factory(services) -> UserRepo:  # type: ignore[no-untyped-def]
    return UserRepo(__DB_SESSION)


def _task_repo_factory(services) -> TaskRepo:  # type: ignore[no-untyped-def]
    return TaskRepo(__DB_SESSION)


def _event_producer_factory(services) -> KafkaProducer:  # type: ignore[no-untyped-def]
    return KafkaProducer(
        bootstrap_servers=[__KAFKA_ADDRESS],
        value_serializer=lambda _: json.dumps(_).encode("utf-8"),
    )


def get_app() -> Application:
    app = Application(show_error_details=True)

    app.register_controllers([BankController])

    app.services.add_scoped_by_factory(_user_repo_factory, UserRepo)  # type: ignore[attr-defined]
    app.services.add_scoped_by_factory(_task_repo_factory, TaskRepo)  # type: ignore[attr-defined]

    app.services.add_scoped_by_factory(_event_producer_factory, KafkaProducer)  # type: ignore[attr-defined]

    @app.on_start
    async def _(_: Application) -> None:
        yoyo_db_uri = __DB_URI.replace("postgresql", "postgresql+psycopg")
        apply_db_migrations(yoyo_db_uri, path_to_migrations="db")

        kafka_consumer = KafkaConsumer(
            bootstrap_servers=[__KAFKA_ADDRESS], api_version=(7, 3, 2)
        )

        consumer_thread = threading.Thread(
            target=run_kafka_consumer,
            args=(kafka_consumer,),
        )
        consumer_thread.start()

    return app
