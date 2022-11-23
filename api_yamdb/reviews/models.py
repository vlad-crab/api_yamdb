# reviews.models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE = (
    ('admin', 'admin'),
    ('moderator', 'moderator'),
    ('user', 'user'),
)


class User(AbstractUser):
    bio = models.TextField('Биография', blank=True,)
    role = models.TextField('Роль пользователя', max_length=16, choices=ROLE)
    confirmation_code = models.CharField('Код подтверждения',
                                         max_length=8,
                                         blank=True,)

    class Meta:
        unique_together = ('username', 'email')
