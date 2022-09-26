from cx_Oracle_async.pools import AsyncPoolWrapper

from fastapi_oracle.constants import DbPoolKey


# Simple singleton to cache DB connection pools for the lifetime of the app object
DB_POOLS: dict[DbPoolKey, AsyncPoolWrapper] = {}
