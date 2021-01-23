import os
from pathlib import Path

import pytest

from simon_says.control import Controller
from simon_says.db import DataStore
from simon_says.events import EventParser
from simon_says.helpers import redis_present

CWD = Path(__file__).parent
TEST_DATA_DIR = CWD / "data"


@pytest.fixture()
def test_config_path():
    return TEST_DATA_DIR / "test_config.ini"


@pytest.mark.skipif(not redis_present(), reason="redis not present")
@pytest.fixture
def test_db():
    return DataStore()


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
def test_controller(tmp_path, test_config_path, test_db):
    return Controller(
        db=test_db,
        config_path=test_config_path,
        spool_dir=tmp_path,
        asterisk_user=os.environ.get("USER", None),
    )
