import logging

from dotenv import load_dotenv
import os

from utils.project.configure_logging import configure_logging
from utils.types_.constans import GiB, BYTE, MAX_BANDWIDTH, MAX_THREADS

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
