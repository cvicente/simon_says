import logging
import sys
from typing import List

DEFAULT_HANDLER = logging.StreamHandler(sys.stdout)


def configure_logging(log_level: str = "INFO", handlers: List[logging.Handler] = None) -> None:
    """
    Configure logging
    """

    root = logging.getLogger()
    root.setLevel(log_level)
    if handlers:
        root.handlers = handlers
    else:
        root.addHandler(DEFAULT_HANDLER)
