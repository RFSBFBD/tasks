from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from tasks.models import Task
from tasks.serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "priority", "category", "project", "due_date"]

    def get_queryset(self):
        # Row-level ownership: a user only ever sees their own tasks —
        # this is the backend-side equivalent of Supabase RLS.
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
