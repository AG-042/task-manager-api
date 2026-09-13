from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Project, Task
from .permissions import IsProjectOwnerOrReadOnly
from .serializers import ProjectSerializer, TaskSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        project.members.add(self.request.user)

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        project = self.get_object()
        key = f"project:{project.pk}:summary"
        data = cache.get(key)
        if data is None:
            tasks = project.tasks.all()
            data = {
                "total": tasks.count(),
                "todo": tasks.filter(status=Task.Status.TODO).count(),
                "in_progress": tasks.filter(status=Task.Status.IN_PROGRESS).count(),
                "done": tasks.filter(status=Task.Status.DONE).count(),
            }
            cache.set(key, data, timeout=60)
        return Response(data)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsProjectOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(
            Q(project__owner=user) | Q(project__members=user)
        ).select_related("project", "assignee").distinct()
        if project_id := self.request.query_params.get("project"):
            queryset = queryset.filter(project_id=project_id)
        if status_value := self.request.query_params.get("status"):
            queryset = queryset.filter(status=status_value)
        if priority := self.request.query_params.get("priority"):
            queryset = queryset.filter(priority=priority)
        return queryset

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        user = self.request.user
        if project.owner_id != user.id and not project.members.filter(id=user.id).exists():
            raise PermissionDenied("You are not a member of this project.")
        task = serializer.save()
        cache.delete(f"project:{task.project_id}:summary")

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = Task.Status.DONE
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at", "updated_at"])
        cache.delete(f"project:{task.project_id}:summary")
        return Response(self.get_serializer(task).data)
