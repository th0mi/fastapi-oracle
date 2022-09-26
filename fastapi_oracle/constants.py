from typing import NamedTuple

from cx_Oracle_async.connections import AsyncConnectionWrapper
from cx_Oracle_async.cursors import AsyncCursorWrapper
from cx_Oracle_async.pools import AsyncPoolWrapper


class DbPoolAndConn(NamedTuple):
    pool: AsyncPoolWrapper
    conn: AsyncConnectionWrapper


class DbPoolConnAndCursor(NamedTuple):
    pool: AsyncPoolWrapper
    conn: AsyncConnectionWrapper
    cursor: AsyncCursorWrapper


class DbPoolKey(NamedTuple):
    db_host: str
    db_port: int
    db_user: str
    db_service_name: str
