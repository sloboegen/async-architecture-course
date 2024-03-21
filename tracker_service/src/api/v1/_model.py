import dataclasses


@dataclasses.dataclass
class TaskModified:
    new_assignee_public_id: str | None = None
    is_closed: bool = False
