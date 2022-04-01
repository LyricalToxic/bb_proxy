from dotenv import load_dotenv
import os

from utils.project.configure_logging import configure_logging
from utils.project.enums import StateLoggingTriggers
from utils.types_.constans import GiB, BYTE, MAX_BANDWIDTH, MAX_THREADS
from distutils.util import strtobool

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
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USERNAME = os.getenv("DB_USERNAME", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DATABASE = os.getenv("DB_DATABASE", "db_name1")

SALT_KEY = os.getenv("SALT_KEY", "7244fe69f96714e4c0269492bb0e9d1e51740f77f27d03c9cd23c7e37ef05c10")

STATISTIC_LOGGING_TIME_TRIGGER = getattr(
    StateLoggingTriggers, os.getenv("STATISTIC_LOGGING_TIME_TRIGGER", "EVERY_HOUR")
)

DB_PREPARING_ENABLED = strtobool(os.getenv("DB_PREPARING_ENABLED", "True"))
