from rest_framework.permissions import BasePermission


class IsProjectOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        project = getattr(obj, "project", obj)
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return project.owner_id == request.user.id or project.members.filter(id=request.user.id).exists()
        return project.owner_id == request.user.id
