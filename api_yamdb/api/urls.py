import api.views as views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter()
router_v1.register("titles", views.TitlesViewSet, basename='Title')
router_v1.register("genres", views.GenreViewSet, basename='Genre')
router_v1.register("categories", views.CategoryViewSet, basename='Category')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
