from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Sum, OuterRef, Subquery
from django.utils.translation import gettext_lazy as _

from task_manager.tasks import send_course_start_notification

from tasks.models import TaskMark

User = get_user_model()


class Course(models.Model):
    name = models.CharField(_("Course Name"), max_length=255, unique=True)
    description = models.TextField(_("Course Description"))
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    student = models.ManyToManyField(User, related_name="students", blank=True)
    tags = ArrayField(models.CharField(max_length=100), default=list, blank=True)
    start_date = models.DateField(_("Start Date"), null=True, blank=True)

    def __str__(self):
        return self.name

    def get_students_with_marks(self):
        student_marks = (
            TaskMark.objects.filter(
                task_answer__student=OuterRef("pk"), task_answer__task__course=self
            )
            .values("task_answer__student")
            .annotate(total_marks=Sum("mark"))
            .values("total_marks")
        )

        students = (
            self.student.all()
            .annotate(total_marks=Subquery(student_marks))
            .order_by("-total_marks")
        )

        return students

    def save(self, *args, **kwargs):
        if self.start_date:
            for student in self.student.all():
                send_course_start_notification.delay(
                    student.email, self.name, str(self.start_date)
                )

        super().save(*args, **kwargs)
