import pytest
from pytest_localserver.http import WSGIServer

from simon_says.app import create_app
from simon_says.client import Client
from simon_says.helpers import redis_present

#
# To run a redis instance locally for testing:
#   docker run --name my-redis -p 6379:6379 --restart always --detach redis
#
pytestmark = pytest.mark.skipif(not redis_present(), reason="redis not present")

CODE = "1234"


@pytest.fixture
def test_server(request, test_controller, test_config):
    server = WSGIServer(application=create_app(config=test_config, controller=test_controller))
    server.start()
    request.addfinalizer(server.stop)
    return server


@pytest.fixture
def test_client(test_server):
    return Client(test_server.url)


def test_get_version(test_client):
    res = test_client.get_version()
    assert res["version"]


def test_client_add_and_get_events(test_client, test_parsed_events):
    uid = "12abcd"
    for rec in test_parsed_events:
        res = test_client.add_event(data=rec)
        assert res["result"] == "OK"

    events = test_client.get_events()
    assert len(events) == 2

    event1 = test_client.get_event(uid)
    assert event1["uid"] == uid


def test_client_arm_home(test_client):
    res = test_client.arm_home(access_code=CODE)
    assert res["result"] == "OK"


def test_client_arm_away(test_client):
    res = test_client.arm_away(access_code=CODE)
    assert res["result"] == "OK"


def test_client_disarm(test_client):
    res = test_client.disarm(access_code=CODE)
    assert res["result"] == "OK"


def test_client_get_sensors(test_client):
    all_sensors = test_client.get_sensors()
    assert len(all_sensors) == 5

    sensor = test_client.get_sensor("0")
    assert sensor["name"] == "nothing"
    assert sensor["state"] == "closed"
