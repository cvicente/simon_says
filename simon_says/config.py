import logging
from configparser import ConfigParser
from pathlib import Path

DEFAULT_CONFIG_PATH = Path("/etc/simon_says.ini")

logger = logging.getLogger(__name__)

DEFAULTS = {
    "data_store": {
        "redis_host": "localhost",
        "redis_port": 6379,
    },
    "events": {
        # Default directories to read files from and move them to on the Asterisk instance
        "src_dir": "/var/spool/asterisk/alarm_events",
        "dst_dir": "/var/spool/asterisk/alarm_events_processed",
    },
    "control": {
        # Default alarm access code
        "access_code": "1234",
        # SIP extension that will receive the commands via Asterisk
        "extension": "100",
        # How long to wait for the alarm to answer
        # Unfortunately it has to ring 10 times, which is roughly 1 minute.
        "wait_time": 65,
        # Wait 10 seconds between retries
        "retry_time": 10,
        # Retry this many times
        "max_retries": 2,
        # Default user that will own the call files
        "asterisk_user": "asterisk",
        # Default spool directory
        "spool_dir": "/var/spool/asterisk/outgoing",
    },
    # Default sensor (zone) names.
    "sensors": {"0": "nothing"},
}


class ConfigLoader:
    def __init__(self, cfg_path: Path = DEFAULT_CONFIG_PATH) -> None:
        self.config = ConfigParser()
        self.load_defaults()
        self.load_from_file(cfg_path)

    def load_defaults(self) -> None:
        self.config.read_dict(DEFAULTS)

    def load_from_file(self, cfg_path) -> None:
        """ Load config file """

        if cfg_path.is_file():
            self.config.read(cfg_path)
        else:
            logger.warning("No configuration file found at %s. Using defaults", cfg_path)
