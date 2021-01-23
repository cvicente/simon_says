import socket
from contextlib import closing

from simon_says.config import ConfigLoader

config = ConfigLoader().config


def port_open(host, port) -> bool:
    """ Check if TCP port is open """
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex((host, port)) == 0:
                return True
            else:
                return False
    except socket.gaierror:
        return False


def redis_present() -> bool:
    """ Check if Redis service is present """
    return port_open(config.get("data_store", "redis_host"), int(config.get("data_store", "redis_port")))
