from django.core.management.base import BaseCommand
from apps.api.models import Book
from datetime import date


class Command(BaseCommand):
    help = 'Populate the database with initial Book data'

    def handle(self, *args, **kwargs):
        # gpt 生成的
        books = [
            Book(title='Django for Beginners', author='William S. Vincent', published_date=date(2018, 8, 1),
                 isbn='1234567890123', pages=200, language='English'),
            Book(title='Django for APIs', author='William S. Vincent', published_date=date(2019, 3, 15),
                 isbn='1234567890124', pages=180, language='English'),
            Book(title='Python Crash Course', author='Eric Matthes', published_date=date(2019, 5, 3),
                 isbn='1234567890125', pages=560, language='English'),
            Book(title='Automate the Boring Stuff with Python', author='Al Sweigart', published_date=date(2019, 11, 17),
                 isbn='1234567890126', pages=500, language='English'),
            Book(title='Learning Python', author='Mark Lutz', published_date=date(2013, 6, 1), isbn='1234567890127',
                 pages=1600, language='English'),
        ]

        Book.objects.bulk_create(books)

        self.stdout.write(self.style.SUCCESS('Successfully populated the Book table.'))
