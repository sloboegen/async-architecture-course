import dataclasses
import uuid

from blacksheep import FromJSON
from blacksheep.messages import Response
from blacksheep.server.controllers import APIController, get, patch, post
from blacksheep.server.responses import json
from kafka import KafkaProducer
from schema_registry.models.account.created.v1 import AccountCreatedData, AccountCreatedEvent
from schema_registry.models.account.role_changed.v1 import (
    AccountRoleChangedData,
    AccountRoleChangedEvent,
)

from src._types import User, UserRole
from src.event import KafkaTopic, wrap_event_data
from src.repos.user_repo import UserRepo


@dataclasses.dataclass
class CreateUserData:
    beak_form: str
    name: str
    email: str
    role: str


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
        user = user_repo.fetch_by_public_id(user_id)
        if user is None:
            return self.not_found()

        return json(user)

    @post("/")
    def create_user(
        self,
        input: FromJSON[CreateUserData],
        user_repo: UserRepo,
        kafka_producer: KafkaProducer,
    ) -> Response:
        print(kafka_producer)
        public_id = str(uuid.uuid4())

        data = input.value

        new_user = User(
            public_id=public_id,
            beak_form=data.beak_form,
            name=data.name,
            email=data.email,
            role=UserRole(data.role),
        )

        user_repo.add_user(new_user)

        event = wrap_event_data(
            AccountCreatedEvent,
            producer="auth_service",
            data=AccountCreatedData(
                public_id=new_user.public_id,
                name=new_user.name,
                email=new_user.email,
                role=new_user.role.value,
            ),
        )

        kafka_producer.send(
            topic=KafkaTopic.ACCOUNT_STREAM,
            value=event.model_dump_json(),
        )

        kafka_producer.flush()

        return self.json(
            {
                "public_id": new_user.public_id,
                "name": new_user.name,
                "beak_form": new_user.beak_form,
                "email": new_user.email,
                "role": new_user.role.value,
            }
        )

    @patch("/{user_id}")
    def patch_user(
        self,
        user_id: str,
        new_role: str,
        user_repo: UserRepo,
        kafka_producer: KafkaProducer,
    ) -> Response:
        is_ok = user_repo.modify_user_role(user_id, new_role)
        if not is_ok:
            return self.bad_request()

        # Stream this event to Kafka.
        event = wrap_event_data(
            info_cls=AccountRoleChangedEvent,
            producer="auth_service",
            data=AccountRoleChangedData(user_id, new_role),
        )

        kafka_producer.send(
            topic=KafkaTopic.ROLE_CHANGED,
            value=event.model_dump_json(),
        )

        kafka_producer.flush()

        return self.ok()
