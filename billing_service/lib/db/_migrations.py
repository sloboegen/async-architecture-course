"""Wrapper for yoyo database schema migration library."""

from yoyo import get_backend, read_migrations  # type: ignore[import-untyped]


def apply_db_migrations(db_uri: str, path_to_migrations: str) -> None:
    backend = get_backend(db_uri)
    migrations = read_migrations(path_to_migrations)

    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
