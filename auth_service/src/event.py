from typing import final


@final
class KafkaTopic:
    ACCOUNT_STREAM = "account_stream"
    ROLE_CHANGED = "role_changed"


@final
class EventName:
    USER_INFO_CHANGED = "UserInfoChanged"
    ROLE_CHANGED = "RoleChanged"
