import os
from pathlib import Path

import pytest

from simon_says.control import Controller
from simon_says.events import EventParser

CWD = Path(__file__).parent
TEST_DATA_DIR = CWD / "data"


@pytest.fixture()
def test_config_path():
    return TEST_DATA_DIR / "test_config.ini"


@pytest.fixture
def test_event_parser(tmp_path, test_config_path):

    parser = EventParser(
        config_path=test_config_path,
        src_dir=TEST_DATA_DIR,
        dst_dir=Path(tmp_path),
        move_files=False,
    )
    return parser


@pytest.fixture
def test_parsed_events(test_event_parser):
    records = test_event_parser.process_files()
    records = sorted(records, key=lambda x: x["timestamp"])
    return records


@pytest.fixture
def test_controller(tmp_path, test_config_path):
    return Controller(
        config_path=test_config_path,
        access_code="123",
        extension="100",
        spool_dir=tmp_path,
        asterisk_user=os.environ.get("USER", None),
    )
