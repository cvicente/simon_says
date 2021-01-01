import datetime
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from simon_says.ademco import CODES
from simon_says.config import ConfigLoader

logger = logging.getLogger(__name__)


class AlarmEvent(BaseModel):
    """ Represents an alarm event """

    uid: str
    timestamp: float
    extension: str
    account: int
    msg_type: int
    qualifier: int
    code: int
    code_description: str
    partition: int
    zone: Optional[int]
    zone_name: Optional[str]
    user: Optional[int]
    checksum: int
    status: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """ Convert to Dict """
        return self.__dict__

    def to_json(self) -> str:
        """ Convert event to JSON """
        return json.dumps(self.to_dict())


class EventQueue:
    """
    A queue of alarm events
    """

    def __init__(self) -> None:
        self._events_by_uid: Dict[str, AlarmEvent] = {}

    @property
    def events(self) -> List[AlarmEvent]:
        """ List events in queue, in order """
        return sorted(self._events_by_uid.values(), key=lambda x: x.timestamp)

    @property
    def events_as_json(self) -> str:
        return json.dumps([e.to_dict() for e in self.events])

    def add(self, event: AlarmEvent) -> None:
        """ Add an event """

        if event.uid in self._events_by_uid:
            raise ValueError(f"Event with uid {event.uid} already in queue")

        self._events_by_uid[event.uid] = event

    def delete(self, uid: str) -> None:
        """ Delete an event given its UID """

        del self._events_by_uid[uid]

    def get(self, uid: str) -> Optional[AlarmEvent]:
        """ Get AlarmEvent by UID """

        return self._events_by_uid.get(uid)


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

                    account, msg_type, qualifier, code, partition, zone_or_user, checksum = fields[0]

                    code_description = CODES[code]["name"]

                    event_data = {
                        "uid": uid,
                        "timestamp": timestamp,
                        "account": account,
                        "msg_type": msg_type,
                        "qualifier": qualifier,
                        "code": code,
                        "code_description": code_description,
                        "partition": partition,
                        "checksum": checksum,
                        "extension": extension,
                    }

                    self._set_zone_or_user(event_data, zone_or_user)

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
    def _parse_timestamp_str(timestamp: str) -> float:
        """ Convert the timestamp coming from Asterisk into a datetime object """
        # e.g
        # Sat Dec 26, 2020 @ 16:16:29 UTC => datetime.datetime(2020, 12, 26, 16, 16, 29)
        return datetime.datetime.strptime(timestamp, "%a %b %d, %Y @ %H:%M:%S %Z").timestamp()

    def _set_zone_or_user(self, event_data: Dict, zone_or_user: str) -> None:
        """ Set either zone or user fields """

        # The Ademco standard reuses the 6th field for either zone or user identification.
        # We look at what each code data type is and set the fields accordingly
        code = str(event_data["code"])
        data_type = CODES[code]["type"]
        if data_type == "zone":
            event_data["zone"] = zone_or_user
            # If there are configured zone names, include the name
            if "zones" in self.cfg and zone_or_user in self.cfg["zones"]:
                event_data["zone_name"] = self.cfg["zones"][zone_or_user]
            else:
                event_data["zone_name"] = None
            event_data["user"] = None
        elif data_type == "user":
            event_data["user"] = zone_or_user
            event_data["zone"] = None
            event_data["zone_name"] = None
        else:
            raise ValueError(f"Invalid data type {data_type}")
