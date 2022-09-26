from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient


@pytest.mark.pureunit
def test_endpoint(client: TestClient, db: AsyncMock):
    db.cursor.fetchall.return_value = [[42]]
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK.value
    data = response.json()
    assert data == [42]


@pytest.mark.database
def test_endpoint_with_db_query(client: TestClient):  # pragma: no cover
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK.value
    data = response.json()
    assert data == [1]
