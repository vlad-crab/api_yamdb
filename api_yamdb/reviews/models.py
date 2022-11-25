from django.db import models
from django.contrib.auth.models import AbstractUser


SCORE_CHOICES = [(i, i) for i in range(1, 11)]
ROLE = (
    ('admin', 'admin'),
    ('moderator', 'moderator'),
    ('user', 'user'),
)


class User(AbstractUser):
    bio = models.TextField('Биография', blank=True,)
    role = models.TextField('Роль пользователя', max_length=16, choices=ROLE)
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=8,
        blank=True,
    )

    class Meta:
        unique_together = ('username', 'email')


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
        verbose_name="Год выпуска"
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


class Review(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(choices=SCORE_CHOICES)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'

    def __str__(self):
        return self.text
