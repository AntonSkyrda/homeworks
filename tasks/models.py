from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from courses.models import Course
from task_manager.tasks import send_new_task_notification, send_task_review_notification

User = get_user_model()


class Task(models.Model):
    description = models.TextField(_("Task description"))
    max_marks = models.PositiveIntegerField(_("Maximum mark"))
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        for student in self.course.student.all():
            send_new_task_notification.delay(
                student.email, self.description, self.course.name
            )


class TaskAnswer(models.Model):
    description = models.TextField(_("Answer description"))
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    mark = models.PositiveIntegerField(_("Task mark"), blank=True, null=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.mark is not None:
            send_task_review_notification.delay(
                self.student.email, self.task.description, self.mark
            )


class TaskMark(models.Model):
    date = models.DateField(_("Task date"))
    mark = models.PositiveIntegerField(_("Task mark"))
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    task_answer = models.ForeignKey("TaskAnswer", on_delete=models.CASCADE)
