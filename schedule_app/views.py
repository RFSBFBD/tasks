from rest_framework import viewsets

from schedule_app.models import ScheduleEntry
from schedule_app.serializers import ScheduleEntrySerializer


class ScheduleEntryViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleEntrySerializer

    def get_queryset(self):
        return ScheduleEntry.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
