import socket
from contextlib import closing

from simon_says.events import DEFAULT_REDIS_HOST, DEFAULT_REDIS_PORT


def port_open(host, port) -> bool:
    """ Check if TCP port is open """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return True
        else:
            return False


def redis_present() -> bool:
    """ Check if Redis service is present """
    return port_open(DEFAULT_REDIS_HOST, DEFAULT_REDIS_PORT)