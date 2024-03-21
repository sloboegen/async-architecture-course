# generated by datamodel-codegen:
#   filename:  v1.json
#   timestamp: 2024-03-21T00:48:42+00:00

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from typing_extensions import Literal


class TaskClosedData(BaseModel):
    task_public_id: str
    assignee_public_id: str


class TaskClosedEvent(BaseModel):
    event_id: str
    event_version: Literal[1] = 1
    event_name: Literal['TaskClosed'] = 'TaskClosed'
    event_time: datetime
    producer: str
    data: TaskClosedData