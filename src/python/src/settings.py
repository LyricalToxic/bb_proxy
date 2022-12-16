import os
from distutils.util import strtobool

from dotenv import load_dotenv

from utils.project.func.configure_logging import configure_logging
from utils.project.enums import StateLoggingTriggers
from utils.constans import GiB, BYTE, MAX_BANDWIDTH, MAX_THREADS

load_dotenv()

DEFAULT_PROXY_HOST = os.getenv("DEFAULT_PROXY_HOST")
DEFAULT_PROXY_PORT = int(os.getenv("DEFAULT_PROXY_PORT") or -1)
DEFAULT_PROXY_CREDENTIALS = os.getenv("DEFAULT_PROXY_CREDENTIALS")
DEFAULT_BANDWIDTH = int(os.getenv("DEFAULT_BANDWIDTH", MAX_BANDWIDTH * (GiB // BYTE)))
DEFAULT_THREADS = int(os.getenv("DEFAULT_THREADS", MAX_THREADS))

LISTEN_PORT = int(os.getenv("LISTEN_PORT", 8081))

SECRET_KEY = os.getenv("SECRET_KEY", "secret_key").encode()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
configure_logging(LOG_LEVEL)

DB_DRIVER = os.getenv("DB_DRIVER", "sqlite")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306) or 3306)
DB_USERNAME = os.getenv("DB_USERNAME", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DATABASE = os.getenv("DB_DATABASE", "bb_proxy")

SALT_KEY = os.getenv("SALT_KEY")
if not SALT_KEY:
    raise Exception("`SALT KEY` not set")

STATISTIC_LOGGING_TIME_TRIGGER = getattr(
    StateLoggingTriggers, os.getenv("STATISTIC_LOGGING_TIME_TRIGGER", "EVERY_HOUR")
)

DB_PREPARING_ENABLED = strtobool(os.getenv("DB_PREPARING_ENABLED", "True"))
