from fastapi_oracle.constants import DbPoolAndCreatedTime, DbPoolKey


# Simple singleton to cache DB connection pools for the lifetime of the app object
DB_POOLS: dict[DbPoolKey, DbPoolAndCreatedTime] = {}
