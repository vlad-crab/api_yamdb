import string
import random
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework import mixins, viewsets
from rest_framework import permissions
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User
from api.serializers import UserSerializer, GetTokenUserSerializer


def code_generate(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class GetTokenUserApi(mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = GetTokenUserSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = GetTokenUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = get_object_or_404(User, username=data['username'])
        if user.confirmation_code == data['confirmation_code']:
            refresh = RefreshToken.for_user(user)
        else:
            raise serializers.ValidationError(
                {'detail': 'Incorrect username or code'})
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            },
            status=status.HTTP_200_OK
        )


class CreateUserViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        code = code_generate()
        username = self.request.data['username']
        email = self.request.data['email']
        if username != 'me':
            user = User.objects.create(
                username=username,
                email=email,
                confirmation_code=code,
                role='user',
            )
            send_mail(
                f'confirmation_code пользователя {username}',
                f'Вот вам код: "{code}", чтобы вы могли зайти на YaMDB',
                'YaMDB@ya.com',
                [email, ],
                fail_silently=False,
            )
            return user
        raise serializers.ValidationError('Нельзя использовать имя "me"')
