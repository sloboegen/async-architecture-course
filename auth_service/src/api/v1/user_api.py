from blacksheep.messages import Response
from blacksheep.server.controllers import APIController, get, patch, post

from src._types import User
from src.repos.user_repo import UserRepo


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

        return user

    @post("/")
    def create_user(self) -> Response:
        raise NotImplementedError

    @patch("/{user_id}")
    def patch_user(self, user_id: str) -> Response:



        raise NotImplementedError
