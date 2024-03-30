from blacksheep import FromJSON
from blacksheep.messages import Request, Response
from blacksheep.server.controllers import APIController, post

from src._tokens import decode_auth_token, generate_auth_token
from src.api.v1._model import BeakFormModel
from src.repos.user_repo import UserRepo


class AuthController(APIController):
    @classmethod
    def route(cls) -> str:
        return "/api/v1/auth"

    @post("login")
    def login(
        self,
        beak_form: FromJSON[BeakFormModel],
        user_repo: UserRepo,
    ) -> Response:
        user = user_repo.fetch_by_beak_form(beak_form.value.beak_form)
        if user is None:
            return self.unauthorized()

        token = generate_auth_token(user)
        return self.json({"success": True, "token": token})

    @post("verify")
    def verify(
        self,
        request: Request,
    ) -> Response:
        header_value = request.get_first_header(b"Authorization")
        token = header_value.decode("utf-8").replace("Bearer ", "")  # type: ignore[union-attr]

        decoded = decode_auth_token(token)

        return self.json(decoded)
