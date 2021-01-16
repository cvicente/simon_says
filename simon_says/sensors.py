import logging
from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseModel

from simon_says.config import ConfigLoader

logger = logging.getLogger(__name__)


class SensorState(Enum):
    OPEN = "open"
    CLOSED = "closed"
    BYPASSED = "bypassed"


class Sensor(BaseModel):
    """ An alarm Sensor """

    number: int
    name: str
    state: SensorState = SensorState.CLOSED


class Sensors:
    """
    A collection of Sensor objects.
    These correspond to "zones" in the Ademco nomenclature.
    """

    def __init__(self, config_path: Path = None) -> None:
        self._sensors_by_number = {}
        self.cfg = ConfigLoader(config_path).config if config_path else ConfigLoader().config
        self._load_from_config()

    def add(self, sensor: Sensor) -> None:
        """ Add a sensor to the collection """
        if sensor.number in self._sensors_by_number:
            raise ValueError("Sensor number %s already exists")

        self._sensors_by_number[sensor.number] = sensor

    def by_number(self, number) -> Sensor:
        """ Get sensor given its number """
        return self._sensors_by_number[number]

    def get_all_sensors(self) -> List[Sensor]:
        """ Get all sensors in the collection """
        return list(self._sensors_by_number.values())

    def clear_all(self) -> None:
        """ Clear all sensors (set to CLOSED state) """

        logger.debug("Clearing all sensors")
        for sensor in self.get_all_sensors():
            sensor.state = SensorState.CLOSED

    def _load_from_config(self) -> None:
        """ Load sensors into collection from config data """
        for number, name in self.cfg["sensors"].items():
            self.add(Sensor(number=number, name=name))
