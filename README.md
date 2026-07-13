# Borderless Interview

FastAPI + PostgreSQL backend, organised as **route -> service -> repository**.

## Prerequisites

- Docker Desktop (running)
- Python 3.12+

## Setup

Start the database:

```bash
docker compose up -d
```

Create the Python environment and install dependencies:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Test

```bash
pip install -r requirements-dev.txt   # first time only
pytest -v
```

(The Postgres container must be running for the repository tests.)

## Stop

```bash
docker compose down       # stop the database (keeps data)
docker compose down -v    # stop and wipe the data volume
```
