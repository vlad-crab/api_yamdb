import api.serializers as serializers
from api.filters import TitleFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from reviews.models import Category, Genre, Title

from .permissions import CustomIsAdminOrReadOnly
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleCreateSerializer, TitleListSerializer)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter)
    permission_classes = [CustomIsAdminOrReadOnly]
    pagination_class = PageNumberPagination
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
    permission_classes = [CustomIsAdminOrReadOnly]
    pagination_class = PageNumberPagination
    search_fields = ['name']
    filter_backends = [SearchFilter]
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    permission_classes = [CustomIsAdminOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'
