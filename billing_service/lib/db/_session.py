from typing import TypeAlias

from psycopg_pool import ConnectionPool

DBSession: TypeAlias = ConnectionPool
