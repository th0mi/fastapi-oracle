from contextlib import asynccontextmanager
from typing import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from fastapi_oracle import DbPoolAndConn, close_db_pools, get_db_conn


@pytest.fixture(scope="session")
def app() -> Generator:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield

        await close_db_pools()

    _app = FastAPI(lifespan=lifespan)

    @_app.get("/")
    async def db_test_route(db: DbPoolAndConn = Depends(get_db_conn)):
        return await db.conn.fetchone("SELECT 1 FROM dual")

    yield _app


@pytest.fixture(scope="module")
def client(app: FastAPI) -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db(app: FastAPI) -> Generator:
    _db = AsyncMock()
    app.dependency_overrides[get_db_conn] = lambda: _db
    yield _db
    del app.dependency_overrides[get_db_conn]
