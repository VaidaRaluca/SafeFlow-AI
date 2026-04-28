# SafeFlow shared database

## Start

```bash
docker compose up
```

## Connect

- Host: `localhost`
- Port: `5432`
- Database: `safeflow_db`
- User: `postgres`
- Password: `postgres`

## Reset and reimport

```bash
docker compose down -v
docker compose up
```

## Enter WSL
```bash
devbox shell
```

## Run backend 
```bash
uv run uvicorn app.main:app --reload
```