# Generated by Django 2.2.16 on 2022-12-01 10:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0009_auto_20221126_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_username', message='Некорректное имя', regex='\\w')], verbose_name='Никнейм'),
        ),
    ]