from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_schema, pool
from app.routes import health, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: open the connection pool and ensure the schema exists.
    pool.open()
    init_schema()
    yield
    # Shutdown: close the pool cleanly.
    pool.close()


app = FastAPI(title="Borderless Interview API", lifespan=lifespan)

app.include_router(health.router)
app.include_router(users.router)
