from django.urls import path

from .views import CourseListView, CourseDetailView, IndexView, CourseStudentsListView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("courses/", CourseListView.as_view(), name="course_list"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course_detail"),
    path(
        "courses/<int:course_id>/students/",
        CourseStudentsListView.as_view(),
        name="course_students_list",
    ),
]

app_name = "courses"
