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

Edit `config.yaml` for local development or `config.docker.yaml` for Docker.

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
