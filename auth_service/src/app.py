import os

from blacksheep import Application, get
from dotenv import load_dotenv

from lib.db import DBSession, apply_db_migrations
from src.api.v1 import AuthController, UserController
from src.repos.user_repo import DBUserRepo, UserRepo


load_dotenv()


# TODO: transfer to app configuration.
__DB_URI: str = os.getenv("AUTH_DB_URI")
__DB_SESSION = DBSession(__DB_URI)


def _user_repo_factory(services) -> DBUserRepo:  # type: ignore[no-untyped-def]
    return DBUserRepo(__DB_SESSION)


def get_app() -> Application:
    app = Application(show_error_details=True)

    @app.on_start
    async def _(_: Application) -> None:
        yoyo_db_uri = __DB_URI.replace("postgresql", "postgresql+psycopg")
        apply_db_migrations(yoyo_db_uri, path_to_migrations="db")

    app.register_controllers([AuthController, UserController])

    app.services.add_scoped_by_factory(_user_repo_factory, UserRepo)  # type: ignore[attr-defined]

    return app
