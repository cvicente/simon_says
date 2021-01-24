from typing import Any, Dict, List

import requests

# This is both the connect and read timeout values
# Notice that this does not apply to the total length of the request
# See: https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
DEFAULT_TIMEOUT = 10


class Client(object):
    def __init__(self, url: str):
        self._url = url
        self._session = requests.Session()

    def arm_home(self, timeout: int = DEFAULT_TIMEOUT) -> str:
        r = self._session.post(f"{self._url}/control", json={"action": "arm_home"}, timeout=timeout)
        if r.status_code == 202:
            return r.text
        else:
            raise RuntimeError(f"Error code: {r.status_code}, content: {r.text}")

    def arm_away(self, timeout: int = DEFAULT_TIMEOUT) -> str:
        r = self._session.post(f"{self._url}/control", json={"action": "arm_away"}, timeout=timeout)
        if r.status_code == 202:
            return r.text
        else:
            raise RuntimeError(f"Error code: {r.status_code}, content: {r.text}")

    def disarm(self, timeout: int = DEFAULT_TIMEOUT) -> str:
        r = self._session.post(f"{self._url}/control", json={"action": "disarm"}, timeout=timeout)
        if r.status_code == 202:
            return r.text
        else:
            raise RuntimeError(f"Error code: {r.status_code}, content: {r.text}")

    def add_event(self, data: Dict, timeout: int = DEFAULT_TIMEOUT) -> str:
        """ Add a single event """
        r = self._session.post(f"{self._url}/events", json=data, timeout=timeout)
        if r.status_code == 201:
            return r.text
        else:
            raise RuntimeError(f"Error code: {r.status_code}, content: {r.text}")

    def get_events(self, timeout: int = DEFAULT_TIMEOUT) -> List[Dict[str, Any]]:
        """ Get all events in queue """
        r = self._session.get(f"{self._url}/events", timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            return data
        else:
            raise RuntimeError(f"Error code: {r.status_code}, content: {r.text}")

    def get_event(self, uid: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """ Get a single event given its UID """
        r = self._session.get(f"{self._url}/events/{uid}", timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            return data
        else:
            raise RuntimeError(f"Error code: {r.status_code}, content: {r.text}")
