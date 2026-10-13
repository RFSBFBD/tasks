from rest_framework import serializers

from projects.models import Project, ProjectMilestone


class ProjectMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMilestone
        fields = ["id", "title", "is_done", "due_date", "order"]
        read_only_fields = ["id"]


class ProjectSerializer(serializers.ModelSerializer):
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "name", "description", "status", "target_date",
            "created_at", "milestones", "progress_percent",
        ]
        read_only_fields = ["id", "created_at"]

    def get_progress_percent(self, obj):
        total = obj.milestones.count()
        if not total:
            return 0
        done = obj.milestones.filter(is_done=True).count()
        return round(done / total * 100, 1)
