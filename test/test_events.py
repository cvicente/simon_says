import json
from pathlib import Path

import pytest

from simon_says import events as under_test
from simon_says.ademco import EVENT_CATEGORIES
from simon_says.helpers import redis_present

CWD = Path(__file__).parent
TEST_DATA_DIR = CWD / "data"


def test_process_files(test_parsed_events):
    records = test_parsed_events
    assert len(records) == 2

    e1 = records[0]
    assert e1["uid"] == "12abcd"
    assert e1["account"] == "1234"
    assert e1["extension"] == "simonxt"
    assert e1["code"] == 601
    assert e1["code_description"] == "Manual trigger test report"
    assert e1["category"] == "Test/Misc"
    assert e1["sensor"] == 0
    assert e1["sensor_name"] == "nothing"

    e2 = records[1]
    assert e2["uid"] == "34efgh"
    assert e2["code"] == 131
    assert e2["code_description"] == "Perimeter"
    assert e2["category"] == "Alarms"
    assert e2["sensor"] == 15
    assert e2["sensor_name"] == "front window left"


def test_event(test_parsed_events):
    for r in test_parsed_events:
        event = under_test.AlarmEvent(**r)
        assert isinstance(event, under_test.AlarmEvent)
        assert event.sensor in [0, 15]
        assert json.loads(event.to_json())


@pytest.mark.skipif(not redis_present(), reason="redis not present")
def test_event_store(test_parsed_events, test_db):

    # Create a new event store for testing
    event_store = under_test.EventStore(db=test_db)

    for r in test_parsed_events:
        # Delete it first if it exists from previous tests
        o = event_store.get(r["uid"])
        if o:
            event_store.delete(r["uid"])

        # Create the object
        event = under_test.AlarmEvent(**r)

        # Add it to store
        event_store.add(event)

        # Retrieve it
        e = event_store.get(r["uid"])
        assert e.uid == r["uid"]

    # Get all events
    events = event_store.get_events()
    assert len(events) == 2

    # Clean up
    for r in test_parsed_events:
        event_store.delete(r["uid"])


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (123, EVENT_CATEGORIES["100"]),
        (234, EVENT_CATEGORIES["200"]),
        (345, EVENT_CATEGORIES["300"]),
        (456, EVENT_CATEGORIES["400"]),
        (567, EVENT_CATEGORIES["500"]),
        (678, EVENT_CATEGORIES["600"]),
    ],
)
def test_event_category(test_input, expected):
    assert under_test.EventParser._get_event_category(test_input) == expected
