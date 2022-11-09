from collections.abc import AsyncIterable, Mapping
from typing import Any, AsyncGenerator, Generator

from cx_Oracle import Object
from cx_Oracle_async.cursors import AsyncCursorWrapper

from fastapi_oracle.constants import DEFAULT_MAX_ROWS


def cursor_rows_as_dicts(cursor: AsyncCursorWrapper):
    """Make the specified cursor return its rows as dicts instead of tuples.

    This should be called after cursor.execute() and before cursor.fetchall().

    Thanks to: https://github.com/oracle/python-cx_Oracle/blob/main/samples/query.py
    """
    columns = [col[0] for col in cursor._cursor.description]
    cursor._cursor.rowfactory = lambda *args: dict(zip(columns, args))


async def cursor_rows_as_gen(
    cursor: AsyncCursorWrapper, max_rows: int = DEFAULT_MAX_ROWS
) -> AsyncGenerator[Any, None]:
    """Loop through the specified cursor's results in a generator."""
    i = 0

    while (row := await cursor.fetchone()) is not None and i < max_rows:
        yield row
        i += 1


def coll_records_as_dicts(coll: Object) -> Generator[dict[str, Any], None, None]:
    """Make the specified collection of records into simple dicts."""
    for record in coll.aslist():
        item = {
            type_attr.name: getattr(record, type_attr.name, None)
            for type_attr in coll.type.element_type.attributes
        }
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
