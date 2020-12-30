import datetime
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

from simon_says.ademco import CODES
from simon_says.config import ConfigLoader

# Default directories to read files from and move them to on the Asterisk instance
DEFAULT_EVENTS_SRC = "/var/spool/asterisk/alarm_events"
DEFAULT_EVENTS_DST = "/var/spool/asterisk/alarm_events_processed"

logger = logging.getLogger(__name__)


class AlarmEvent(BaseModel):
    """ Represents an alarm event """

    uid: str
    timestamp: datetime.datetime
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


class EventHandler:
    """
    * Parses Asterisk's AlarmReceiver events
    * Instantiates AlarmEvent objects and keeps them in memory
    """

    def __init__(
        self,
        config_path: Path = None,
        events_src_dir: Path = None,
        events_dst_dir: Path = None,
        move_files: bool = True,
    ) -> None:
        self.cfg = ConfigLoader(config_path).config if config_path else ConfigLoader().config

        self.events_src_dir = events_src_dir or self.cfg.get("events_src_dir", Path(DEFAULT_EVENTS_SRC))
        self.events_dst_dir = events_dst_dir or self.cfg.get("events_dst_dir", Path(DEFAULT_EVENTS_DST))

        for d in (self.events_src_dir, self.events_dst_dir):
            if not d.is_dir():
                raise RuntimeError(f"Required directory {d} does not exist")

        self.move_files = move_files
        self._events: List[AlarmEvent] = []

    @property
    def events(self):
        return sorted(self._events, key=lambda x: x.timestamp)

    def parse_file(self, path: Path) -> Optional[AlarmEvent]:
        """
        Parse an event file and convert it to an AlarmEvent object.
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
                        "account": int(account),
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
                    return AlarmEvent(**event_data)

        logger.warning("No events found in file %s", path)

    def _set_zone_or_user(self, event_data: Dict, zone_or_user: str) -> None:
        """ Set either zone or user fields """

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

    def move_file(self, src: Path) -> None:
        """ Move event file to processed folder """

        if not self.move_files:
            return

        dst = self.events_dst_dir / src.name
        logger.debug("Moving file %s to %s", src, dst)
        src.rename(dst)

    def process_files(self) -> None:
        """
        Parse all event files available in spool directory.
        Move each parsed file to another directory
        """
        for file in self.events_src_dir.glob("*"):
            if file.is_file():
                event = self.parse_file(file)
                if event:
                    self._events.append(event)
                self.move_file(file)

    @staticmethod
    def _get_uid_from_filename(filename: str) -> str:
        """ Extract unique ID from filename """

        # e.g. event-1IkVo1 -> 1IkVo1
        return filename.replace("event-", "")

    @staticmethod
    def _parse_timestamp_str(timestamp: str) -> datetime.datetime:
        """ Convert the timestamp coming from Asterisk into a datetime object """
        # e.g
        # Sat Dec 26, 2020 @ 16:16:29 UTC => datetime.datetime(2020, 12, 26, 16, 16, 29)
        return datetime.datetime.strptime(timestamp, "%a %b %d, %Y @ %H:%M:%S %Z")
