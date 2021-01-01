from pathlib import Path

from simon_says.events import AlarmEvent, EventQueue

CWD = Path(__file__).parent
TEST_DATA_DIR = CWD / "data"


def test_process_files(test_parsed_events):
    records = test_parsed_events
    assert len(records) == 2

    e1 = records[0]
    assert e1["uid"] == "12abcd"
    assert e1["account"] == "1234"
    assert e1["extension"] == "simonxt"
    assert e1["code"] == "601"
    assert e1["code_description"] == "Manual trigger test report Zone"
    assert e1["zone"] == "000"
    assert e1["zone_name"] is None

    e2 = records[1]
    assert e2["uid"] == "34efgh"
    assert e2["code"] == "131"
    assert e2["code_description"] == "Perimeter Zone"
    assert e2["zone"] == "015"
    assert e2["zone_name"] == "front window left"


def test_event(test_parsed_events):
    for r in test_parsed_events:
        event = AlarmEvent(**r)
        assert isinstance(event, AlarmEvent)
        assert event.to_json()


def test_event_queue(test_parsed_events):
    event_queue = EventQueue()
    for r in test_parsed_events:
        event = AlarmEvent(**r)
        event_queue.add(event)

    events = event_queue.events
    assert len(events) == 2
    assert events[0].uid == "12abcd"
    assert events[1].uid == "34efgh"

    event_queue.delete("12abcd")
    assert len(event_queue.events) == 1

    e = event_queue.get("34efgh")
    assert e.uid == "34efgh"
