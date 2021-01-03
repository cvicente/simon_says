import pytest
from pytest_localserver.http import WSGIServer

from simon_says.app import create_app
from simon_says.client import Client


@pytest.fixture
def test_server(request, test_controller):
    server = WSGIServer(application=create_app(controller=test_controller))
    server.start()
    request.addfinalizer(server.stop)
    return server


@pytest.fixture
def test_client(test_server):
    return Client(test_server.url)


def test_client_add_and_get_events(test_client, test_parsed_events):
    uid = "12abcd"
    for rec in test_parsed_events:
        res = test_client.add_event(data=rec)
        assert res == '{"result": "OK"}'

    events = test_client.get_events()
    assert len(events) == 2

    event1 = test_client.get_event(uid)
    assert event1["uid"] == uid


def test_client_disarm(test_client):
    res = test_client.disarm()
    assert res == '{"result": "OK"}'


def test_client_arm_home(test_client):
    res = test_client.arm_home()
    assert res == '{"result": "OK"}'


def test_client_arm_away(test_client):
    res = test_client.arm_away()
    assert res == '{"result": "OK"}'
