import datetime
import random
import uuid
from typing import final

from blacksheep.messages import Response
from blacksheep.server.controllers import APIController, get, patch, post

from src._types import Task
from src.repos.task_repo import TaskRepo
from src.repos.user_repo import UserRepo


@final
class TasksController(APIController):
    @classmethod
    def route(cls) -> str:
        return "api/v1/tasks"

    @get("/")
    def get_tasks(self) -> Response:
        raise NotImplementedError

    @get("/{task_id}")
    def get_task(self) -> Response:
        raise NotImplementedError

    @post("/")
    def create_task(
        self,
        title: str,
        assignee_public_id: str,
        task_repo: TaskRepo,
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

        return self.json({"task_id": public_id})

    @patch("/{task_id}")
    def update_task(self) -> Response:
        raise NotImplementedError

    @post("/shuffleAssignee")
    def shuffle_assignee(
        self,
        task_repo: TaskRepo,
        user_repo: UserRepo,
    ) -> Response:
        opened_tasks = task_repo.get_open_tasks()
        user_ids = user_repo.fetch_employee_public_ids()

        new_assignee_ids = random.choices(user_ids, k=len(opened_tasks))

        for new_assignee_id, task in zip(new_assignee_ids, opened_tasks):
            task_repo.modify_task(
                task_public_id=task.public_id,
                assignee_public_id=new_assignee_id,
            )

        return self.json({"success": True})
