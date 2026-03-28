# Telegram Logger

A lightweight Telegram message logger built with **Telethon** and **MySQL**.

Telegram Logger performs an incremental synchronization of your Telegram chats, stores messages in a MySQL database and a JSON Lines archive, optionally downloads media files, and continues logging new messages in real time.

---

## Features

* Incremental synchronization using the last processed message ID
* Real-time logging of incoming and outgoing messages
* MySQL storage with connection pooling
* JSON Lines (`.jsonl`) message archive
* Automatic media download (configurable size limit)
* Linux desktop notifications and notification sounds
* Duplicate-safe database inserts
* Asynchronous database and file writes
* Modular package structure

---

## Project Structure

```text
.
├── README.md
├── requirements.txt
└── tel_logger
    ├── __init__.py
    ├── __main__.py          # Package entry point
    ├── app.py               # Application startup
    ├── cli.py               # Command-line interface
    ├── config.example.py    # Configuration template
    ├── database.py          # MySQL connection pool & queries
    ├── jsonl.py             # JSONL writer
    ├── messages.py          # Telegram handlers & backfill
    └── notifications.py     # Desktop notifications
```

---

## Requirements

* Python 3.10 or newer
* MySQL or MariaDB
* Linux desktop environment (for notifications)
* Telegram API credentials

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```text
Telethon
mysql-connector-python
```

Install the notification utilities (Debian/Ubuntu):

```bash
sudo apt install libnotify-bin pulseaudio-utils
```

---

## Configuration

Copy the example configuration:

```bash
cp tel_logger/config.example.py tel_logger/config.py
```

Edit `config.py` and configure:

* Telegram API ID
* Telegram API Hash
* MySQL connection settings
* Maximum media download size
* JSONL output path
* Media directory
* Notification sound

---

## Telegram API Credentials

Create your API credentials at:

https://my.telegram.org

Copy the generated values into `config.py`.

---

## Database

The application expects two tables.

### `messages2`

Stores all logged messages.

Suggested columns:

| Column     | Type     |
| ---------- | -------- |
| chat_id    | BIGINT   |
| message_id | BIGINT   |
| sender_id  | BIGINT   |
| ts_utc     | DATETIME |
| text       | TEXT     |
| has_media  | BOOLEAN  |
| media_path | TEXT     |

The primary key should uniquely identify each message, typically:

```sql
PRIMARY KEY(chat_id, message_id)
```

---

### `sync_state`

Stores the last synchronized message ID for each chat.

Suggested schema:

| Column          | Type               |
| --------------- | ------------------ |
| chat_id         | BIGINT PRIMARY KEY |
| last_message_id | BIGINT             |

---

## Running

Start the logger normally:

```bash
python -m tel_logger
```

The application will:

1. Authenticate with Telegram.
2. Incrementally synchronize all dialogs.
3. Update the synchronization state.
4. Continue monitoring Telegram for new messages.

---

## Command Line Options

### Normal Mode

```bash
python -m tel_logger
```

Performs:

* Backfill
* Live monitoring
* Database logging
* JSONL logging
* Media download
* Notifications

---

### Notification Only

```bash
python -m tel_logger --just-notify
```

Performs a complete backfill but only displays notifications.

No database writes.

No JSON logging.

No media downloads.

---

### Notification Only (Live Messages)

```bash
python -m tel_logger --just-notify-running
```

Skips the initial synchronization and only shows notifications for messages received after startup.

No database connection is required.

---

### Disable Notifications

```bash
python -m tel_logger --no-notification
```

Runs normally while suppressing desktop notifications and notification sounds.

---

## Output

### JSON Archive

Messages are appended to a JSON Lines file.

Example:

```json
{
  "chat_id": 123456789,
  "name": "Alice",
  "direction": "in",
  "message_id": 254,
  "sender_id": 987654321,
  "ts_utc": "2026-06-26T14:32:10",
  "text": "Hello",
  "has_media": false,
  "media_path": null
}
```

---

### Media

Downloaded media files are stored in the configured media directory.

Files larger than the configured maximum size are skipped.

---

## Architecture

| Module             | Responsibility                                    |
| ------------------ | ------------------------------------------------- |
| `__main__.py`      | Package entry point                               |
| `app.py`           | Initializes and starts the application            |
| `cli.py`           | Parses command-line arguments                     |
| `config.py`        | User configuration                                |
| `database.py`      | Database connection pool and queries              |
| `jsonl.py`         | JSONL logging                                     |
| `messages.py`      | Message handlers, synchronization, media download |
| `notifications.py` | Desktop notifications                             |

---

## Limitations

* Linux notification support only (`notify-send` and `paplay`).
* Message edits are not tracked.
* Deleted messages are not tracked.
* Media larger than the configured limit are ignored.
* The database schema must already exist.

---

## Future Improvements

* Automatic database schema creation
* Docker support
* Configuration using environment variables
* YAML/TOML configuration files
* Message edit tracking
* Deleted message tracking
* Retry logic for transient database failures
* Graceful shutdown waiting for pending asynchronous tasks
* Structured logging
* Unit and integration tests

---

## License

This project is released under the MIT License.
