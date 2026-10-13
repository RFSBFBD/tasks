"""
My Task — MCP server.

Lets ANY MCP-compatible AI assistant (Claude Desktop, Claude Code, ChatGPT
with MCP support, etc.) read and update your tasks, goals, and schedule.

This talks to the SAME PostgreSQL database as the Django backend, directly
via psycopg2 — it does not go through Django's ORM, so it stays lightweight
and has zero dependency on the web app being deployed.

SECURITY NOTE: this first version is scoped to a SINGLE user (yours) and
has no multi-tenant auth — it's meant to run locally/privately, next to a
database that only has your data in it. Don't expose this server's port to
the public internet without adding real authentication in front of it.

Run it with:
    python mcp_server/server.py
or wire it into Claude Desktop / Claude Code's MCP config (see PROMPTS.md
stage 4 for the exact config block).
"""
import os
from contextlib import contextmanager
from datetime import date, datetime

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

DATABASE_URL = os.environ.get("MCP_DATABASE_URL") or os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Set MCP_DATABASE_URL (or DATABASE_URL) before starting the MCP server.")

mcp = FastMCP("my-task")


@contextmanager
def get_cursor():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        conn.autocommit = False
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _json_safe(row: dict) -> dict:
    out = {}
    for k, v in row.items():
        if isinstance(v, (date, datetime)):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


@mcp.tool()
def list_tasks(status: str | None = None, due_before: str | None = None) -> list[dict]:
    """List tasks, optionally filtered by status (todo/in_progress/done)
    and/or a due_before date (YYYY-MM-DD)."""
    query = "SELECT id, title, status, priority, due_date FROM tasks_task WHERE 1=1"
    params: list = []
    if status:
        query += " AND status = %s"
        params.append(status)
    if due_before:
        query += " AND due_date <= %s"
        params.append(due_before)
    query += " ORDER BY due_date NULLS LAST, priority DESC"

    with get_cursor() as cur:
        cur.execute(query, params)
        return [_json_safe(dict(r)) for r in cur.fetchall()]


@mcp.tool()
def add_task(
    title: str,
    owner_id: int,
    description: str = "",
    due_date: str | None = None,
    priority: str = "medium",
    category_id: int | None = None,
    project_id: int | None = None,
) -> dict:
    """Create a new task. priority is one of low/medium/high."""
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO tasks_task
                (title, description, status, priority, due_date,
                 category_id, project_id, owner_id, created_at, updated_at)
            VALUES (%s, %s, 'todo', %s, %s, %s, %s, %s, now(), now())
            RETURNING id, title, status, priority, due_date
            """,
            (title, description, priority, due_date, category_id, project_id, owner_id),
        )
        return _json_safe(dict(cur.fetchone()))


@mcp.tool()
def update_task_status(task_id: int, status: str) -> dict:
    """Update a task's status. status is one of todo/in_progress/done."""
    completed_at_sql = "now()" if status == "done" else "NULL"
    with get_cursor() as cur:
        cur.execute(
            f"""
            UPDATE tasks_task
            SET status = %s, completed_at = {completed_at_sql}, updated_at = now()
            WHERE id = %s
            RETURNING id, title, status, completed_at
            """,
            (status, task_id),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"No task with id {task_id}")
        return _json_safe(dict(row))


@mcp.tool()
def list_goals(timeframe: str | None = None) -> list[dict]:
    """List goals, optionally filtered by timeframe (weekly/monthly/quarterly/yearly)."""
    query = "SELECT id, title, timeframe, target_value, current_value, is_achieved FROM goals_goal WHERE 1=1"
    params: list = []
    if timeframe:
        query += " AND timeframe = %s"
        params.append(timeframe)

    with get_cursor() as cur:
        cur.execute(query, params)
        return [_json_safe(dict(r)) for r in cur.fetchall()]


@mcp.tool()
def get_weekly_schedule() -> list[dict]:
    """Return the full recurring weekly schedule (all entries, all days)."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, title, weekday, start_time, end_time, is_recurring
            FROM schedule_app_scheduleentry
            ORDER BY weekday, start_time
            """
        )
        return [_json_safe(dict(r)) for r in cur.fetchall()]


@mcp.tool()
def get_progress_summary(days: int = 14) -> dict:
    """Same aggregation as the dashboard chart: completion rate per day
    over the last N days, plus an overall rate."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT due_date,
                   count(*) AS total,
                   count(*) FILTER (WHERE status = 'done') AS completed
            FROM tasks_task
            WHERE due_date >= (CURRENT_DATE - (%s || ' days')::interval)
            GROUP BY due_date
            ORDER BY due_date
            """,
            (days,),
        )
        rows = [_json_safe(dict(r)) for r in cur.fetchall()]

    total = sum(r["total"] for r in rows)
    completed = sum(r["completed"] for r in rows)
    return {
        "range_days": days,
        "overall_completion_rate": round(completed / total * 100, 1) if total else 0,
        "series": rows,
    }


if __name__ == "__main__":
    mcp.run()
