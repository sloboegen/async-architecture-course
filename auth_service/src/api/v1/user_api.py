import dataclasses

from blacksheep.messages import Response
from blacksheep.server.controllers import APIController, get, patch
from blacksheep.server.responses import json
from kafka import KafkaProducer

from src._types import UserRole
from src.event import EventName, KafkaTopic
from src.repos.user_repo import UserRepo


@dataclasses.dataclass
class PatchUserRole:
    user_public_id: str
    new_role: UserRole


class UserController(APIController):
    @classmethod
    def route(cls) -> str:
        return "api/v1/users"

    @get("/")
    def get_users(self) -> Response:
        raise NotImplementedError

    @get("/{user_id}")
    def get_user(
        self,
        user_id: str,
        user_repo: UserRepo,
    ) -> Response:
        user = user_repo.get_by_public_id(user_id)
        if user is None:
            return self.not_found()

        return json(user)

    @patch("/{user_id}")
    def patch_user(
        self,
        user_id: str,
        new_role: str,
        user_repo: UserRepo,
        producer: KafkaProducer,
    ) -> Response:
        # is_ok = user_repo.modify_user_role(user_id, new_role)
        # if not is_ok:
        #     return self.bad_request()

        # Stream this event to Kafka.
        producer.send(
            topic=KafkaTopic.ROLE_CHANGED,
            value={
                "name": EventName.ROLE_CHANGED,
                "user_id": user_id,
                "new_role": new_role,
            },
        )

        producer.flush()

        return self.ok()
