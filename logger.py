import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from uvicorn.logging import AccessFormatter
import hashlib



RESET = "\033[0m"
WHITE = "\033[97m"


def moscow_time(*args):
    return datetime.now(ZoneInfo("Europe/Moscow")).timetuple()

logging.Formatter.converter = moscow_time


def color_ip(client_addr):
    ip, port = client_addr.split(":")

    ip_parts = ip.split(".")
    colored_ip_parts = []
    h_ip = hashlib.md5(ip.encode()).hexdigest()

    for i, part in enumerate(ip_parts):
        r = int(h_ip[i*2:i*2+2], 16)
        g = int(h_ip[(i*2+2)%32:(i*2+4)%32], 16)
        b = int(h_ip[(i*2+4)%32:(i*2+6)%32], 16)
        color = f"\033[38;2;{r};{g};{b}m"
        colored_ip_parts.append(f"{color}{part}{RESET}")

    colored_ip = f"{WHITE}.{RESET}".join(colored_ip_parts)

    h_port = hashlib.md5(port.encode()).hexdigest()
    r = int(h_port[0:2], 16)
    g = int(h_port[2:4], 16)
    b = int(h_port[4:6], 16)
    colored_port = f"\033[38;2;{r};{g};{b}m{port}{RESET}"

    return f"{colored_ip}:{colored_port}"


class AccFormatter(AccessFormatter):
    def format(self, record):
        try:
            client_addr, method, path, http_version, status_code = record.args

            new_client = color_ip(client_addr)

            record.args = (new_client, method, path, http_version, status_code)
        except Exception:
            pass

        return super().format(record)
        


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s %(levelprefix)s \n%(message)s\n",
            "datefmt": "%d-%m %H hour %M min",
        },
        "access": {
            "()": AccFormatter,
            "fmt": "%(asctime)s %(levelprefix)s \n%(client_addr)s - \"%(request_line)s\" %(status_code)s\n",
            "datefmt": "%d-%m %H hour %M min",
        },
    },

    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "access": {
            "class": "logging.StreamHandler",
            "formatter": "access",
        },
    },

    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
