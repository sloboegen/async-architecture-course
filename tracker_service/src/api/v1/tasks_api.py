import datetime
import random
import uuid
from typing import final

from blacksheep import FromJSON
from blacksheep.messages import Request, Response
from blacksheep.server.controllers import APIController, get, patch, post
from kafka import KafkaProducer  # type: ignore[import-untyped]
from schema_registry.models.task.assigned.v1 import (  # type: ignore[import-untyped]
    TaskAssignedData,
    TaskAssignedEvent,
)
from schema_registry.models.task.closed.v1 import (  # type: ignore[import-untyped]
    TaskClosedData,
    TaskClosedEvent,
)
from schema_registry.models.task.created.v1 import (  # type: ignore[import-untyped]
    TaskCreatedData,
    TaskCreatedEvent,
)

from lib.auth_client import AuthClient
from src._types import Task, UserRole
from src.api.v1._model import TaskModified
from src.event import KafkaTopic, wrap_event_data
from src.repos.task_repo import TaskRepo
from src.repos.user_repo import UserRepo


@final
class TasksController(APIController):
    @classmethod
    def route(cls) -> str:
        return "api/v1/tasks"

    @get("/")
    def get_tasks(
        self,
        request: Request,
        task_repo: TaskRepo,
    ) -> Response:
        token = request.get_first_header(b"authorization")  # type: ignore[assignment]
        token = token.decode("utf-8").replace("Bearer ", "")  # type: ignore

        auth_client = AuthClient(token)  # type: ignore[arg-type]
        user_data = auth_client.verify()

        user_tasks = task_repo.fetch_assigned_tasks(user_data["public_id"])
        tasks = [
            {
                "public_id": task.public_id,
                "title": task.title,
                "is_closed": task.is_closed,
            }
            for task in user_tasks
        ]

        return self.json(
            {"success": True, "user_id": user_data["public_id"], "tasks": tasks}
        )

    @post("/")
    def create_task(
        self,
        title: str,
        assignee_public_id: str,
        task_repo: TaskRepo,
        kafka_producer: KafkaProducer,
    ) -> Response:
        public_id = str(uuid.uuid4())

        new_task = Task(
            public_id=public_id,
            title=title,
            assignee_public_id=assignee_public_id,
            is_closed=False,
            created_at=datetime.datetime.now(tz=datetime.UTC),
        )

        task_repo.add_task(new_task)

        # Stream this event to Kafka.
        event = wrap_event_data(
            info_cls=TaskCreatedEvent,
            producer="tracker_service",
            data=TaskCreatedData(public_id, assignee_public_id),
        )

        kafka_producer.send(
            topic=KafkaTopic.TASK_CREATED,
            value=event.model_dump_json(),
        )

        return self.json({"task_id": public_id})

    @patch("/{task_id}")
    def update_task(
        self,
        task_id: str,
        task_modified: FromJSON[TaskModified],
        task_repo: TaskRepo,
        kafka_producer: KafkaProducer,
    ) -> Response:
        data = task_modified.value

        task = task_repo.fetch_task_by_public_id(task_id)
        if task is None:
            return self.not_found()

        if data.is_closed:
            task_repo.modify_task(task_id, is_closed=True)

            # Stream this event to Kafka.
            event = wrap_event_data(
                info_cls=TaskClosedEvent,
                producer="tracker_service",
                data=TaskClosedData(
                    task_public_id=task.public_id,
                    assignee_public_id=task.assignee_public_id,
                ),
            )

            kafka_producer.send(
                topic=KafkaTopic.TASK_CLOSED,
                value=event.model_dump_json(),
            )

            return self.ok()

        elif data.new_assignee_public_id is not None:
            task_repo.modify_task(
                task_id, assignee_public_id=data.new_assignee_public_id
            )

            # Stream this event to Kafka.
            event = wrap_event_data(
                info_cls=TaskAssignedEvent,
                producer="tracker_service",
                data=TaskAssignedData(
                    task_public_id=task.public_id,
                    assignee_public_id=data.new_assignee_public_id,
                ),
            )

            kafka_producer.send(
                topic=KafkaTopic.TASK_ASSIGNEED,
                value=event.model_dump_json(),
            )

            return self.ok()

        return self.bad_request(message="Unsupported update")

    @post("/shuffleAssignee")
    def shuffle_assignee(
        self,
        task_repo: TaskRepo,
        user_repo: UserRepo,
        kafka_producer: KafkaProducer,
        request: Request,
    ) -> Response:
        token = request.get_first_header(b"authorization")  # type: ignore[assignment]
        token = token.decode("utf-8").replace("Bearer ", "")  # type: ignore

        auth_client = AuthClient(token)  # type: ignore[arg-type]
        user_data = auth_client.verify()

        if user_data["role"] is UserRole.EMPLOYEE:
            return self.forbidden()

        opened_tasks = task_repo.fetch_opened_tasks()
        user_ids = user_repo.fetch_employee_public_ids()

        new_assignee_ids = random.choices(user_ids, k=len(opened_tasks))

        # TODO: Sends batches.
        for new_assignee_id, task in zip(new_assignee_ids, opened_tasks):
            task_repo.modify_task(
                task_public_id=task.public_id,
                assignee_public_id=new_assignee_id,
            )

            # Stream this event to Kafka.
            event = wrap_event_data(
                info_cls=TaskAssignedEvent,
                producer="tracker_service",
                data=TaskAssignedData(task.public_id, new_assignee_id),
            )

            kafka_producer.send(
                topic=KafkaTopic.TASK_ASSIGNEED,
                value=event.model_dump_json(),
            )

        return self.json({"success": True})
