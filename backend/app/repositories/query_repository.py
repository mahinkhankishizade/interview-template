from psycopg import Connection

# Repository = the ONLY place that knows SQL for the `query` table.
# Every query is parameterized with %s placeholders: values are sent to
# Postgres separately from the query text, so user input can never be
# parsed as SQL. This is the SQL-injection defense.

_COLUMNS = "id, query_text, is_input, created_at, conversation_id"


class QueryRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    def get_all(self) -> list[dict]:
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT {_COLUMNS} FROM query ORDER BY id")
            return cur.fetchall()

    def get_by_id(self, query_id: int) -> dict | None:
        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT {_COLUMNS} FROM query WHERE id = %s",
                (query_id,),  # note the trailing comma: always a tuple
            )
            return cur.fetchone()

    def get_by_conversation(self, conversation_id: int) -> list[dict]:
        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT {_COLUMNS} FROM query WHERE conversation_id = %s ORDER BY id",
                (conversation_id,),
            )
            return cur.fetchall()

    def create(
        self, query_text: str, conversation_id: int, is_input: bool
    ) -> dict:
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO query (query_text, conversation_id, is_input)
                VALUES (%s, %s, %s)
                RETURNING {_COLUMNS}
                """,
                (query_text, conversation_id, is_input),
            )
            self.conn.commit()
            return cur.fetchone()
