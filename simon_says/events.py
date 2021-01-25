import configparser
import datetime
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from simon_says.ademco import CODES, EVENT_CATEGORIES
from simon_says.config import ConfigLoader
from simon_says.db import DataStore

logger = logging.getLogger(__name__)


class AlarmEvent(BaseModel):
    """ Represents an alarm event """

    uid: str
    timestamp: int
    extension: str
    account: int
    msg_type: int
    qualifier: int
    code: int
    code_description: str
    category: str
    partition: int
    sensor: Optional[int]
    sensor_name: Optional[str]
    user: Optional[int]
    checksum: int
    status: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """ Convert to Dict """
        return self.__dict__

    def to_json(self) -> str:
        """ Convert event to JSON """
        return json.dumps(self.to_dict())


class EventStore:
    """ A store of alarm events """

    def __init__(self, db: DataStore) -> None:
        self._namespace = "event"
        self._db = db

    def add(self, event: AlarmEvent) -> None:
        """ Add an event """

        if self._db.get(self.obj_key(event.uid)):
            raise ValueError(f"Event with uid {event.uid} already exists")

        logger.debug("Adding AlarmEvent %s to store", event.uid)
        self._db.add(self.obj_key(event.uid), event.to_json())

    def delete(self, uid: str) -> None:
        """ Delete an event given its UID """

        logger.debug("Deleting event %s", uid)
        self._db.delete(self.obj_key(uid))

    def get(self, uid: str) -> Optional[AlarmEvent]:
        """ Get AlarmEvent by UID """

        logger.debug("Getting event %s from store", uid)

        j_str = self._db.get(self.obj_key(uid))
        if not j_str:
            return None

        obj_data = json.loads(j_str)
        return AlarmEvent(**obj_data)

    def get_all_keys(self) -> List[str]:
        """ Get all keys in our namespace """

        logger.debug("Retrieving all %s keys from store", self._namespace)
        return self._db.get_all_keys(f"{self._namespace}*")

    def obj_key(self, uid: str) -> str:
        """ Return the key string used to store and retrieve event objects """

        return f"{self._namespace}:{uid}"

    def get_events(self) -> List[AlarmEvent]:
        """ Get all events in store, in chronological order """

        logger.debug("Retrieving all events from store")
        res = []
        for key in self.get_all_keys():
            obj_data = json.loads(self._db.get(key))
            res.append(AlarmEvent(**obj_data))

        return sorted(res, key=lambda x: x.timestamp)

    def events_as_json(self) -> str:
        """ Get all events as a list, in JSON format """

        logger.debug("Retrieving all events, in JSON format")
        return json.dumps([e.to_dict() for e in self.get_events()])


class EventParser:
    """
    Parse Asterisk's AlarmReceiver events
    """

    def __init__(
        self,
        config_path: Path = None,
        src_dir: Path = None,
        dst_dir: Path = None,
        move_files: bool = True,
    ) -> None:

        self.cfg = ConfigLoader(config_path).config if config_path else ConfigLoader().config
        self.src_dir = src_dir or Path(self.cfg.get("events", "src_dir"))
        self.dst_dir = dst_dir or Path(self.cfg.get("events", "dst_dir"))

        for p in (self.src_dir, self.dst_dir):
            if not p.is_dir():
                raise RuntimeError(f"Required directory {p} does not exist")

        self.move_files = move_files

    def parse_file(self, path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse an event file
        See: https://www.voip-info.org/asterisk-cmd-alarmreceiver/

        Notice that this code expects Asterisk's EventHandler config to be set with:
            logindividualevents = yes
        """

        logger.debug("Parsing event file at %s", path)
        with path.open("r") as f:
            for line in f:
                line = line.strip()

                # Verify Protocol
                proto_match = re.match(r"PROTOCOL=(.*)$", line)
                if proto_match:
                    proto_value = proto_match.group(1)
                    if proto_value != "ADEMCO_CONTACT_ID":
                        logger.warning("Invalid protocol. Skipping file {p}")
                        break

                uid = self._get_uid_from_filename(path.name)

                # Get caller extension
                x_match = re.match(r"CALLINGFROM=(.*)$", line)
                if x_match:
                    extension = x_match.group(1)

                # Get Timestamp
                t_match = re.match(r"TIMESTAMP=(.*)$", line)
                if t_match:
                    timestamp_str = t_match.group(1)
                    timestamp = self._parse_timestamp_str(timestamp_str)

                # Get event info
                fields = re.findall(r"^(\d{4})(\d{2})(\d)(\d{3})(\d{2})(\d{3})(\d)", line)
                if fields:
                    logger.debug("Event line found: %s", line)

                    account, msg_type, qualifier, code, partition, sensor_or_user, checksum = fields[0]

                    event_data = {
                        "uid": uid,
                        "timestamp": timestamp,
                        "account": account,
                        "msg_type": msg_type,
                        "qualifier": qualifier,
                        "code": int(code),
                        "code_description": CODES[code]["name"],
                        "category": self._get_event_category(int(code)),
                        "partition": partition,
                        "checksum": checksum,
                        "extension": extension,
                    }

                    self._set_sensor_or_user(event_data, int(sensor_or_user))

                    logger.debug("Event data: %s", event_data)
                    return event_data

        logger.warning("No events found in file %s", path)

    def move_file(self, src: Path) -> None:
        """ Move event file to processed folder """

        dst = self.dst_dir / src.name
        logger.debug("Moving file %s to %s", src, dst)
        src.rename(dst)

    def process_files(self) -> List[Dict[str, Any]]:
        """
        Parse all event files available in spool directory.
        Move each parsed file to another directory
        """
        results = []
        for file in self.src_dir.glob("event-*"):
            if file.is_file():
                event_data = self.parse_file(file)
                if event_data:
                    results.append(event_data)
                if self.move_files:
                    self.move_file(file)
        return results

    @staticmethod
    def _get_uid_from_filename(filename: str) -> str:
        """ Extract unique ID from filename """

        # e.g. event-1IkVo1 -> 1IkVo1
        return filename.replace("event-", "")

    @staticmethod
    def _parse_timestamp_str(timestamp: str) -> int:
        """ Convert the string timestamp coming from Asterisk into seconds from epoch"""
        # e.g
        # Sat Dec 26, 2020 @ 16:16:29 UTC => datetime.datetime(2020, 12, 26, 16, 16, 29)
        return int(datetime.datetime.strptime(timestamp, "%a %b %d, %Y @ %H:%M:%S %Z").timestamp())

    def _set_sensor_or_user(self, event_data: Dict, sensor_or_user: int) -> None:
        """ Set either sensor or user fields """

        # The Ademco standard reuses the 6th field for either sensor or user identification.
        # We look at what each code data type is and set the fields accordingly
        code = str(event_data["code"])
        data_type = CODES[code]["type"]
        if data_type == "zone":
            event_data["sensor"] = sensor_or_user
            # If there are configured sensor names, include the name
            try:
                event_data["sensor_name"] = self.cfg.get("sensors", str(sensor_or_user))
            except (KeyError, configparser.NoOptionError):
                logger.debug("Sensor %s not found in config", str(sensor_or_user))
                event_data["sensor_name"] = None
            event_data["user"] = None
        elif data_type == "user":
            event_data["user"] = sensor_or_user
            event_data["sensor"] = None
            event_data["sensor_name"] = None
        else:
            raise ValueError(f"Invalid data type {data_type}")

    @staticmethod
    def _get_event_category(code: int) -> str:
        """ Given a code number, get the ADEMCO category description """

        bases = [int(s) for s in sorted(EVENT_CATEGORIES)]
        last_base = None
        for b in bases:
            if code >= b:
                last_base = b
            elif code < b:
                break
        return EVENT_CATEGORIES[str(last_base)]
