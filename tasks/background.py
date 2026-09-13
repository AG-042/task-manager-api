from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from .models import Task


@shared_task

def send_due_task_reminders():
    now = timezone.now()
    deadline = now + timedelta(hours=24)

    due_tasks = (
        Task.objects.filter(
            due_at__gte=now,
            due_at__lte=deadline,
            status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS],
            assignee__isnull=False,
        )
        .select_related("assignee", "project")
    )

    sent = 0
    for task in due_tasks:
        if not task.assignee.email:
            continue

        send_mail(
            subject=f"Task due soon: {task.title}",
            message=(
                f"Your task '{task.title}' in project '{task.project.name}' "
                f"is due at {task.due_at:%Y-%m-%d %H:%M %Z}."
            ),
            from_email=None,
            recipient_list=[task.assignee.email],
            fail_silently=True,
        )
        sent += 1

    return {"reminders_sent": sent}
