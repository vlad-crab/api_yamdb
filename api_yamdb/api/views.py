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
    CreateUserSerializer,
    GetTokenSerializer,
    RetrieveUpdateUserSerializer
)


def code_generate(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class GetTokenViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = GetTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = GetTokenSerializer(data=request.data)
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
        if request.data.get('username', False) == 'me':
            raise serializers.ValidationError('Нельзя использовать имя "me"')
        username = request.data.get('username')
        email = request.data.get('email')
        if not User.objects.filter(username=username).exists():
            code = code_generate()
            serializer = CreateUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(confirmation_code=code, role='user',)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        else:  # условие если пользователь сущетсвует
            user = User.objects.get(username=username)
            if user.email != email:
                return Response('А почта-то неверная!',
                                status=status.HTTP_400_BAD_REQUEST)
            code = user.confirmation_code
        send_mail(
            f'confirmation_code пользователя {username}',
            f'Вот вам код: "{code}", для YaMDB',
            'YaMDB@ya.com',
            [email],
            fail_silently=False,
        )
        return Response(
            {
                'username': str(username),
                'email': str(email)
            },
            status=status.HTTP_200_OK)


class RetrieveUpdateUserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = RetrieveUpdateUserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = RetrieveUpdateUserSerializer(
            user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(username=user.username, email=user.email,
                            role=user.role)
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
