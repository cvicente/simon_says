import falcon
import pytest
from falcon import testing

from simon_says.app import create_app


@pytest.fixture
def client(test_controller):
    app = create_app(controller=test_controller)
    return testing.TestClient(app)


def test_post_and_get_events(client, test_parsed_events):
    uid = "12abcd"
    for rec in test_parsed_events:
        res = client.simulate_post("/events", json=rec)
        assert res.status == falcon.HTTP_CREATED

    response = client.simulate_get("/events")
    assert response.status == falcon.HTTP_OK

    result = response.json
    assert len(result) == 2
    e1 = result[0]
    assert e1["uid"] == uid

    response = client.simulate_get(f"/events/{uid}")
    result = response.json
    assert result["uid"] == uid


def test_controller_disarm(client, tmp_path):

    data = {"action": "disarm"}
    resp = client.simulate_post("/command", json=data)
    assert resp.status == falcon.HTTP_ACCEPTED

    call_file = next(tmp_path.iterdir())
    lines = call_file.read_text().splitlines()
    assert lines[5] == "Data: ww123w1w9"
    call_file.unlink()
