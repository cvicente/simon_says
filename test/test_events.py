from pathlib import Path

import pytest

from simon_says.events import AlarmEvent, EventHandler

CWD = Path(__file__).parent
TEST_DATA_DIR = CWD / "data"


@pytest.fixture
def test_event_handler(tmp_path):
    cfg_path = TEST_DATA_DIR / "test_config.ini"
    return EventHandler(
        config_path=cfg_path,
        events_src_dir=TEST_DATA_DIR,
        events_dst_dir=Path(tmp_path),
        move_files=False,
    )


def test_process_files(test_event_handler):
    test_event_handler.process_files()
    events = test_event_handler.events
    assert len(events) == 2

    e1 = events[0]
    assert isinstance(e1, AlarmEvent)
    assert e1.uid == "12abcd"
    assert e1.account == 1234
    assert e1.extension == "simonxt"
    assert e1.code == 601
    assert e1.code_description == "Manual trigger test report Zone"
    assert e1.zone == 0
    assert e1.zone_name is None

    e2 = events[1]
    assert e2.uid == "34efgh"
    assert e2.code == 131
    assert e2.code_description == "Perimeter Zone"
    assert e2.zone == 15
    assert e2.zone_name == "front window left"
