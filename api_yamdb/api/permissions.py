from django.contrib.auth import get_user_model
from rest_framework import permissions
from reviews.models import Review, Comment, User


class CustomPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == 'GET' or request.user.is_authenticated or request.user.is_staff


    def has_object_permission(self, request, view, obj):
        if request.method == 'GET' or request.user.role == 'admin':
            return True
        elif request.user.role == 'moderator' and (type(obj) is Comment or type(obj) is Review):
            return True
        elif request.user.role == 'user':
            if request.method == 'POST' and (type(obj) is Comment or type(obj) is Review):
                return True
            if type(obj) is Comment or type(obj) is Review:
                if request.user == obj.author:
                    return True
        return False


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'admin'

class YaMDB_Admin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role == 'admin' or request.user.is_staff is True
