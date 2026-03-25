from mysql.connector import pooling


pool = None


def init_pool(db_config):
    global pool

    if pool is not None:
        return pool

    pool = pooling.MySQLConnectionPool(
        pool_name="tg_pool",
        pool_size=5,
        **db_config,
    )
    return pool


def get_conn():
    if pool is None:
        raise RuntimeError("database pool is not initialized")

    return pool.get_connection()


def get_last_message_id(chat_id):
    conn = get_conn()

    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT last_message_id FROM sync_state WHERE chat_id=%s",
                (chat_id,),
            )
            row = cur.fetchone()

            if row:
                return row[0]

            return 0

    finally:
        conn.close()


def update_last_message_id(chat_id, message_id):
    conn = get_conn()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sync_state (chat_id, last_message_id)
                VALUES (%s, %s)

                ON DUPLICATE KEY UPDATE
                    last_message_id = GREATEST(
                        last_message_id,
                        VALUES(last_message_id)
                    )
                """,
                (chat_id, message_id),
            )

        conn.commit()

    finally:
        conn.close()


def upsert_message(conn, row):
    sql = """
    INSERT INTO messages2
      (
        chat_id,
        message_id,
        sender_id,
        ts_utc,
        text,
        has_media,
        media_path
      )
    VALUES
      (%s, %s, %s, %s, %s, %s, %s)

    ON DUPLICATE KEY UPDATE
      text=VALUES(text),
      has_media=VALUES(has_media),
      media_path=COALESCE(
        VALUES(media_path),
        media_path
      )
    """

    with conn.cursor() as cur:
        cur.execute(sql, row)

    conn.commit()


def db_worker(row):
    conn = get_conn()

    try:
        upsert_message(conn, row)

    except Exception as e:
        print(f"[WARN] MySQL write failed: {e}")

    finally:
        conn.close()
