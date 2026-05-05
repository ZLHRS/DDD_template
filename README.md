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

## Configuration

Default values live in `config.yaml`. `app/config.py` now loads overrides from environment variables and `.env` via `pydantic-settings`; nested keys use `__`, for example `POSTGRES__HOST`, `POSTGRES__PASSWORD`, and `AUTH__SECRET_KEY`.

`config.docker.yaml` remains available if you explicitly point `CONFIG_PATH` at it, but Docker Compose now passes the application config through environment variables instead.

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
