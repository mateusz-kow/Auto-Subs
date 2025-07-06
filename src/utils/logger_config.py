import logging
import os
from logging.handlers import RotatingFileHandler
from src.utils.constants import LOGS_DIR

LOG_FILE = "app.log"
MAX_BYTES = 1 * 1024 * 1024
BACKUP_COUNT = 3

os.makedirs(LOGS_DIR, exist_ok=True)
log_path = os.path.join(LOGS_DIR, LOG_FILE)

formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

file_handler = RotatingFileHandler(
    filename=log_path, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)
