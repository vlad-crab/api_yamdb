from rest_framework import serializers
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from django.db.models import Avg

from reviews.models import Category, Genre, Title, Comment, Review, User


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre
        lookup_field = 'slug'
        read_only_fields = ('id',)


class TitleListSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('name', 'year', 'description', 'genre', 'category', 'rating', 'id')
        model = Title
        read_only_fields = ('id', 'genre', 'category', 'rating')

    def get_rating(self, obj):
        reviews = Review.objects.filter(title=obj)
        rating = reviews.aggregate(Avg('score'))
        return rating.get('score__avg')


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category', 'reviews')
        model = Title



class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(default=serializers.CurrentUserDefault(), read_only=True)
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        model = Review
        read_only_fields = ('pub_date', 'author', 'title')

    def validate(self, data):
        title_id = self.context.get('request').parser_context.get('kwargs').get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if self.context.get('request').method == 'POST':
            if Review.objects.filter(title=title, author=self.context.get('request').user).exists():
                raise serializers.ValidationError(
                    'Нельзя добавить несколько ревью на одно произведение'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(default=serializers.CurrentUserDefault(), read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'review')
        model = Comment
        read_only_fields = ('id', 'pub_date', 'author', 'review')


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


class GetTokenUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
