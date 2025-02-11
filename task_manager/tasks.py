from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


@shared_task
def send_registration_email(email, token):
    subject = "Registration confirmation"
    message = f"Confirm your registration: http://example.com/verify/{token}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


@shared_task
def send_course_start_notification(email, course_name, start_date):
    subject = f"Your course {course_name} start soon!"
    message = f"Course {course_name} starts {start_date}."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


@shared_task
def send_new_task_notification(email, task_description, course_name):
    subject = f"New task in {course_name}"
    message = f"You have task: {task_description}. Dont forget to add!"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


@shared_task
def send_task_review_notification(email, task_description, mark):
    subject = "Task review"
    message = f'Your task "{task_description}" was reviewed. your mark: {mark}.'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


@shared_task
def send_password_reset_email(email, token):
    reset_link = f"{settings.SITE_URL}{reverse('password_reset_confirm', args=[token])}"

    send_mail(
        subject="Reset password",
        message=f"Follow this link to reset your password: {reset_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
