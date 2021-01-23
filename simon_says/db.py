import logging
from pathlib import Path
from typing import List

import redis

from simon_says.config import ConfigLoader

logger = logging.getLogger(__name__)


class DataStore:
    """ Persistence class """

    def __init__(self, config_path: Path = None) -> None:
        self.cfg = ConfigLoader(config_path).config if config_path else ConfigLoader().config
        redis_host = self.cfg.get("data_store", "redis_host")
        redis_port = self.cfg.get("data_store", "redis_port")
        logger.debug("Instantiating Redis client at %s:%s", redis_host, redis_port)
        self._redis = redis.Redis(host=redis_host, port=int(redis_port), db=0, decode_responses=True)

    def add(self, key: str, value: str) -> None:
        """ Add a record """

        logger.debug("Adding key %s to db", key)
        self._redis.execute_command("SET", key, value)

    def delete(self, key: str) -> None:
        """ Delete a record """

        logger.debug("Deleting record %s", key)
        self._redis.execute_command("DEL", key)

    def get(self, key: str) -> str:
        """ Get AlarmEvent by UID """

        logger.debug("Getting key %s from store", key)
        return self._redis.execute_command("GET", key)

    def get_all_keys(self, pattern: str) -> List[str]:
        """ Get all keys matching the given pattern """

        logger.debug("Retrieving all keys matching %s from store", pattern)
        return self._redis.execute_command(f"KEYS {pattern}")
