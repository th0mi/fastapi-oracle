from unittest.mock import MagicMock

import pytest

from fastapi_oracle.utils import (
    coll_records_as_dicts,
    cursor_rows_as_dicts,
    result_keys_to_lower,
)


@pytest.mark.pureunit
def test_cursor_rows_as_dicts():
    cursor = MagicMock()
    cursor._cursor.description = [["do"], ["re"], ["mi"]]
    cursor_rows_as_dicts(cursor)
    row_as_dict = cursor._cursor.rowfactory(111, 222, 333)
    assert row_as_dict == {"do": 111, "re": 222, "mi": 333}


@pytest.mark.pureunit
def test_coll_records_as_dicts():
    record1 = MagicMock()
    record1.do = 111
    record2 = MagicMock()
    record2.re = 222
    record2.mi = 333
    coll = MagicMock()
    coll.aslist.return_value = [record1, record2]

    type_attr1 = MagicMock()
    type_attr1.name = "do"
    type_attr2 = MagicMock()
    type_attr2.name = "re"
    type_attr3 = MagicMock()
    type_attr3.name = "mi"
    coll_type = MagicMock()
    coll_type.element_type.attributes = [type_attr1, type_attr2, type_attr3]

    dicts = [x for x in coll_records_as_dicts(coll, coll_type)]

    assert dicts[0]["do"] == 111
    assert dicts[1]["re"] == 222
    assert dicts[1]["mi"] == 333


@pytest.mark.pureunit
def test_result_keys_to_lower():
    result = [
        {"DO": 111, "RE": 222, "MI": 333},
        {"DO": 444, "RE": 555, "MI": 666},
    ]
    assert [x for x in result_keys_to_lower(result)] == [
        {"do": 111, "re": 222, "mi": 333},
        {"do": 444, "re": 555, "mi": 666},
    ]
