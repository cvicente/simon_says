import logging
import os
import sys
from typing import List

DEFAULT_LOGLEVEL = "INFO"


def configure_logging(log_level: str = None, handlers: List[logging.Handler] = None) -> None:
    """
    Configure logging
    """

    # Get root logger
    root = logging.getLogger()

    if log_level:
        # Set the level passed to this function
        root.setLevel(log_level)
    else:
        # Check if ENV log level is set, otherwise use default
        log_level = os.environ.get("SIMON_SAYS_LOGLEVEL") or DEFAULT_LOGLEVEL
        root.setLevel(log_level)
    if handlers:
        # Use the handlers passed to this function
        root.handlers = handlers
    else:
        # Or use the default handler
        root.addHandler(logging.StreamHandler(sys.stdout))
