from psycopg import Connection

# Repository = the ONLY place that knows SQL for the `conversations` table.
# Every query is parameterized with %s placeholders: values are sent to
# Postgres separately from the query text, so user input can never be
# parsed as SQL. This is the SQL-injection defense.

_COLUMNS = "id, quality_metric, created_at, llm_model"


class ConversationRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    def get_all(self) -> list[dict]:
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT {_COLUMNS} FROM conversations ORDER BY id")
            return cur.fetchall()

    def get_by_id(self, conversation_id: int) -> dict | None:
        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT {_COLUMNS} FROM conversations WHERE id = %s",
                (conversation_id,),  # note the trailing comma: always a tuple
            )
            return cur.fetchone()

    def create(self, llm_model: str = "A") -> dict:
        # llm_model is chosen when the conversation starts. quality_metric
        # stays NULL until the conversation is scored; id/created_at come from
        # their column defaults.
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO conversations (llm_model)
                VALUES (%s)
                RETURNING {_COLUMNS}
                """,
                (llm_model,),
            )
            self.conn.commit()
            return cur.fetchone()

    def set_quality_metric(
        self, conversation_id: int, quality_metric: bool
    ) -> dict | None:
        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE conversations
                SET quality_metric = %s
                WHERE id = %s
                RETURNING {_COLUMNS}
                """,
                (quality_metric, conversation_id),
            )
            self.conn.commit()
            return cur.fetchone()
