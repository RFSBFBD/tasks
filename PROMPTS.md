# My Task — Prompts للـ Agent (Claude Code أو أي agent تاني)

استخدم البرومتات دي بالترتيب. كل مرحلة مبنية على اللي قبلها، فمتخبطش الترتيب.
انسخ البرومت كامل، حط مكان الأقواس [] التفاصيل بتاعتك، وابعته للـ agent في مجلد المشروع.

---

## Stage 1 — ربط الـ Frontend (Next.js) بـ Clerk + الـ Backend الجديد

```
I have an existing Next.js + React frontend for a personal task management
app called "My Task", currently wired to Supabase for both auth and data.
I'm migrating it to use Clerk for authentication and a separate Django
REST API (running at http://localhost:8000/api/ locally) for all data.

The Django backend is already built and expects:
- Authorization: Bearer <clerk_session_token> on every API request
- Endpoints: /api/tasks/, /api/goals/, /api/projects/, /api/schedule/,
  /api/dashboard/progress/?days=14
- Standard DRF pagination ({ "count", "next", "previous", "results": [...] })

Please:
1. Install and configure @clerk/nextjs. Wrap the app in <ClerkProvider>,
   add middleware.ts to protect all routes except /sign-in and /sign-up.
2. Replace every Supabase auth call (supabase.auth.*) with Clerk's
   equivalents (useUser, useAuth, SignIn/SignUp components).
3. Remove all direct Supabase data queries (supabase.from(...)). Replace
   them with a small typed API client (lib/api.ts) that:
   - reads NEXT_PUBLIC_API_URL from env
   - attaches the Clerk session token via useAuth().getToken() to every
     request's Authorization header
   - exposes functions like getTasks(), createTask(), updateTaskStatus(),
     getGoals(), getProjects(), getWeeklySchedule(), getDashboardProgress()
4. Update every page/component that currently reads from Supabase to use
   this new API client instead, keeping the existing UI/UX untouched.
5. Remove the Supabase client package and its env vars once nothing
   references them anymore.
6. Add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY, and
   NEXT_PUBLIC_API_URL to frontend/.env.local (use placeholder values,
   I'll fill in the real keys myself).

Don't change the color palette, layout, or add any animations — the
existing design (sidebar navigation, no-animation, light practical UI)
should stay exactly as is. Ask me before deleting any file you're not
sure about.
```

---

## Stage 2 — استكمال الـ Backend (Django)

```
This Django REST backend for "My Task" currently has working CRUD for
tasks, goals, projects, and schedule entries, all scoped per-user via
Clerk authentication (see core/authentication.py). I need you to finish
the remaining pieces:

1. Add filtering + search to goals, projects, and schedule endpoints
   (same pattern as tasks/views.py using DjangoFilterBackend).
2. Add a /api/projects/{id}/milestones/ nested endpoint for creating
   and toggling ProjectMilestone rows.
3. Add a /api/schedule/{id}/exceptions/ endpoint for creating one-off
   ScheduleException overrides on a recurring entry.
4. Add an /api/dashboard/upcoming/ endpoint returning: today's tasks,
   this week's schedule entries (expanded with any exceptions applied),
   and goals due in the next 7 days — in one response, for the dashboard
   landing view.
5. Write Django management command `seed_demo_data` that creates
   categories (University, Gym, Quran, Freelance, AI Educational
   Assistant) and a couple of example tasks/goals for the currently
   logged-in UserProfile, so the dashboard isn't empty on first login.
6. Add drf-spectacular (or similar) for auto-generated OpenAPI docs at
   /api/schema/swagger-ui/.

Keep the existing ownership pattern (filter every queryset by
request.user, set owner on create) — don't introduce any endpoint that
can read or write another user's rows.
```

---

## Stage 3 — Docker الكامل + اختبار شامل

```
I have a docker-compose.yml with db, backend, and mcp services already
defined for this Django + PostgreSQL + MCP project. I now also have a
Next.js frontend repo that talks to this backend via Clerk-authenticated
REST calls. Please:

1. Write a production-sensible Dockerfile for the Next.js frontend
   (multi-stage: deps -> build -> run, non-root user, standalone output).
2. Add a `frontend` service to docker-compose.yml, on the same Docker
   network as `backend`, exposing port 3000, reading its env from
   frontend/.env.local.
3. Add a healthcheck to the `backend` service (curl against a simple
   /api/health/ endpoint — create that endpoint if it doesn't exist).
4. Write pytest tests for the Django backend covering: Clerk JWT
   verification failure cases (missing token, expired token, bad
   signature — mock the JWKS fetch), and that a user can never read or
   modify another user's tasks/goals/projects/schedule entries.
5. Add a GitHub Actions (or simple shell script, whichever fits my setup)
   workflow that runs `docker compose build` and the pytest suite on
   every push.
6. Verify end-to-end locally: `docker compose up --build`, run migrations,
   create a demo user via the seed command from Stage 2, confirm the
   frontend can sign in through Clerk and load real data from the API
   (not mocked data).

Report back exactly what you tested and what still needs my manual
verification (e.g. anything requiring real Clerk keys).
```

---

## Stage 4 — تفعيل الـ MCP عشان أي AI يربط بالموقع

```
mcp_server/server.py already defines MCP tools (list_tasks, add_task,
update_task_status, list_goals, get_weekly_schedule, get_progress_summary)
that talk directly to the same PostgreSQL database as the Django backend.
Currently it runs over stdio and assumes a single user with no per-request
auth. Please:

1. Add two more tools: delete_task(task_id) and get_today_overview()
   (today's tasks + today's schedule entries + any goals due today, in
   one call — this is the main thing I'll ask an AI assistant for).
2. Switch the server to run over Streamable HTTP (FastMCP supports this)
   instead of stdio, on the MCP_SERVER_PORT from .env, so it can run as
   its own container (mcp_server/Dockerfile already exists) and be
   reached by name from other machines on my network, not just locally.
3. Add a simple shared-secret header check (MCP_ACCESS_TOKEN env var) so
   the HTTP endpoint isn't wide open — reject any request missing or
   mismatching that header before it touches the database.
4. Write the exact JSON config block I need to add to Claude Desktop's
   (or Claude Code's) MCP settings to connect to this server, assuming
   it's running at http://localhost:8001.
5. Document in mcp_server/README.md: which tools exist, what each
   returns, and the one security caveat (single-user, shared-secret only,
   not meant to be exposed to the public internet without a real
   per-user auth layer).

Don't touch the Django backend or the frontend in this stage — this is
MCP-server-only.
```

---

## ملاحظات عامة لأي مرحلة
- كل .env بيتملى منك إنت شخصيًا (Clerk keys, DB password) — محدش يحطهم في الكود أو يرفعهم Git.
- لو الـ agent عايز يحذف أو يغيّر حاجة في ملفات مش واضحة له، خليه يسألك الأول (مكتوب في البرومتات أعلاه).
- بعد كل مرحلة، شغّل `docker compose up --build` وتأكد إن حاجة واحدة بس اتغيرت زي المتوقع قبل ما تكمل للمرحلة اللي بعدها.
