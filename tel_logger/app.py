import asyncio

from telethon import TelegramClient

from tel_logger import config, database
from tel_logger.cli import parse_args
from tel_logger.messages import MessageLogger


async def main():
    args = parse_args()

    config.MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    if not args.just_notify_running:
        try:
            database.init_pool(config.DB_CONFIG)
        except Exception:
            print("MySQL Connection faild please checkout is it running and try again")
            raise SystemExit(1)

    client = TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH)
    logger = MessageLogger(client, args, config)
    logger.register_handlers()

    await client.start()

    if not args.just_notify_running:
        print("Starting incremental backfill...")

        async for dialog in client.iter_dialogs():
            try:
                await logger.backfill_chat(dialog.entity)

            except Exception as e:
                print(f"[WARN] backfill failed for {dialog.id}: {e}")

        print("Backfill complete.")

    else:
        print("Skipping backfill (--just-notify-running).")

    print("Live logger running...")

    await client.run_until_disconnected()


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nstopped")
