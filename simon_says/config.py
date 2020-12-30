import logging
from configparser import ConfigParser
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".simon_says.ini"

logger = logging.getLogger(__name__)


class ConfigLoader:
    def __init__(self, cfg_path: Path = DEFAULT_CONFIG_PATH) -> None:
        self._cfg_path = cfg_path
        self.config = ConfigParser()
        self.load()

    def load(self) -> None:
        """ Load config file """

        if self._cfg_path.is_file():
            self.config.read(str(self._cfg_path.resolve()))
        else:
            logger.warning("No configuration file found at %s", self._cfg_path)
