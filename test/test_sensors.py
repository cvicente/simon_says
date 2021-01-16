import pytest

from simon_says.sensors import Sensor, Sensors, SensorState


@pytest.fixture
def test_sensor_collection(test_config_path):
    return Sensors(config_path=test_config_path)


@pytest.fixture
def all_test_sensors(test_sensor_collection):
    all_sensors = test_sensor_collection.get_all_sensors()
    assert len(all_sensors) == 5
    return all_sensors


def test_sensor_ops(test_sensor_collection, all_test_sensors):
    for sensor in all_test_sensors:
        assert isinstance(sensor, Sensor)
        assert test_sensor_collection.by_number(sensor.number) == sensor
        assert sensor.state == SensorState.CLOSED
        sensor.state = SensorState.OPEN
        assert sensor.state == SensorState.OPEN

    test_sensor_collection.clear_all()
    for sensor in all_test_sensors:
        assert sensor.state == SensorState.CLOSED
