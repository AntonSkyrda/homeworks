from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView

from .models import Course


class IndexView(TemplateView):
    template_name = "courses/index.html"


class CourseListView(ListView):
    model = Course
    context_object_name = "courses"

    def get_queryset(self):
        return Course.objects.prefetch_related(
            "student",
            "lessons",
            "task_set",
        ).select_related(
            "teacher",
        )


class CourseDetailView(DetailView):
    model = Course


class CourseStudentsListView(ListView):
    template_name = "courses/students_list.html"
    context_object_name = "students"

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs["course_id"])
        students = course.get_students_with_marks()

        sort_order = self.request.GET.get("sort", "desc")
        if sort_order == "asc":
            students = students.order_by("total_marks")

        return students

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = get_object_or_404(Course, id=self.kwargs["course_id"])
        return context
