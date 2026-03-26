import asyncio
from datetime import datetime, timezone

from telethon import events

from tel_logger import database
from tel_logger.jsonl import append_jsonl
from tel_logger.notifications import notify


class MessageLogger:
    def __init__(self, client, args, config):
        self.client = client
        self.args = args
        self.config = config

    def register_handlers(self):
        self.client.add_event_handler(self.handle_message, events.NewMessage)

    async def handle_message(self, event):
        msg = event.message
        direction = "out" if event.out else "in"
        ts = datetime.fromtimestamp(msg.date.timestamp(), tz=timezone.utc).replace(
            tzinfo=None
        )

        media_path = await self.download_media(msg)
        name = await self.get_message_name(event, direction)

        record = {
            "chat_id": event.chat_id,
            "name": name,
            "direction": direction,
            "message_id": msg.id,
            "sender_id": msg.sender_id,
            "ts_utc": ts.isoformat(),
            "text": msg.text or msg.raw_text,
            "has_media": bool(msg.media),
            "media_path": media_path,
        }

        if direction == "in" and not self.args.no_notification:
            notify(name, record["text"], self.config.NOTIFICATION_SOUND)

        if self.args.just_notify or self.args.just_notify_running:
            return

        row = self.record_to_row(record, ts)

        asyncio.create_task(
            asyncio.to_thread(append_jsonl, self.config.JSONL_PATH, record)
        )
        asyncio.create_task(asyncio.to_thread(database.db_worker, row))

    async def backfill_chat(self, chat):
        last_id = await asyncio.to_thread(database.get_last_message_id, chat.id)

        async for msg in self.client.iter_messages(chat, min_id=last_id, reverse=True):
            direction = "out" if msg.out else "in"
            name = "you" if direction == "out" else getattr(chat, "first_name", "")
            ts = msg.date.replace(tzinfo=None)
            media_path = await self.download_media(msg)

            record = {
                "chat_id": msg.chat_id,
                "name": name,
                "direction": direction,
                "message_id": msg.id,
                "sender_id": msg.sender_id,
                "ts_utc": ts.isoformat(),
                "text": msg.text or msg.raw_text,
                "has_media": bool(msg.media),
                "media_path": media_path,
            }

            if direction == "in" and not self.args.no_notification:
                notify(name, record["text"], self.config.NOTIFICATION_SOUND)

            if self.args.just_notify:
                continue

            row = self.record_to_row(record, ts)

            await asyncio.to_thread(append_jsonl, self.config.JSONL_PATH, record)
            await asyncio.to_thread(database.db_worker, row)
            await asyncio.to_thread(database.update_last_message_id, msg.chat_id, msg.id)

    async def download_media(self, msg):
        if not msg.media:
            return None

        size = getattr(msg.file, "size", 0)
        if size > self.config.MAX_MEDIA_SIZE:
            return None

        try:
            if not (self.args.just_notify or self.args.just_notify_running):
                return await msg.download_media(file=str(self.config.MEDIA_DIR / ""))

        except Exception as e:
            print(f"[WARN] media download failed: {e}")

        return None

    async def get_message_name(self, event, direction):
        if direction == "out":
            return "you"

        chat = await event.get_chat()
        first = getattr(chat, "first_name", "") or ""
        last = getattr(chat, "last_name", "") or ""
        title = getattr(chat, "title", "") or ""

        return f"{first} {last}".strip() or title or "Unknown"

    @staticmethod
    def record_to_row(record, ts):
        return (
            record["chat_id"],
            record["message_id"],
            record["sender_id"],
            ts,
            record["text"],
            record["has_media"],
            record["media_path"],
        )
