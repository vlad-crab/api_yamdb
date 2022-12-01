# reviews.models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


ROLE = (
    ('admin', 'admin'),
    ('moderator', 'moderator'),
    ('user', 'user'),
)

NAME_REGEX = RegexValidator(regex=r'^[\w.@+-]+$',
                            message='Некорректное имя',
                            code='invalid_username')


class User(AbstractUser):
    username = models.CharField('Никнейм', max_length=150, unique=True,
                                validators=[NAME_REGEX],)
    email = models.EmailField('Епочта', max_length=254, unique=True,)
    first_name = models.CharField('Имя пользователя',
                                  max_length=150, blank=True,)
    bio = models.TextField('Биография', blank=True,)
    role = models.CharField('Роль пользователя', max_length=16,
                            choices=ROLE, default='user')
    confirmation_code = models.CharField('Код подтверждения',
                                         max_length=8,
                                         blank=True,)

    class Meta:
        unique_together = ('username', 'email')  # можно убрать?
        # хотя в username разрешен символ @ и . Они могу дублироваться
