# Telegram Logger

Logs Telegram messages to MySQL and JSONL, optionally downloading media and
showing desktop notifications.

## Install

```sh
pip install -r requirements.txt
cp tel_logger/config.example.py tel_logger/config.py
```

Edit `tel_logger/config.py` with your Telegram API and MySQL credentials. The
real config file is ignored by git.

## Run

```sh
python -m tel_logger
```

Flags:

- `-jn`, `--just-notify`: send notifications while backfilling, without writing
  new rows or media.
- `-jnr`, `--just-notify-running`: skip backfill and database startup, only
  notify for live incoming messages.
- `-nn`, `--no-notification`: disable desktop notifications.
