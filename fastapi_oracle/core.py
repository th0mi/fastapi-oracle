from typing import AsyncGenerator

from cx_Oracle_async import create_pool
from cx_Oracle_async.pools import AsyncPoolWrapper
from fastapi import Depends

from fastapi_oracle import pools
from fastapi_oracle.config import Settings, get_settings
from fastapi_oracle.constants import DbPoolAndConn, DbPoolConnAndCursor, DbPoolKey


async def get_db_pool(
    settings: Settings = Depends(get_settings),
) -> AsyncPoolWrapper:  # pragma: no cover
    """Get the DB connection pool.

    Creates a new singleton connection pool if one doesn't yet exist, otherwise returns
    the existing singleton connection pool.

    Suitable for use as a FastAPI path operation with depends().
    """
    pool_key = DbPoolKey(
        settings.db_host, settings.db_port, settings.db_user, settings.db_service_name
    )
    if pools.DB_POOLS.get(pool_key) is not None:
        return pools.DB_POOLS[pool_key]

    pools.DB_POOLS[pool_key] = await create_pool(
        host=settings.db_host,
        port=f"{settings.db_port}",
        user=settings.db_user,
        password=settings.db_password,
        service_name=settings.db_service_name,
    )
    return pools.DB_POOLS[pool_key]


async def get_db_conn(
    pool: AsyncPoolWrapper = Depends(get_db_pool),
) -> AsyncGenerator[DbPoolAndConn, None]:  # pragma: no cover
    """Get a DB connection.

    Suitable for use as a FastAPI path operation with depends().
    """
    async with pool.acquire() as conn:
        yield DbPoolAndConn(pool=pool, conn=conn)


async def get_db_cursor(
    pool_and_conn: DbPoolAndConn = Depends(get_db_conn),
) -> AsyncGenerator[DbPoolConnAndCursor, None]:  # pragma: no cover
    """Get a DB cursor.

    Suitable for use as a FastAPI path operation with depends().

    This is more convenient to use than get_db_pool() or get_db_conn(), it calls those
    for you, so you can without further ado get a cursor ready to chuck a query at.
    """
    pool, conn = pool_and_conn
    async with conn.cursor() as cursor:
        yield DbPoolConnAndCursor(pool=pool, conn=conn, cursor=cursor)


async def close_db_pools():  # pragma: no cover
    """Close the DB connection pools.

    This shouldn't need to be called manually in most cases, it's registered as a
    FastAPI shutdown function, so it will get called when the Python process ends.
    """
    for pool in pools.DB_POOLS.values():
        await pool.close()

    pools.DB_POOLS = {}
