# backend-template

Layer-first FastAPI backend template with a small, coherent example surface:

- `presentation/` — HTTP routers and request/response handling
- `application/` — use cases and application errors
- `domain/` — entities, value objects, repository contracts
- `infrastructure/` — SQLAlchemy, auth implementation, DI wiring
- `app/config.py` and `app/security.py` — neutral cross-cutting modules shared by multiple layers

## Included example slices

- `health` — public liveness endpoint
- `auth` — register, login, refresh, logout
- `user` — authenticated `GET /users/me`

The template intentionally keeps authentication as the main example of project style and removes domain-specific sample code.

## Run locally

```bash
uv sync
uv run uvicorn main:app --reload
```

Run database migrations before starting the API:

```bash
uv run alembic upgrade head
```


## Configuration

Create a `.env` file and set `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `AUTH_SECRET_KEY`, `AUTH_ALGORITHM`, `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES`, `AUTH_REFRESH_TOKEN_EXPIRE_DAYS`, and optionally `ENVIRONMENT`. The app still accepts the equivalent nested `POSTGRES__*` and `AUTH__*` variables when Docker Compose injects them.

## Migrations

- Alembic lives only in `alembic/`
- model metadata is loaded from `app.infrastructure.db.models`
- create a new migration with `uv run alembic revision --autogenerate -m "describe_change"`


## Structure

```txt
app/
  application/
    auth/
    common/
    interfaces/
    user/
  config.py
  domain/
    auth/
    common/
    user/
  infrastructure/
    db/
    di/
    auth.py
    container.py
  presentation/
    api/
      auth/
      health/
      user/
  security.py
```
