from pathlib import Path

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import settings

# A single connection pool for the whole app. Each request borrows a
# connection and returns it. dict_row makes every fetch return dicts
# (e.g. {"id": 1, "email": "a@b.com"}) instead of tuples, which are
# far nicer to hand back to FastAPI.
pool = ConnectionPool(
    conninfo=settings.database_url,
    min_size=1,
    max_size=10,
    open=False,  # opened explicitly on startup (see main.py lifespan)
    kwargs={"row_factory": dict_row},
)


def init_schema() -> None:
    """Run schema.sql once on startup. Idempotent (CREATE TABLE IF NOT EXISTS)."""
    schema_sql = (Path(__file__).parent / "schema.sql").read_text()
    with pool.connection() as conn:
        conn.execute(schema_sql)
        conn.commit()


def get_conn():
    """FastAPI dependency: yield a pooled connection for the request."""
    with pool.connection() as conn:
        yield conn
