import pytest

from simon_says.helpers import redis_present

test_data = {
    "test:1": "foo",
    "test:2": "bar",
    "other": "baz",
}


@pytest.mark.skipif(not redis_present(), reason="redis not present")
def test_db_crud(test_db):
    for k, v in test_data.items():
        test_db.add(k, v)
        assert test_db.get(k) == v

    test_keys = test_db.get_all_keys("test:*")
    assert len(test_keys) == 2

    for k, v in test_data.items():
        test_db.delete(k)

    all_keys = test_db.get_all_keys("test:*")
    assert len(all_keys) == 0
