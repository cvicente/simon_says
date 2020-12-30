import logging
import sys
from pathlib import Path

DEFAULT_LOG_DIR = "/var/log/"
LOG_FILENAME = "simon_says.log"


def configure_logging(log_level: str, log_path: Path = DEFAULT_LOG_DIR) -> None:
    """
    Configure logging to log both to LOG_FILENAME and to STDOUT.
    """

    root = logging.getLogger()
    root.setLevel(log_level)

    log_file_path = log_path / LOG_FILENAME
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    file_handler.suffix = "%Y%m%d"

    stream_handler = logging.StreamHandler(sys.stdout)

    for handler in (stream_handler, file_handler):
        root.addHandler(handler)
