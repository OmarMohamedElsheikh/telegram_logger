from pathlib import Path


API_ID = 123456
API_HASH = "replace-with-your-api-hash"

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "tg_user",
    "password": "replace-with-your-db-password",
    "database": "tg_logger",
    "charset": "utf8mb4",
    "use_unicode": True,
}

MAX_MEDIA_SIZE = 50 * 1024 * 1024

JSONL_PATH = Path("messages_log.jsonl")
MEDIA_DIR = Path("media")
SESSION_NAME = "logger_session"
NOTIFICATION_SOUND = "Ed.mp3"
