from django.shortcuts import render
import string
import random
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets, permissions, serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Title, Review, User
from api.filters import TitleFilter
import api.serializers as serializers
from .permissions import CustomPermission


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter)
    permission_classes = (CustomPermission, )
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return serializers.TitleCreateSerializer
        return serializers.TitleListSerializer


class CreateListDestroyViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass

class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = (CustomPermission,)
    search_fields = ['name']
    filter_backends = [SearchFilter]
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (CustomPermission,)
    filter_backends = [SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (CustomPermission, )

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (CustomPermission, )

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments



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
    serializer_class = serializers.GetTokenUserSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = serializers.GetTokenUserSerializer(data=request.data)
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
    serializer_class = serializers.UserSerializer
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
