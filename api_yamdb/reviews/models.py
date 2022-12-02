from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def validate_year(value):
    now = timezone.now().year
    if value > now:
        raise ValidationError(
            f'{value} не может быть больше {now}'
        )


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name="Жанр")
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="Категория"
    )
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200, verbose_name='Произведение')
    year = models.IntegerField(
        null=True,
        verbose_name="Год выпуска",
        validators=(validate_year, )
    )
    description = models.CharField(max_length=200, null=True)
    genre = models.ManyToManyField(Genre, blank=True, related_name="titles")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="titles"
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
