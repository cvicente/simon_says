import argparse

from simon_says.events import EventHandler
from simon_says.helpers import configure_logging


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description="Alarm Events Handler")
    parser.add_argument("-l", "--log-level", default="INFO", choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"))
    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()
    configure_logging(args.log_level)
    EventHandler().process_files()
