import datetime
import uuid
from typing import Any, Literal, TypeAlias, TypeVar, final

from pydantic import BaseModel

__all__ = (
    "wrap_event_data",
    "KafkaTopic",
    "EventName",
    "EventProducer",
)


_ProducerName: TypeAlias = Literal["auth_service"]

_T = TypeVar("_T", bound=BaseModel)


def wrap_event_data(info_cls: type[_T], producer: _ProducerName, data: Any) -> _T:
    event_id = str(uuid.uuid4())
    event_time = datetime.datetime.now(tz=datetime.UTC)

    return info_cls(
        event_id=event_id,
        event_time=event_time,
        producer=producer,
        data=data,
    )


@final
class KafkaTopic:
    ACCOUNT_STREAM = "account_stream"
    ROLE_CHANGED = "role_changed"
