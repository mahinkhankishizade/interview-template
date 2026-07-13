from psycopg import Connection

# Repository = the ONLY place that knows SQL for the `users` table.
# Every query is parameterized with %s placeholders: values are sent to
# Postgres separately from the query text, so user input can never be
# parsed as SQL. This is the SQL-injection defense.


class UserRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    def get_all(self) -> list[dict]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, full_name, created_at FROM users ORDER BY id"
            )
            return cur.fetchall()

    def get_by_id(self, user_id: int) -> dict | None:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, full_name, created_at FROM users WHERE id = %s",
                (user_id,),  # note the trailing comma: always a tuple
            )
            return cur.fetchone()

    def get_by_email(self, email: str) -> dict | None:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, full_name, created_at FROM users WHERE email = %s",
                (email,),
            )
            return cur.fetchone()

    def create(self, email: str, full_name: str) -> dict:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (email, full_name)
                VALUES (%s, %s)
                RETURNING id, email, full_name, created_at
                """,
                (email, full_name),
            )
            self.conn.commit()
            return cur.fetchone()
