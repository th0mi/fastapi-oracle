from collections.abc import Mapping, Sequence
from typing import Any, Generator

from cx_Oracle import Object, ObjectType
from cx_Oracle_async.cursors import AsyncCursorWrapper


def cursor_rows_as_dicts(cursor: AsyncCursorWrapper):
    """Make the specified cursor return its rows as dicts instead of tuples.

    This should be called after cursor.execute() and before cursor.fetchall().

    Thanks to: https://github.com/oracle/python-cx_Oracle/blob/main/samples/query.py
    """
    columns = [col[0] for col in cursor._cursor.description]
    cursor._cursor.rowfactory = lambda *args: dict(zip(columns, args))


def coll_records_as_dicts(
    coll: Object, coll_type: ObjectType
) -> Generator[dict[str, Any], None, None]:
    """Make the specified collection of records into simple dicts."""
    for record in coll.aslist():
        item = {
            type_attr.name: getattr(record, type_attr.name, None)
            for type_attr in coll_type.element_type.attributes
        }
        yield item


def row_keys_to_lower(row: Mapping[str, Any]) -> dict[str, Any]:
    """Make the keys lowercase for the specified row."""
    return {k.lower(): v for k, v in row.items()}


def result_keys_to_lower(
    result: Sequence[Mapping[str, Any]]
) -> Generator[dict[str, Any], None, None]:
    """Make the keys lowercase for each row in the specified results."""
    return (row_keys_to_lower(row) for row in result)
