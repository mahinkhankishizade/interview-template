from fastapi import APIRouter, Depends
from psycopg import Connection

from app.db import get_conn

router = APIRouter(tags=["health"])


@router.get("/health")
def health(conn: Connection = Depends(get_conn)):
    """Liveness + DB connectivity check. Actually pings Postgres."""
    row = conn.execute("SELECT 1 AS ok").fetchone()
    return {"status": "ok", "db": row["ok"] == 1}
