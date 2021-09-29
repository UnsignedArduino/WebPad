import logging
import socket

from create_logger import create_logger

logger = create_logger(name=__name__, level=logging.DEBUG)


def get_ip_addr() -> str:
    logger.debug("Obtaining IP address")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
    return ip
