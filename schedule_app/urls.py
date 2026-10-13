from rest_framework.routers import DefaultRouter

from schedule_app.views import ScheduleEntryViewSet

router = DefaultRouter()
router.register("", ScheduleEntryViewSet, basename="schedule-entry")

urlpatterns = router.urls
