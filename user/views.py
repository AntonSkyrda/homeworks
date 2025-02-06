from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, DetailView

from courses.models import Course
from tasks.models import Task, TaskAnswer
from tasks.forms import TaskAnswerForm
from .forms import UserCreateForm
from task_manager.tasks import send_registration_email


class UserLoginView(LoginView):
    template_name = "auth/login.html"

    def form_invalid(self, form):
        messages.error(self.request, "Incorrect username or password")
        return self.render_to_response(self.get_context_data(form=form))


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("user:login")


class RegisterView(FormView):
    template_name = "auth/register.html"
    form_class = UserCreateForm
    success_url = reverse_lazy("user:login")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)

        send_registration_email.delay(user.email, "some-generated-token")

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        email = EmailMultiAlternatives(
            subject="Registration",
            body="Thank you for registering",
            to=[self.request.user.email],
        )

        email.send()


class UserDashboardView(LoginRequiredMixin, ListView):
    model = Course
    template_name = "user/dashboard.html"
    context_object_name = "courses"

    def get_queryset(self):
        return Course.objects.filter(student=self.request.user)


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = "user/course_detail.html"
    context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        tasks = Task.objects.filter(course=course)
        tasks_answers = TaskAnswer.objects.filter(
            student=self.request.user, task__in=tasks
        )

        task_grades = {
            task.id: (
                tasks_answers.filter(task=task).first().mark
                if tasks_answers.filter(task=task).exists()
                else None
            )
            for task in tasks
        }
        context["tasks"] = tasks
        context["task_grades"] = task_grades
        return context

    def get_object(self):
        course_id = self.kwargs.get("course_id")
        return get_object_or_404(Course, id=course_id)


class TaskAnswerFormView(LoginRequiredMixin, FormView):
    template_name = "user/submit_task_answer.html"
    form_class = TaskAnswerForm

    def form_valid(self, form):
        task = form.cleaned_data["task"]
        description = form.cleaned_data["description"]
        TaskAnswer.objects.create(
            student=self.request.user,
            task=task,
            description=description,
            mark=None,
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "user:course_detail", kwargs={"course_id": self.kwargs["course_id"]}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = get_object_or_404(Task, id=self.kwargs["task_id"])
        return context
