from rest_framework import serializers

from schedule_app.models import ScheduleEntry, ScheduleException


class ScheduleExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleException
        fields = ["id", "date", "is_cancelled", "new_start_time", "new_end_time"]
        read_only_fields = ["id"]


class ScheduleEntrySerializer(serializers.ModelSerializer):
    exceptions = ScheduleExceptionSerializer(many=True, read_only=True)

    class Meta:
        model = ScheduleEntry
        fields = [
            "id", "title", "category", "weekday", "start_time",
            "end_time", "is_recurring", "exceptions",
        ]
        read_only_fields = ["id"]
