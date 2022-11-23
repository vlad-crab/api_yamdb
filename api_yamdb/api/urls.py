from django.urls import path, include
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

from rest_framework import routers

from .views import CreateUserViewSet, GetTokenUserApi

router_v1 = routers.DefaultRouter()
router_v1.register(r'auth/signup', CreateUserViewSet)
router_v1.register(r'auth/token', GetTokenUserApi, basename='GetToken')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    # path('v1/auth/token/', TokenObtainPairView.as_view(),
    #      name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(),
    #      name='token_refresh'),
    # path('v1/', include('djoser.urls')),
    # path('v1/', include('djoser.urls.jwt')),
]


# from rest_framework import routers

# router_v1 = routers.DefaultRouter()
# router_v1.register(r'v1/auth/signup/', UserViewSet)
# router_v1.register(r'posts', PostViewSet)
# router_v1.register(r'posts/(?P<post_id>\d+)/comments',
#                    CommentViewSet,
#                    basename='comments')
# router_v1.register(r'follow', FollowViewSet, basename='follow')
