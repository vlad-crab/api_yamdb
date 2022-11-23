from rest_framework import serializers

from reviews.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'bio', 'first_name', 'last_name',
        )
        read_only_fields = ('role', 'bio', 'first_name', 'last_name',)


class GetTokenUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
