from django.urls import path

from core.views import DashboardProgressView

urlpatterns = [
    path("progress/", DashboardProgressView.as_view(), name="dashboard-progress"),
]
