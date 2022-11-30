from django.shortcuts import render
import string
import random
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets, permissions, serializers, views
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import YaMDB_Admin
from rest_framework.pagination import PageNumberPagination

from reviews.models import Category, Genre, Title, Review, User, Comment
from .filters import TitleFilter
import api.serializers as serializers
from .permissions import CustomPermission, IsAdminOrReadOnly


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter)
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = TitleFilter

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
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ['name']
    filter_backends = (SearchFilter,)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [SearchFilter,]
    search_fields = ['name']
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = (CustomPermission, )

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(
            author=self.request.user,
            title=title
        )

    def perform_update(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(
            author=self.request.user,
            title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    permission_classes = (CustomPermission, )

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return Comment.objects.filter(review=review)
    
    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(
            author=self.request.user,
            review=review
        )

    def perform_update(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(
            author=self.request.user,
            review=review
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
                'access': str(refresh.access_token)
            },
            status=status.HTTP_200_OK
        )


class CreateUserView(views.APIView):
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
        serializer = serializers.RetrieveUpdateUserSerializer(data=request.data)
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


class RetrieveUpdateUserView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = serializers.RetrieveUpdateUserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = User.objects.get(id=request.user.id)
        if 'role' in request.data:
            request.data.pop('role')
        serializer = serializers.RetrieveUpdateUserSerializer(
            user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.RetrieveUpdateUserSerializer
    permission_classes = (permissions.IsAuthenticated, YaMDB_Admin,)
    filter_backends = (SearchFilter, )
    search_fields = ('username',)
    lookup_field = 'username'