from rest_framework import serializers
from django.core.validators import RegexValidator

from reviews.models import User


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[RegexValidator(regex=r'^[\w.@+-]+',
                                   message='Некорректное имя',
                                   code='invalid_username'), ])
    email = serializers.EmailField()
    confirmation_code = serializers.CharField(max_length=8)


class GetTokenUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class RetrieveUpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role',)
        read_only = ('role')
