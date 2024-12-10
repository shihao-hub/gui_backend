from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    published_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)  # 13 位 ISBN
    pages = models.PositiveIntegerField()
    language = models.CharField(max_length=30)

    def __str__(self):
        return self.title

# -------------------------------------------------------------------------------------------------------------------- #
# mongodb
# -------------------------------------------------------------------------------------------------------------------- #


# -------------------------------------------------------------------------------------------------------------------- #
# redis
# -------------------------------------------------------------------------------------------------------------------- #
