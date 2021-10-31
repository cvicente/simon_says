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

    def get_version(self, timeout: int = DEFAULT_TIMEOUT):
        r = self._session.get(f"{self._url}/version", timeout=timeout)
        if r.status_code == 200:
            return r.json()
        else:
            raise RuntimeError(f"Error code: {r.status_code}, content: {r.text}")

    def _action(self, action: str, access_code: str, timeout: int = DEFAULT_TIMEOUT) -> str:
        r = self._session.post(
            f"{self._url}/control", json={"action": action, "access_code": access_code}, timeout=timeout
        )
        if r.status_code == 202:
            return r.json()
        else:
            raise RuntimeError(f"Error code: {r.status_code}, content: {r.text}")

    def arm_home(self, access_code: str, timeout: int = DEFAULT_TIMEOUT) -> str:
        return self._action(timeout=timeout, action="arm_home", access_code=access_code)

    def arm_away(self, access_code: str, timeout: int = DEFAULT_TIMEOUT) -> str:
        return self._action(timeout=timeout, action="arm_away", access_code=access_code)

    def disarm(self, access_code: str, timeout: int = DEFAULT_TIMEOUT) -> str:
        return self._action(timeout=timeout, action="disarm", access_code=access_code)

    def add_event(self, data: Dict, timeout: int = DEFAULT_TIMEOUT) -> str:
        """ Add a single event """
        r = self._session.post(f"{self._url}/events", json=data, timeout=timeout)
        if r.status_code == 201:
            return r.json()
        else:
            raise RuntimeError(f"Error code: {r.status_code}, content: {r.text}")

    def get_events(self, timeout: int = DEFAULT_TIMEOUT) -> List[Dict[str, Any]]:
        """ Get all events """
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

    def get_sensors(self, timeout: int = DEFAULT_TIMEOUT) -> List[Dict[str, Any]]:
        """ Get all sensors """
        r = self._session.get(f"{self._url}/sensors", timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            return data
        else:
            raise RuntimeError(f"Error code: {r.status_code}, content: {r.text}")

    def get_sensor(self, number: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """ Get a single sensor given its number """
        r = self._session.get(f"{self._url}/sensors/{number}", timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            return data
        else:
            raise RuntimeError(f"Error code: {r.status_code}, content: {r.text}")
