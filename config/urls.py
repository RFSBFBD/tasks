from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/tasks/", include("tasks.urls")),
    path("api/goals/", include("goals.urls")),
    path("api/projects/", include("projects.urls")),
    path("api/schedule/", include("schedule_app.urls")),
    path("api/dashboard/", include("core.urls")),
]
