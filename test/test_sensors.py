import json

import pytest

from simon_says.sensors import Sensor, Sensors, SensorState


@pytest.fixture
def test_sensors(test_config_path):
    return Sensors(config_path=test_config_path)


@pytest.fixture
def all_test_sensors(test_sensors):
    all_sensors = test_sensors.get_all_sensors()
    assert len(all_sensors) == 5
    return all_sensors


def test_sensor_ops(test_sensors, all_test_sensors):
    for sensor in all_test_sensors:
        assert isinstance(sensor, Sensor)
        assert test_sensors.by_number(sensor.number) == sensor
        assert sensor.state == SensorState.CLOSED
        sensor.state = SensorState.OPEN
        assert sensor.state == SensorState.OPEN

    test_sensors.clear_all()
    for sensor in all_test_sensors:
        assert sensor.state == SensorState.CLOSED


def test_sensors_all_as_json(test_sensors):
    j_str = test_sensors.all_as_json()
    data = json.loads(j_str)
    assert len(data) == 5
