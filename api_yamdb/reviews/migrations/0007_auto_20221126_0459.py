# Generated by Django 2.2.16 on 2022-11-26 04:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0006_auto_20221124_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'admin'), ('moderator', 'moderator'), ('user', 'user')], default='user', max_length=16, verbose_name='Роль пользователя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_username', message='Некорректное имя', regex='^[\\w.@+-]+\\z')]),
        ),
    ]