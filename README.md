# My Task — Backend

Django + PostgreSQL backend for the My Task personal productivity app,
with Clerk handling authentication and an MCP server exposing the data to
any AI assistant.

## Stack
- **API**: Django + Django REST Framework
- **DB**: PostgreSQL
- **Auth**: Clerk (JWT verified against Clerk's JWKS — see `core/authentication.py`)
- **AI access**: MCP server in `mcp_server/` (separate process/container)
- **Containers**: Docker + docker-compose

## What's already wired up
- `config/settings.py` — reads everything from `.env` (DB, Clerk keys, CORS, allowed hosts)
- `core/authentication.py` — verifies Clerk JWTs, maps them to Django users
- `core/models.py` — `UserProfile` (Clerk↔Django mapping) + `Category`
- `tasks/`, `goals/`, `projects/`, `schedule_app/` — full CRUD models + DRF endpoints, scoped per-user
- `core/views.py` — `/api/dashboard/progress/` endpoint feeding the dashboard progress chart
- `mcp_server/server.py` — MCP tools: `list_tasks`, `add_task`, `update_task_status`, `list_goals`, `get_weekly_schedule`, `get_progress_summary`
- `docker-compose.yml` — `db` + `backend` + `mcp` services

## What's NOT done yet (on purpose — see PROMPTS.md)
- The Next.js frontend isn't in this repo — it's wired via prompts for your coding agent
- No automated tests yet
- MCP server currently assumes a single user (no per-request auth) — fine for local/private use, not for exposing publicly
- No production Dockerfile hardening (non-root user, multi-stage build, etc.)

## Local setup
```bash
cp .env.example .env         # then fill in real values, especially CLERK_* and POSTGRES_PASSWORD
docker compose up --build
docker compose exec backend python manage.py createsuperuser   # optional, for /admin/
```
Backend API: http://localhost:8000/api/
Django admin: http://localhost:8000/admin/
MCP server: listens per `mcp_server/server.py` (stdio by default — see PROMPTS.md stage 4 to run it over HTTP/SSE instead if you want a remote AI to reach it)

## Next steps
Open `PROMPTS.md` — it has ready-to-paste prompts for your coding agent to
finish the frontend integration, complete the backend, wire Docker testing,
and finalize the MCP connection.
