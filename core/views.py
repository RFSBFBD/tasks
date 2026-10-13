"""
Feeds the dashboard progress chart. Kept intentionally simple — this is the
shape your Next.js chart component should expect; expand the aggregation
logic once the real models are filled with data.
"""
from datetime import timedelta

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.models import Task


class DashboardProgressView(APIView):
    """GET /api/dashboard/progress/?days=14

    Returns, per day, how many tasks were completed vs. total due —
    exactly what a line/bar chart needs.
    """

    def get(self, request):
        days = int(request.query_params.get("days", 14))
        today = timezone.localdate()
        start = today - timedelta(days=days - 1)

        qs = Task.objects.filter(owner=request.user, due_date__gte=start, due_date__lte=today)

        by_day = {start + timedelta(days=i): {"total": 0, "completed": 0} for i in range(days)}
        for task in qs:
            bucket = by_day.get(task.due_date)
            if bucket is None:
                continue
            bucket["total"] += 1
            if task.status == Task.Status.DONE:
                bucket["completed"] += 1

        series = [
            {
                "date": day.isoformat(),
                "total": stats["total"],
                "completed": stats["completed"],
                "completion_rate": (
                    round(stats["completed"] / stats["total"] * 100, 1)
                    if stats["total"]
                    else 0
                ),
            }
            for day, stats in sorted(by_day.items())
        ]

        overall_total = sum(s["total"] for s in series)
        overall_completed = sum(s["completed"] for s in series)

        return Response(
            {
                "range_days": days,
                "overall_completion_rate": (
                    round(overall_completed / overall_total * 100, 1) if overall_total else 0
                ),
                "series": series,
            }
        )
