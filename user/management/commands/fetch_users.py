import requests
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

from task_manager.tasks import send_password_reset_email

User = get_user_model()


class Command(BaseCommand):
    help = "Get users list from API https://reqres.in/ and create new student accounts"

    def handle(self, *args, **kwargs):
        url = "https://reqres.in/api/users"
        response = requests.get(url)

        if response.status_code != 200:
            self.stderr.write(self.style.ERROR("Error from API"))
            return

        users_data = response.json().get("data", [])

        for user_data in users_data:
            email = user_data["email"]
            first_name = user_data["first_name"]
            last_name = user_data["last_name"]

            password = get_random_string(12)

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_active": True,
                },
            )

            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Account created to {email}"))

                send_password_reset_email.delay(email, get_random_string(32))
            else:
                self.stdout.write(self.style.WARNING(f"User {email} is already exists"))
