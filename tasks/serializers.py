from django.utils import timezone
from rest_framework import serializers

from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status", "priority",
            "category", "project", "due_date", "completed_at",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "completed_at", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        if validated_data.get("status") == Task.Status.DONE and instance.status != Task.Status.DONE:
            validated_data["completed_at"] = timezone.now()
        elif validated_data.get("status") and validated_data["status"] != Task.Status.DONE:
            validated_data["completed_at"] = None
        return super().update(instance, validated_data)
