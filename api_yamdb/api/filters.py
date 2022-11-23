import django_filters
from reviews.models import Title


class TitleFilter(filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains'
    )
    category = django_filters.CharFilter(
        field_name='category__slug', lookup_expr='iexact'
    )
    genre = django_filters.CharFilter(
        field_name='genre__slug', lookup_expr='iexact'
    )
    year = django_filters.NumberFilter()

    class Meta:
        model = Title
        fields = ['name', 'category', 'genre', 'year']
