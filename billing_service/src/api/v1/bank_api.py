from typing import final

from blacksheep.messages import Response
from blacksheep.server.controllers import APIController, get


@final
class BankController(APIController):
    @classmethod
    def route(cls) -> str:
        return "api/v1/bank"

    @get("/")
    def get_payments(self) -> Response:
        raise NotImplementedError
