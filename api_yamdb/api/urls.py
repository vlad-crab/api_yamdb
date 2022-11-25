from django.urls import include, path
from rest_framework.routers import DefaultRouter

import api.views as views

router_v1 = DefaultRouter()
router_v1.register("titles", views.TitlesViewSet, basename='Title')
router_v1.register("genres", views.GenreViewSet, basename='Genre')
router_v1.register("categories", views.CategoryViewSet, basename='Category')
router_v1.register(r'auth/signup', views.CreateUserViewSet)
router_v1.register(r'auth/token', views.GetTokenUserApi, basename='GetToken')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet,
    basename='Comment'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet,
    basename='Review'
)


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
