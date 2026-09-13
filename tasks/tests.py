from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Project, Task

User = get_user_model()


class TaskFlowAPITests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="test-pass-123")
        self.member = User.objects.create_user(username="member", password="test-pass-123")
        self.outsider = User.objects.create_user(username="outsider", password="test-pass-123")

        self.project = Project.objects.create(name="Launch API", owner=self.owner)
        self.project.members.add(self.owner, self.member)
        self.task = Task.objects.create(
            project=self.project,
            title="Ship backend",
            assignee=self.member,
            priority=Task.Priority.HIGH,
        )

    def test_project_member_can_list_tasks(self):
        self.client.force_authenticate(self.member)
        response = self.client.get(reverse("task-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_outsider_cannot_see_project_tasks(self):
        self.client.force_authenticate(self.outsider)
        response = self.client.get(reverse("task-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_member_can_complete_task(self):
        self.client.force_authenticate(self.member)
        response = self.client.post(reverse("task-complete", args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.DONE)
        self.assertIsNotNone(self.task.completed_at)

    def test_project_owner_is_set_from_authenticated_user(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            reverse("project-list"),
            {"name": "New Project", "description": "API work"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        created = Project.objects.get(id=response.data["id"])
        self.assertEqual(created.owner, self.owner)
