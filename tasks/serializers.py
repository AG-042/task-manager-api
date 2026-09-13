from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Project, Task

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSummarySerializer(read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "members",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]


class TaskSerializer(serializers.ModelSerializer):
    assignee_detail = UserSummarySerializer(source="assignee", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "title",
            "description",
            "assignee",
            "assignee_detail",
            "status",
            "priority",
            "due_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "completed_at", "created_at", "updated_at"]

    def validate(self, attrs):
        project = attrs.get("project") or getattr(self.instance, "project", None)
        assignee = attrs.get("assignee")
        if project and assignee:
            allowed_ids = set(project.members.values_list("id", flat=True)) | {project.owner_id}
            if assignee.id not in allowed_ids:
                raise serializers.ValidationError(
                    {"assignee": "Assignee must be the project owner or a project member."}
                )
        return attrs
