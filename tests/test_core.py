from http import HTTPStatus
from unittest.mock import AsyncMock, patch

import pytest
from cx_Oracle import DatabaseError
from fastapi.testclient import TestClient

from fastapi_oracle.core import handle_db_errors
from fastapi_oracle.errors import (
    IntermittentDatabaseError,
    PackageStateInvalidatedError,
    ProgramUnitNotFoundError,
)


@pytest.mark.pureunit
def test_endpoint(client: TestClient, db: AsyncMock):
    db.cursor.fetchall.return_value = [[42]]
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK.value
    data = response.json()
    assert data == [42]


@handle_db_errors
async def handle_db_errors_test_func():
    return 42


@pytest.mark.pureunit
@pytest.mark.asyncio
async def test_handle_db_errors():
    ret = await handle_db_errors_test_func()

    assert ret == 42


@handle_db_errors
async def handle_db_errors_program_unit_not_found_test_func():
    raise ProgramUnitNotFoundError("ouch")


@pytest.mark.pureunit
@pytest.mark.asyncio
@patch("fastapi_oracle.core.close_db_pools")
async def test_handle_db_errors_program_unit_not_found_raised(mock_close_db_pools):
    with pytest.raises(IntermittentDatabaseError) as exc_info:
        await handle_db_errors_program_unit_not_found_test_func()

    assert "intermittent database error occurred" in str(exc_info.value)


@handle_db_errors
async def handle_db_errors_package_state_invalidated_test_func():
    raise PackageStateInvalidatedError("ouch")


@pytest.mark.pureunit
@pytest.mark.asyncio
@patch("fastapi_oracle.core.close_db_pools")
async def test_handle_db_errors_package_state_invalidated_raised(mock_close_db_pools):
    with pytest.raises(IntermittentDatabaseError) as exc_info:
        await handle_db_errors_package_state_invalidated_test_func()

    assert "intermittent database error occurred" in str(exc_info.value)


@handle_db_errors
async def handle_db_errors_unknown_db_error_test_func():
    raise DatabaseError("footastic")


@pytest.mark.pureunit
@pytest.mark.asyncio
async def test_handle_db_errors_unknown_db_error_raised():
    with pytest.raises(DatabaseError) as exc_info:
        await handle_db_errors_unknown_db_error_test_func()

    assert "footastic" in str(exc_info.value)


@handle_db_errors
async def handle_db_errors_close_pool_and_fail_test_func(error_msg):
    raise DatabaseError(error_msg)


@pytest.mark.pureunit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["error_msg"],
    [
        ("foo could not find program unit being called moo",),
        ("foo existing state of packages has been discarded moo",),
        ('foo existing state of package body "WOO" has been invalidated moo',),
        ("foo no listener moo",),
        ("foo not connected moo",),
        ("foo connection was closed moo",),
    ],
)
@patch("fastapi_oracle.core.close_db_pools")
async def test_do_db_call_close_pool_and_fail(mock_close_db_pools, error_msg):
    with pytest.raises(IntermittentDatabaseError) as exc_info:
        await handle_db_errors_close_pool_and_fail_test_func(error_msg)

    assert "intermittent database error occurred" in str(exc_info.value)


@pytest.mark.database
def test_endpoint_with_db_query(client: TestClient):  # pragma: no cover
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK.value
    data = response.json()
    assert data == [1]
