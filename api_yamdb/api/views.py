import string
import random
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import mixins, viewsets, permissions, status, serializers
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User
from .permissions import YaMDB_Admin
from api.serializers import (
    GetTokenUserSerializer,
    RetrieveUpdateUserSerializer
)


def code_generate(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
    }


class GetTokenViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
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
                'access': str(refresh.access_token)
            },
            status=status.HTTP_200_OK
        )


class CreateUserView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data['username']
        email = request.data['email']
        print(username, email)
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.email = email  # Ее сказало что делать если почта новая?
            user.save()  # а юзер старый, перезаписываю почту.
            print(str(user), type(user), user.email, user.confirmation_code)
            send_mail(
                f'confirmation_code пользователя {username}',
                f'Вот вам код: "{user.confirmation_code}", для YaMDB',
                'YaMDB@ya.com',
                [user.email, ],
                fail_silently=False,
            )
            return Response(
                {
                    'username': str(username),
                    'confirmation_code': str(user.confirmation_code),
                },
                status=status.HTTP_200_OK)

        if request.data['username'] == 'me':
            raise serializers.ValidationError('Нельзя использовать имя "me"')
        code = code_generate()
        serializer = RetrieveUpdateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(confirmation_code=code, role='user',)
            send_mail(
                f'confirmation_code пользователя {username}',
                f'Вот вам код: "{code}", чтобы вы могли зайти на YaMDB',
                'YaMDB@ya.com',
                [email, ],
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveUpdateUserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = RetrieveUpdateUserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = User.objects.get(id=request.user.id)
        if 'role' in request.data:
            request.data.pop('role')
        serializer = RetrieveUpdateUserSerializer(
            user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RetrieveUpdateUserSerializer
    permission_classes = (permissions.IsAuthenticated, YaMDB_Admin,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username',)
    lookup_field = 'username'
