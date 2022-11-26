from django.urls import path, include

from rest_framework import routers

from .views import (
    CreateUserView,
    GetTokenViewSet,
    RetrieveUpdateUserView,
    AdminUserViewSet,
)

router_v1 = routers.DefaultRouter()
router_v1.register(r'auth/token', GetTokenViewSet, basename='GetToken')
router_v1.register(r'users', AdminUserViewSet, basename='AdminUser')

urlpatterns = [
    path('v1/users/me/', RetrieveUpdateUserView.as_view()),
    path('v1/auth/signup/', CreateUserView.as_view()),
    path('v1/', include(router_v1.urls)),
]
