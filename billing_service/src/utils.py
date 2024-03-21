import random

from src._types import Task, UnpricedTask


def generate_price_task(task: UnpricedTask) -> Task:
    return Task(
        public_id=task.public_id,
        assignee_price=generate_assignee_price(task),
        complete_price=generate_assignee_price(task),
    )


def generate_assignee_price(_: UnpricedTask) -> int:
    return random.randint(10, 20)


def generate_complete_price(_: UnpricedTask) -> int:
    return random.randint(20, 40)
