from rest_framework import serializers

from goals.models import Goal


class GoalSerializer(serializers.ModelSerializer):
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = [
            "id", "title", "description", "category", "timeframe",
            "target_value", "current_value", "due_date", "is_achieved",
            "created_at", "progress_percent",
        ]
        read_only_fields = ["id", "created_at"]

    def get_progress_percent(self, obj):
        if not obj.target_value:
            return 0
        return round(min(obj.current_value / obj.target_value, 1) * 100, 1)
