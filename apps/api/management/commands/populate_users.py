from django.core.management.base import BaseCommand
from apps.api.models import User


class Command(BaseCommand):
    help = 'Create sample users'

    def handle(self, *args, **kwargs):
        # 创建一组用户
        users = [
            {"username": "user1", "password": "password1"},
            {"username": "user2", "password": "password2"},
            {"username": "user3", "password": "password3"},
        ]

        for user_data in users:
            user = User(**user_data)
            user.save()  # 保存用户
            self.stdout.write(self.style.SUCCESS(f'Successfully created user: {user.username}'))
