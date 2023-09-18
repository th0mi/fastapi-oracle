from collections.abc import AsyncIterable, Mapping
from functools import partial
from typing import Any, AsyncGenerator, Generator

from cx_Oracle import Object
from cx_Oracle_async.cursors import AsyncCursorWrapper
from loguru import logger

from fastapi_oracle.constants import DEFAULT_MAX_ROWS, DbPoolConnAndCursor
from fastapi_oracle.errors import (
    CursorRecordCharacterEncodingError,
    RecordAttributeCharacterEncodingError,
)


def cursor_rows_as_dicts(cursor: AsyncCursorWrapper):
    """Make the specified cursor return its rows as dicts instead of tuples.

    This should be called after cursor.execute() and before cursor.fetchall().

    Thanks to: https://github.com/oracle/python-cx_Oracle/blob/main/samples/query.py
    """
    columns = [col[0] for col in cursor._cursor.description]
    cursor._cursor.rowfactory = lambda *args: dict(zip(columns, args))


async def _fetch_cursor_record(cursor: AsyncCursorWrapper) -> Any:
    try:
        return await cursor.fetchone()
    except UnicodeDecodeError as ex:
        raise CursorRecordCharacterEncodingError(
            "Character encoding error in cursor record, decoding to utf-8 failed, "
            f"error: {ex}, value: {ex.object!r}"
        )


async def cursor_rows_as_gen(
    cursor: AsyncCursorWrapper, max_rows: int = DEFAULT_MAX_ROWS
) -> AsyncGenerator[Any, None]:
    """Loop through the specified cursor's results in a generator."""
    i = 0

    while (row := await _fetch_cursor_record(cursor)) is not None:
        if i >= max_rows:
            logger.warning(
                "Max rows exceeded while looping through cursor results "
                f"(max_rows={max_rows})"
            )
            break

        yield row
        i += 1


def coll_records_as_dicts(coll: Object) -> Generator[dict[str, Any], None, None]:
    """Make the specified collection of records into simple dicts."""
    for record in coll.aslist():
        item: dict[str, Any] = {}

        for type_attr in coll.type.element_type.attributes:
            attr_name = type_attr.name

            try:
                attr_value = getattr(record, type_attr.name, None)
            except UnicodeDecodeError as ex:
                raise RecordAttributeCharacterEncodingError(
                    "Character encoding error in record attribute, decoding to utf-8 "
                    f"failed, error: {ex}, attribute: {attr_name}, value: {ex.object!r}"
                )

            item[f"{attr_name}"] = attr_value

        yield item


def row_keys_to_lower(row: Mapping[str, Any]) -> dict[str, Any]:
    """Make the keys lowercase for the specified row."""
    return {k.lower(): v for k, v in row.items()}


async def result_keys_to_lower(
    result: AsyncIterable[Mapping[str, Any]]
) -> AsyncGenerator[dict[str, Any], None]:
    """Make the keys lowercase for each row in the specified results."""
    async for row in result:
        yield row_keys_to_lower(row)


async def callproc(
    db: DbPoolConnAndCursor,
    name: str,
    parameters: list[Any] | None = None,
    keyword_parameters: dict[str, Any] | None = None,
) -> Any:  # pragma: no cover
    """Wrapper around db.cursor._cursor.callproc.

    Wouldn't be needed if this fix ever went in upstream:
    https://github.com/GoodManWEN/cx_Oracle_async/pull/21
    """
    callproc_kwargs: dict[str, Any] = {}

    if parameters is not None:
        callproc_kwargs["parameters"] = parameters
    if keyword_parameters is not None:
        callproc_kwargs["keyword_parameters"] = keyword_parameters

    return await db.cursor._loop.run_in_executor(
        db.cursor._thread_pool,
        partial(
            db.cursor._cursor.callproc,
            name,
            **callproc_kwargs,
        ),
    )


async def callfunc(
    db: DbPoolConnAndCursor,
    name: str,
    return_type: Any,
    parameters: list[Any] | None = None,
    keyword_parameters: dict[str, Any] | None = None,
) -> Any:  # pragma: no cover
    """Wrapper around db.cursor._cursor.callfunc."""
    callfunc_kwargs: dict[str, Any] = {}

    if parameters is not None:
        callfunc_kwargs["parameters"] = parameters
    if keyword_parameters is not None:
        callfunc_kwargs["keyword_parameters"] = keyword_parameters

    return await db.cursor._loop.run_in_executor(
        db.cursor._thread_pool,
        partial(
            db.cursor._cursor.callfunc,
            name,
            return_type,
            **callfunc_kwargs,
        ),
    )
